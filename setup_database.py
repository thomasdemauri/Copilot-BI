#!/usr/bin/env python3
"""
Script de Setup do Database Olist
- Verifica se as tabelas existem
- Importa arquivos CSV
- Aplica índices de performance
"""

import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

# Configurações
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_ROOT_PASSWORD = str(os.getenv("MYSQL_ROOT_PASSWORD"))
HOST = str(os.getenv("HOST"))
PORT = int(os.getenv("MYSQL_PORT", 3306))
DATABASE = os.getenv("DATABASE")

# Diretório de dados
DATA_DIR = Path(__file__).parent / "data"
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).parent.parent / "data"

print(f"🔍 Procurando dados em: {DATA_DIR}")


def create_connection(user="root"):
    """Cria conexão com MySQL."""
    connection_string = (
        f"mysql+pymysql://{user}:{MYSQL_ROOT_PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    )
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )
    return engine


def table_exists(engine, table_name):
    """Verifica se uma tabela existe no banco."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def import_csv(engine, csv_file, table_name):
    """Importa um arquivo CSV para o banco de dados."""
    try:
        print(f"  📥 Importando {csv_file.name} para tabela '{table_name}'...")
        
        # Ler CSV
        df = pd.read_csv(csv_file, encoding='utf-8', on_bad_lines='skip')
        
        # Se falhar, tentar com latin1
        if df.empty:
            df = pd.read_csv(csv_file, encoding='latin1', on_bad_lines='skip')
        
        print(f"     └─ {len(df)} linhas lidas")
        
        # Salvar no banco
        df.to_sql(table_name, con=engine, if_exists='replace', index=False, chunksize=1000)
        print(f"     ✅ Tabela '{table_name}' criada com {len(df)} linhas")
        
        return True
    except Exception as e:
        print(f"     ❌ Erro ao importar {csv_file.name}: {str(e)}")
        return False


def apply_indexes(engine):
    """Aplica índices de performance no banco."""
    indexes = {
        # Orders (usando prefixo para colunas TEXT)
        "idx_orders_timestamp_status": "CREATE INDEX idx_orders_timestamp_status ON olist_orders_dataset(order_purchase_timestamp(20), order_status(20))",
        "idx_orders_customer_id": "CREATE INDEX idx_orders_customer_id ON olist_orders_dataset(customer_id(50))",
        
        # Order Items
        "idx_order_items_product_order": "CREATE INDEX idx_order_items_product_order ON olist_order_items_dataset(product_id(50), order_id(50))",
        "idx_order_items_seller": "CREATE INDEX idx_order_items_seller ON olist_order_items_dataset(seller_id(50))",
        
        # Customers
        "idx_customers_state": "CREATE INDEX idx_customers_state ON olist_customers_dataset(customer_state(5))",
        "idx_customers_unique_id": "CREATE INDEX idx_customers_unique_id ON olist_customers_dataset(customer_unique_id(50))",
        
        # Products
        "idx_products_category": "CREATE INDEX idx_products_category ON olist_products_dataset(product_category_name(100))",
        
        # Payments
        "idx_payments_order_type": "CREATE INDEX idx_payments_order_type ON olist_order_payments_dataset(order_id(50), payment_type(20))",
        
        # Reviews
        "idx_reviews_order_score": "CREATE INDEX idx_reviews_order_score ON olist_order_reviews_dataset(order_id(50), review_score)",
        
        # Sellers
        "idx_sellers_state": "CREATE INDEX idx_sellers_state ON olist_sellers_dataset(seller_state(5))",
    }
    
    print("\n📊 Aplicando índices de performance...")
    try:
        with engine.connect() as conn:
            # Verificar índices existentes
            existing_indexes = set()
            result = conn.execute(text("""
                SELECT DISTINCT INDEX_NAME 
                FROM information_schema.STATISTICS 
                WHERE TABLE_SCHEMA = DATABASE()
            """))
            for row in result:
                existing_indexes.add(row[0])
            
            # Criar apenas índices que não existem
            for idx_name, idx_sql in indexes.items():
                if idx_name in existing_indexes:
                    continue
                    
                try:
                    conn.execute(text(idx_sql))
                    print(f"  ✅ Criado: {idx_name}")
                except Exception as e:
                    if "Duplicate key name" in str(e) or "already exists" in str(e):
                        continue
                    print(f"  ⚠️  Erro em {idx_name}: {str(e)[:80]}")
            
            conn.commit()
        print("  ✅ Índices aplicados com sucesso!")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao aplicar índices: {str(e)}")
        return False


def main():
    """Executa o setup completo."""
    print("\n" + "="*60)
    print("🚀 SETUP DATABASE OLIST")
    print("="*60)
    
    # Verificar credenciais
    print(f"\n📌 Configurações:")
    print(f"   Database: {DATABASE}")
    print(f"   User: {MYSQL_USER}")
    print(f"   Host: {HOST}:{PORT}")
    print(f"   Data Dir: {DATA_DIR}")
    
    if not DATA_DIR.exists():
        print(f"\n❌ Diretório de dados não encontrado: {DATA_DIR}")
        print("   Crie uma pasta 'data' com os arquivos CSV")
        sys.exit(1)
    
    # Conectar ao banco
    print(f"\n🔌 Conectando ao MySQL...")
    try:
        engine = create_connection(user="root")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("   ✅ Conectado com sucesso!")
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {str(e)}")
        sys.exit(1)
    
    # Procurar por CSVs
    csv_files = list(DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        print(f"\n❌ Nenhum arquivo CSV encontrado em {DATA_DIR}")
        print("   Adicione arquivos .csv nesta pasta")
        sys.exit(1)
    
    print(f"\n📂 Arquivos encontrados ({len(csv_files)}):")
    for csv_file in sorted(csv_files):
        print(f"   - {csv_file.name}")
    
    # Importar CSVs
    print(f"\n📥 Importando dados...")
    imported_count = 0
    
    for csv_file in sorted(csv_files):
        table_name = csv_file.stem  # Remove .csv
        
        # Verificar se tabela já existe
        if table_exists(engine, table_name):
            print(f"  ⏭️  Pulando '{table_name}' (já existe)")
            continue
        
        if import_csv(engine, csv_file, table_name):
            imported_count += 1
    
    if imported_count == 0:
        print("  ℹ️  Nenhuma tabela nova foi importada (todas já existem)")
    else:
        print(f"\n✅ {imported_count} tabela(s) importada(s)")
    
    # Listar tabelas
    print(f"\n📋 Tabelas no database:")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    with engine.connect() as conn:
        for table in sorted(tables):
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   - {table}: {row_count:,} linhas")
    
    # Aplicar índices
    apply_indexes(engine)
    
    # Estatísticas finais
    print(f"\n📊 Estatísticas finais:")
    print(f"   Total de tabelas: {len(tables)}")
    print(f"   Database: {DATABASE}")
    
    print("\n" + "="*60)
    print("✅ SETUP CONCLUÍDO!")
    print("="*60)
    print("\n🎯 Próximos passos:")
    print("   1. Inicie a API: python api.py")
    print("   2. Teste com: POST http://localhost:8000/api/ask")
    print("   3. Crie um novo chat: POST http://localhost:8000/api/chat/new")
    print("\n")


if __name__ == "__main__":
    main()
