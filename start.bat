@echo off
REM Script de inicialização rápida para Windows

setlocal enabledelayedexpansion

cls
echo.
echo ================================================
echo  COPILOT-BI - Quick Start
echo ================================================
echo.

REM 1. Criar venv se não existir
if not exist "venv\" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo Erro ao criar venv!
        pause
        exit /b 1
    )
)

REM 2. Ativar venv
echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM 3. Instalar dependências
echo 📚 Instalando dependências...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Erro ao instalar dependências!
    pause
    exit /b 1
)

REM 4. Setup database
echo 🗄️  Configurando database...
python setup_database.py
if errorlevel 1 (
    echo Erro no setup do database!
    pause
    exit /b 1
)

REM 5. Iniciar API
echo.
echo 🌐 Iniciando API na porta 8000...
echo 📍 Acesso em: http://localhost:8000/docs
echo.
cd app
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

pause
