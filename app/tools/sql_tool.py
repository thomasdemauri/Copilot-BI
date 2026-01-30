from langchain_core.tools import tool
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from domain.olist_ecommerce import (
    OLIST_SCHEMA, 
    OLIST_METRICS, 
    OLIST_ANALYTICAL_PATTERNS,
    OLIST_QUERY_EXAMPLES
)

def build_sql_tool(context):
    """Factory to create Olist-specialized SQL tool with context injected."""
    
    @tool
    def do_sql_query(query: str):
        """Execute an optimized SQL query on Olist Brazilian E-Commerce database."""

        raw_engine = context.db
        sql = (query or "").strip().rstrip(";")

        if not sql:
            return {"response": "SQL vazio. Envie uma consulta SELECT."}

        sql_lower = sql.lstrip().lower()
        if not (sql_lower.startswith("select") or sql_lower.startswith("with")):
            return {"response": "Somente consultas SELECT são permitidas."}

        if "limit" not in sql_lower:
            sql = f"{sql} LIMIT 100"

        try:
            with raw_engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.mappings().all()

            return {"response": rows}
        except SQLAlchemyError as e:
            return {"response": f"Erro SQL: {str(e)}"}

    return do_sql_query