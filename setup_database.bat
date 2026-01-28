@echo off
REM Script de Setup do Database Olist para Windows

echo.
echo ====================================================================
echo  SETUP DATABASE OLIST
echo ====================================================================
echo.

REM Verificar se está na venv
if not exist venv\ (
    echo Erro: Ambiente virtual nao encontrado!
    echo Execute primeiro: python -m venv venv
    echo Depois: venv\Scripts\activate
    pause
    exit /b 1
)

REM Ativar venv
call venv\Scripts\activate.bat

echo.
echo 📦 Instalando dependencias necessarias...
pip install pandas sqlalchemy pymysql python-dotenv -q

echo.
echo 🔄 Executando setup...
python setup_database.py

if errorlevel 1 (
    echo.
    echo ❌ Erro durante o setup!
    pause
    exit /b 1
)

echo.
echo ✅ Setup concluido com sucesso!
echo.
pause
