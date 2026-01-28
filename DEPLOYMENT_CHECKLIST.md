# ✅ Checklist de Deployment - Copilot-BI

## 🔍 Pré-Deployment

- [ ] Todos os arquivos CSV estão na pasta `data/`
- [ ] Arquivo `.env` está configurado corretamente
- [ ] MySQL está rodando e acessível
- [ ] Python 3.8+ instalado
- [ ] `requirements.txt` atualizado

## 🛠️ Setup

- [ ] Criar venv: `python -m venv venv`
- [ ] Ativar venv
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Executar setup: `python setup_database.py`
- [ ] Verificar se todas as tabelas foram criadas

## 🧪 Testes

- [ ] API inicia sem erros: `python -m uvicorn app.api:app --reload`
- [ ] Swagger UI acessível: `http://localhost:8000/docs`
- [ ] Criar novo chat: `POST /api/chat/new` (status 200)
- [ ] Fazer pergunta: `POST /api/ask` (status 200)
- [ ] Recuperar chat: `GET /api/chat/{chat_id}` (status 200)
- [ ] Testar resposta com Markdown renderizado no frontend

## 🚀 Deployment

### Local/Dev
- [ ] Script `start.bat` funciona (Windows)
- [ ] Script `start.sh` funciona (Linux/Mac)
- [ ] Logs aparecem no console
- [ ] Resposta da IA leva ~5-10 segundos

### Docker (opcional)
- [ ] Dockerfile criado
- [ ] `docker build -t copilot-bi .`
- [ ] `docker run -p 8000:8000 copilot-bi`
- [ ] API acessível em `http://localhost:8000`

### Production
- [ ] Variáveis de ambiente em secrets
- [ ] CORS configurado para domínios específicos
- [ ] Rate limiting ativado
- [ ] Logging centralizado
- [ ] Backup automático do banco

## 📊 Monitoramento

### Performance
- [ ] Tempo de resposta < 10s
- [ ] CPU usage < 70%
- [ ] Memory usage < 2GB
- [ ] Database queries usando índices

### Logs
- [ ] Erros de conexão capturados
- [ ] Queries SQL lentas identificadas
- [ ] Timestamps corretos em mensagens

## 🔒 Segurança

- [ ] API keys não em commits (usar .env)
- [ ] Senha do MySQL não em logs
- [ ] CORS restrito ao frontend
- [ ] SQL injection prevenido (LangChain tool)
- [ ] Rate limiting por IP

## 📱 Frontend

- [ ] Conexão com backend funciona
- [ ] Chat history persistido
- [ ] Markdown renderizado corretamente
- [ ] Emojis aparecem (se aplicável)
- [ ] Responsive design testado

## 📈 Performance

- [ ] Índices aplicados no MySQL
- [ ] Query cache ativado (MySQL < 8.0)
- [ ] Connection pool configurado
- [ ] LLM resposta em tempo razoável

## ✨ Extras

- [ ] Documentação atualizada (QUICKSTART.md, SETUP_GUIDE.md)
- [ ] Exemplos de uso fornecidos
- [ ] Erros tratados com mensagens claras
- [ ] README.md com overview do projeto

## 🎯 Pós-Deployment

- [ ] Monitorar logs por 24h
- [ ] Coletar feedback de usuários
- [ ] Otimizar queries lentes (se houver)
- [ ] Backups automáticos do database

---

## 🚨 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| "Access denied" | Executar `GRANT ALL PRIVILEGES ON Olist.* TO 'agent_bi'@'%';` |
| "Database not found" | Executar `CREATE DATABASE Olist;` |
| "Module not found" | `pip install -r requirements.txt` |
| "API lenta" | Verificar índices: `python setup_database.py` |
| "CSV não importa" | Verificar encoding e separador do arquivo |

## 📞 Contatos

- Documentação: QUICKSTART.md, SETUP_GUIDE.md
- Código principal: app/
- Setup: setup_database.py
