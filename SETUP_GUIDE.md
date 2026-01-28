# 🗄️ Setup Automático do Database Olist

## O que o script faz

✅ **Verifica** se as tabelas existem no banco  
✅ **Importa** arquivos CSV automaticamente  
✅ **Cria índices** de performance  
✅ **Exibe relatório** com estatísticas  

## Pré-requisitos

1. **MySQL rodando** com credenciais no `.env`
2. **Arquivos CSV** na pasta `data/`
3. **Python 3.8+** com venv ativado

## Como usar

### Windows

```bash
# 1. Colocar CSVs na pasta 'data'
mkdir data
# Copiar seus arquivos CSV para c:\Dev\Local\Copilot-BI\data\

# 2. Executar o setup
setup_database.bat
```

### Linux/Mac

```bash
# 1. Colocar CSVs na pasta 'data'
mkdir data
# Copiar seus arquivos CSV para ./data/

# 2. Ativar venv
source venv/bin/activate

# 3. Executar o setup
python setup_database.py
```

## Estrutura esperada

```
Copilot-BI/
├── data/
│   ├── orders.csv
│   ├── customers.csv
│   ├── products.csv
│   ├── order_items.csv
│   ├── sellers.csv
│   ├── order_payments.csv
│   ├── order_reviews.csv
│   └── product_category_name_translation.csv
├── setup_database.py
├── setup_database.bat
├── app/
│   ├── api.py
│   └── ...
└── .env
```

## Saída esperada

```
============================================================
🚀 SETUP DATABASE OLIST
============================================================

📌 Configurações:
   Database: Olist
   User: agent_bi
   Host: localhost:3306
   Data Dir: C:\Dev\Local\Copilot-BI\data

🔌 Conectando ao MySQL...
   ✅ Conectado com sucesso!

📂 Arquivos encontrados (8):
   - customers.csv
   - order_items.csv
   - order_payments.csv
   - order_reviews.csv
   - orders.csv
   - product_category_name_translation.csv
   - products.csv
   - sellers.csv

📥 Importando dados...
  📥 Importando orders.csv para tabela 'orders'...
     └─ 99,441 linhas lidas
     ✅ Tabela 'orders' criada com 99,441 linhas
  ...

📋 Tabelas no database:
   - customers: 99,441
   - order_items: 112,650
   - order_payments: 103,886
   - order_reviews: 98,672
   - orders: 99,441
   - product_category_name_translation: 71
   - products: 32,951
   - sellers: 3,095

📊 Aplicando índices de performance...
  ✅ Índices aplicados com sucesso!

📊 Estatísticas finais:
   Total de tabelas: 8
   Database: Olist

============================================================
✅ SETUP CONCLUÍDO!
============================================================

🎯 Próximos passos:
   1. Inicie a API: python api.py
   2. Teste com: POST http://localhost:8000/api/ask
   3. Crie um novo chat: POST http://localhost:8000/api/chat/new
```

## Solução de Problemas

### Erro: "Nenhum arquivo CSV encontrado"
- Verifique se a pasta `data/` existe
- Certifique-se de que os CSVs estão em `Copilot-BI/data/`

### Erro: "Access denied for user 'agent_bi'"
- O script vai tentar conceder permissões automaticamente
- Se falhar, execute como root:
  ```sql
  GRANT ALL PRIVILEGES ON Olist.* TO 'agent_bi'@'%';
  FLUSH PRIVILEGES;
  ```

### Erro: "Table already exists"
- O script pula tabelas que já existem
- Para reimportar, delete a tabela no MySQL primeiro

## Automação Completa

Para integrar ao processo de deployment:

```bash
# .github/workflows/deploy.yml (GitHub Actions)
- name: Setup Database
  run: python setup_database.py
```

Ou no seu CI/CD:

```bash
#!/bin/bash
python setup_database.py || exit 1
python -m uvicorn app.api:app --reload
```
