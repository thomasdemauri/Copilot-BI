#!/bin/bash
# Script de inicialização rápida para Linux/Mac

set -e

echo "================================================"
echo "🚀 COPILOT-BI - Quick Start"
echo "================================================"

# 1. Criar venv se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# 2. Ativar venv
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# 3. Instalar dependências
echo "📚 Instalando dependências..."
pip install -q -r requirements.txt

# 4. Setup database
echo "🗄️  Configurando database..."
python setup_database.py

# 5. Iniciar API
echo ""
echo "🌐 Iniciando API na porta 8000..."
echo "📍 Acesso em: http://localhost:8000/docs"
echo ""
cd app
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
