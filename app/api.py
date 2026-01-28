import os
import traceback
import uvicorn
import re
import pandas as pd
from dotenv import load_dotenv
from langchain.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
from agents.sql_agent import build_agent
from graph.graph import build_graph
from graph.state import ContextSchema
from helpers.panda import excel_to_db
from db.mysql import create_mysql_engine
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="AI SQL Agent API", description="API para consulta dinâmica em bancos SQL via LangChain")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_ROOT_PASSWORD = str(os.getenv("MYSQL_ROOT_PASSWORD"))
HOST = str(os.getenv("HOST"))
PORT = int(os.getenv("MYSQL_PORT", 3306))

class QueryRequest(BaseModel):
    question: str
    namespace_name: str

class CreateNamespaceRequest(BaseModel):
    namespace_name: str

class QueryResponse(BaseModel):
    answer: str

def validate_db_name(name: str):
    """Garante que o nome do banco só tenha letras, números e underline."""
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        raise HTTPException(status_code=400, detail="Nome do namespace inválido. Use apenas letras, números e '_'.")
    return name

@app.post("/api/namespaces", status_code=201)
async def create_namespace(request: CreateNamespaceRequest):
    """Cria um novo banco de dados no MySQL para isolar os dados."""
    db_name = validate_db_name(request.namespace_name)
    
    try:
        # Conecta no MySQL sem especificar banco (ou no 'mysql' padrão) para poder criar um novo
        # Nota: Estou assumindo que sua função create_mysql_engine aceita database=None ou string vazia
        # Se não aceitar, você pode criar uma engine direta do SQLAlchemy aqui.
        engine_root = create_mysql_engine(
            user="root", password=MYSQL_ROOT_PASSWORD, host=HOST, port=PORT, database=""
        )
        
        with engine_root.connect() as conn:
            # Commit automático é necessário para DDL (Create Database) em algumas versões
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            
        return {"message": f"Namespace '{db_name}' criado com sucesso (ou já existia)."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar namespace: {str(e)}")

@app.get("/api/namespaces")
async def list_namespaces():
    """Lista todos os bancos de dados (namespaces) com suas tabelas."""
    try:
        engine_root = create_mysql_engine(
            user="root", password=MYSQL_ROOT_PASSWORD, host=HOST, port=PORT, database="mysql"
        )
        
        with engine_root.connect() as conn:
            result = conn.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result]
            
            # Filtra bancos de sistema do MySQL
            system_dbs = {'information_schema', 'mysql', 'performance_schema', 'sys'}
            user_databases = [db for db in databases if db not in system_dbs]
        
        # Para cada banco, lista suas tabelas
        namespaces_with_tables = []
        for db_name in user_databases:
            try:
                engine_db = create_mysql_engine(
                    user="root", password=MYSQL_ROOT_PASSWORD, host=HOST, port=PORT, database=db_name
                )
                
                with engine_db.connect() as conn:
                    tables_result = conn.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in tables_result]
                
                namespaces_with_tables.append({
                    "name": db_name,
                    "tables": tables
                })
            except Exception as e:
                # Se não conseguir conectar ao banco, ainda assim o inclui com lista vazia
                namespaces_with_tables.append({
                    "name": db_name,
                    "tables": [],
                    "error": str(e)
                })
        
        return {"namespaces": namespaces_with_tables}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar namespaces: {str(e)}")

@app.post("/api/upload")
async def upload_files(
    namespace_name: str = Form(...), 
    files: List[UploadFile] = File(...)
):
    """
    Recebe o nome do namespace e uma lista de arquivos.
    Lê cada arquivo e salva como uma tabela no banco de dados correspondente.
    """
    db_name = validate_db_name(namespace_name)
    
    try:
        engine = create_mysql_engine(
            user="root", password=MYSQL_ROOT_PASSWORD, host=HOST, port=PORT, database=db_name
        )
        
        uploaded_tables = []
        print(f"Recebido {len(files)} arquivos para o namespace '{db_name}'.")
        for file in files:
            filename = file.filename.lower()
            table_name = os.path.splitext(filename)[0].replace(" ", "_").replace("-", "_")
            if filename.endswith(".csv"):
                try:
                    df = pd.read_csv(file.file,sep=None,encoding="utf-8",engine="python",on_bad_lines="skip")
                except:
                    file.file.seek(0)
                    df = pd.read_csv(file.file,sep=None,encoding="latin1",engine="python",on_bad_lines="skip")
            elif filename.endswith(".xlsx") or filename.endswith(".xls"):
                df = pd.read_excel(file.file)
            else:
                continue

            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            uploaded_tables.append(table_name)

        if not uploaded_tables:
            return {"message": "Nenhum arquivo válido processado.", "tables": []}

        return {
            "message": "Arquivos processados com sucesso.",
            "namespace": db_name,
            "created_tables": uploaded_tables
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/ask", response_model=QueryResponse)
async def ask_database(request: QueryRequest):
    """Consulta os dados usando LangChain e seu Agente."""
    try:
        db_name = validate_db_name(request.namespace_name)
        
        engine = create_mysql_engine(
            user="root", password=MYSQL_ROOT_PASSWORD, host=HOST, port=PORT, database=db_name
        )
        context = ContextSchema(llm=None, db=engine)
        
        # Reconstrói o agente para este contexto específico
        agent, tools, model = build_agent(API_KEY, context=context)
        app_graph = build_graph(agent, tools, model)

        result = app_graph.invoke({
            "messages": [HumanMessage(content=request.question)]
        }, context=context)

        print("=== DEBUG: Result completo ===")
        print(result)
        print("\n=== DEBUG: Messages ===")
        print(result.get("messages", []))
        print("\n=== DEBUG: Última mensagem ===")
        if result.get("messages"):
            last_msg = result["messages"][-1]
            print(f"Tipo: {type(last_msg)}")
            print(f"Content: {last_msg.content}")
        
        final_content = result["messages"][-1].content if result.get("messages") else ""

        return QueryResponse(answer=final_content)

    except Exception as e:
        print(f"Erro detalhado: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar a pergunta da AI: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)