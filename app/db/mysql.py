from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def create_mysql_engine(
    user: str,
    password: str,
    host: str,
    port: int,
    database: str
):
    connection_string = (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    )

    engine = create_engine(
        connection_string,
        poolclass=QueuePool,
        pool_size=5,              # Conexões simultâneas
        max_overflow=10,          # Conexões extras sob demanda
        pool_pre_ping=True,       # Verifica conexão antes de usar
        pool_recycle=3600,        # Recicla conexões a cada hora
        echo=False,               # Desativa log SQL (performance)
        connect_args={
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
        }
    )

    return engine
