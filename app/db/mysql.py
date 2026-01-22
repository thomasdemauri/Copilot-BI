from sqlalchemy import create_engine

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
        pool_pre_ping=True,
        pool_recycle=3600
    )

    return engine
