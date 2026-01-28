# 🚀 Guia de Uso - Copilot-BI

## ⚡ Quick Start (Recomendado)

### Windows
```bash
# 1. Clone o repositório
git clone seu-repo
cd Copilot-BI

# 2. Coloque os CSVs
mkdir data
# Copie seus arquivos .csv para a pasta data/

# 3. Execute o script de inicialização
start.bat
```

### Linux/Mac
```bash
# 1. Clone o repositório
git clone seu-repo
cd Copilot-BI

# 2. Coloque os CSVs
mkdir data
# Copie seus arquivos .csv para a pasta data/

# 3. Execute o script de inicialização
chmod +x start.sh
./start.sh
```

## 📋 Fluxo Completo

```
┌──────────────────────────────────────────────────────────┐
│                    ARQUIVOS CSV                           │
│  (orders.csv, customers.csv, products.csv, etc)           │
└───────────────────┬──────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │  setup_database.py        │
        │ • Verifica tabelas        │
        │ • Importa CSVs            │
        │ • Aplica índices          │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │  MySQL Database (Olist)   │
        │  8 tabelas com índices    │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │  api.py                   │
        │  • FastAPI Server         │
        │  • LangChain Agent        │
        │  • Chat History           │
        └───────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │  Frontend (React/Vue)     │
        │  • Interface de Chat      │
        │  • Renderização Markdown  │
        └───────────────────────────┘
```

## 🔧 Passo a Passo Manual

Se preferir fazer manualmente:

### 1. Preparar Ambiente
```bash
# Criar venv
python -m venv venv

# Ativar
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Preparar Dados
```bash
# Criar pasta de dados
mkdir data

# Copiar CSVs
# Windows:
copy *.csv data\

# Linux/Mac:
cp *.csv data/
```

### 3. Setup Database
```bash
python setup_database.py
```

### 4. Iniciar API
```bash
python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### 5. Testar
```bash
# No navegador:
http://localhost:8000/docs

# Ou com curl:
curl -X POST http://localhost:8000/api/chat/new

curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quais são as top categorias por GMV?",
    "chat_id": "uuid-aqui"
  }'
```

## 📚 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/chat/new` | Criar novo chat |
| `POST` | `/api/ask` | Fazer pergunta |
| `GET` | `/api/chat/{chat_id}` | Recuperar chat |
| `GET` | `/api/chats` | Listar todos chats |
| `DELETE` | `/api/chat/{chat_id}` | Deletar chat |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

## 🔍 Verificar Status

```bash
# Verificar se API está rodando
curl http://localhost:8000/api/chats

# Ver logs
# Windows: verifique a janela do terminal
# Linux/Mac: veja o output do terminal

# Verificar database
mysql -u agent_bi -p Olist -e "SHOW TABLES; SELECT COUNT(*) FROM orders;"
```

## ⚙️ Configuração

Arquivo `.env`:
```ini
# OpenAI
API_KEY=sk-...

# MySQL
MYSQL_USER=agent_bi
MYSQL_ROOT_PASSWORD=sua_senha
HOST=localhost
MYSQL_PORT=3306
DATABASE=Olist
```

## 🚨 Troubleshooting

### Erro: "No module named 'langchain'"
```bash
pip install langchain langchain_openai langchain-community
```

### Erro: "Access denied for user 'agent_bi'"
```sql
-- Execute como root
GRANT ALL PRIVILEGES ON Olist.* TO 'agent_bi'@'%';
FLUSH PRIVILEGES;
```

### Erro: "Database 'Olist' doesn't exist"
```sql
-- Execute como root
CREATE DATABASE Olist;
```

### Erro: "No CSV files found"
- Verifique se a pasta `data/` existe
- Coloque os CSVs lá (ex: `data/orders.csv`)

## 📊 Exemplo de Interação

```bash
# 1. Criar chat
POST /api/chat/new
Response: {
  "chat_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2026-01-28T10:30:00"
}

# 2. Fazer pergunta
POST /api/ask
{
  "question": "Quais são as top 10 categorias por GMV?",
  "chat_id": "123e4567-e89b-12d3-a456-426614174000"
}

Response: {
  "answer": "## 📊 Top 10 Categorias por GMV\n\n### 🔍 Key Findings\n...",
  "chat_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2026-01-28T10:30:05"
}

# 3. Recuperar histórico
GET /api/chat/123e4567-e89b-12d3-a456-426614174000
Response: {
  "chat_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2026-01-28T10:30:00",
  "messages": [
    {
      "role": "user",
      "content": "Quais são as top 10 categorias por GMV?",
      "timestamp": "2026-01-28T10:30:01"
    },
    {
      "role": "assistant",
      "content": "## 📊 Top 10 Categorias...",
      "timestamp": "2026-01-28T10:30:05"
    }
  ]
}
```

## 🎯 Próximas Integrações

- [ ] Salvar histórico em banco de dados
- [ ] Autenticação de usuários
- [ ] Rate limiting
- [ ] Cache de respostas
- [ ] Export de relatórios
- [ ] Agendamento de análises

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no terminal
2. Consulte SETUP_GUIDE.md
3. Verifique os arquivos de configuração
