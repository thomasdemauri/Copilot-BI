import os
import traceback
import uvicorn
from dotenv import load_dotenv
from langchain.messages import HumanMessage
from agents.sql_agent import build_agent
from graph.graph import build_graph
from graph.state import ContextSchema
from db.mysql import create_mysql_engine
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from datetime import datetime
from sqlalchemy import text

load_dotenv()

app = FastAPI(title="AI SQL Agent API - Olist", description="API para análise de dados Olist via IA")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
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
DATABASE = os.getenv("DATABASE")

# Armazenar histórico de chats em memória (em produção, usar DB)
chat_history = {}

def setup_database_permissions():
    """Configura permissões do banco de dados na inicialização."""
    try:
        print(f"🔧 Verificando permissões do usuário '{MYSQL_USER}' no database '{DATABASE}'...")
        
        # Tentar conectar com o usuário normal primeiro
        try:
            engine = create_mysql_engine(
                user=MYSQL_USER,
                password=MYSQL_ROOT_PASSWORD,
                host=HOST,
                port=PORT,
                database=DATABASE
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ Usuário '{MYSQL_USER}' tem acesso ao database '{DATABASE}'")
            return
        except Exception as e:
            if "Access denied" not in str(e):
                raise
            print(f"⚠️  Usuário '{MYSQL_USER}' sem acesso. Tentando configurar permissões...")
        
        # Se não tiver acesso, tentar conceder permissões com root
        try:
            engine_root = create_mysql_engine(
                user="root",
                password=MYSQL_ROOT_PASSWORD,
                host=HOST,
                port=PORT,
                database="mysql"
            )
            
            with engine_root.connect() as conn:
                # Conceder permissões
                conn.execute(text(f"GRANT ALL PRIVILEGES ON `{DATABASE}`.* TO '{MYSQL_USER}'@'%'"))
                conn.execute(text("FLUSH PRIVILEGES"))
                conn.commit()
            
            print(f"✅ Permissões concedidas para '{MYSQL_USER}' no database '{DATABASE}'")
            
            # Verificar se funcionou
            engine = create_mysql_engine(
                user=MYSQL_USER,
                password=MYSQL_ROOT_PASSWORD,
                host=HOST,
                port=PORT,
                database=DATABASE
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ Acesso confirmado!")
            
        except Exception as root_error:
            print(f"❌ Erro ao configurar permissões com root:")
            print(f"   {str(root_error)}")
            print(f"\n⚠️  Execute manualmente como root:")
            print(f"   GRANT ALL PRIVILEGES ON `{DATABASE}`.* TO '{MYSQL_USER}'@'%';")
            print(f"   FLUSH PRIVILEGES;")
            raise
    
    except Exception as e:
        print(f"❌ Erro ao configurar database: {str(e)}")
        raise

# Executar setup na inicialização
@app.on_event("startup")
async def startup_event():
    """Executado quando a API inicia."""
    try:
        setup_database_permissions()
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível verificar permissões automaticamente")
        print(f"   A API ainda pode funcionar se as permissões estão corretas")

class QueryRequest(BaseModel):
    question: str
    chat_id: str | None = None

class QueryResponse(BaseModel):
    answer: str
    chat_id: str
    timestamp: str

class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str
    timestamp: str

class ChatResponse(BaseModel):
    chat_id: str
    created_at: str
    messages: list[ChatMessage]

def get_or_create_chat(chat_id: str | None = None) -> str:
    """Retorna chat_id existente ou cria um novo."""
    if chat_id and chat_id in chat_history:
        return chat_id
    
    new_chat_id = str(uuid4())
    chat_history[new_chat_id] = {
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    return new_chat_id

@app.post("/api/chat/new")
async def create_new_chat():
    """Cria um novo chat."""
    chat_id = get_or_create_chat()
    return {
        "chat_id": chat_id,
        "created_at": chat_history[chat_id]["created_at"]
    }

@app.get("/api/chat/{chat_id}")
async def get_chat(chat_id: str):
    """Recupera um chat específico com seu histórico."""
    if chat_id not in chat_history:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    
    chat = chat_history[chat_id]
    messages = [
        ChatMessage(role=msg["role"], content=msg["content"], timestamp=msg["timestamp"])
        for msg in chat["messages"]
    ]
    
    return ChatResponse(
        chat_id=chat_id,
        created_at=chat["created_at"],
        messages=messages
    )

@app.get("/api/chats")
async def list_chats():
    """Lista todos os chats."""
    chats = []
    for chat_id, chat in chat_history.items():
        chats.append({
            "chat_id": chat_id,
            "created_at": chat["created_at"],
            "message_count": len(chat["messages"]),
            "last_message": chat["messages"][-1]["content"] if chat["messages"] else None
        })
    return {"chats": chats}

@app.delete("/api/chat/{chat_id}")
async def delete_chat(chat_id: str):
    """Deleta um chat."""
    if chat_id not in chat_history:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    
    del chat_history[chat_id]
    return {"message": "Chat deletado com sucesso"}

@app.post("/api/ask", response_model=QueryResponse)
async def ask_database(request: QueryRequest):
    """Consulta o dataset com suporte a múltiplos chats."""
    try:
        # Obter ou criar chat
        chat_id = get_or_create_chat(request.chat_id)
        
        # Conectar ao database
        try:
            engine = create_mysql_engine(
                user=MYSQL_USER,
                password=MYSQL_ROOT_PASSWORD,
                host=HOST,
                port=PORT,
                database=DATABASE
            )
        except Exception as db_error:
            if "Access denied" in str(db_error):
                raise HTTPException(
                    status_code=403,
                    detail=f"Erro de acesso ao database. Verifique se o usuário '{MYSQL_USER}' tem permissões no database '{DATABASE}'. Consulte setup_permissions.sql para corrigir."
                )
            elif "Unknown database" in str(db_error):
                raise HTTPException(
                    status_code=404,
                    detail=f"Database '{DATABASE}' não encontrado. Verifique a configuração no .env"
                )
            raise
        
        context = ContextSchema(llm=None, db=engine)
        
        # Reconstrói o agente para este contexto específico
        agent, tools, model = build_agent(API_KEY, context=context)
        app_graph = build_graph(agent, tools, model)

        # Construir histórico de mensagens
        messages = []
        for msg in chat_history[chat_id]["messages"]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                from langchain.messages import AIMessage
                messages.append(AIMessage(content=msg["content"]))
        
        # Adicionar pergunta atual
        messages.append(HumanMessage(content=request.question))

        result = app_graph.invoke({
            "messages": messages
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

        # Salvar no histórico
        timestamp = datetime.now().isoformat()
        chat_history[chat_id]["messages"].append({
            "role": "user",
            "content": request.question,
            "timestamp": timestamp
        })
        chat_history[chat_id]["messages"].append({
            "role": "assistant",
            "content": final_content,
            "timestamp": timestamp
        })

        return QueryResponse(
            answer=final_content,
            chat_id=chat_id,
            timestamp=timestamp
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro detalhado: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar a pergunta da IA: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
