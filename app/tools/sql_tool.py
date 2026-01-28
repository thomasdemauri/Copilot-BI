from langchain_core.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage
from langchain_community.utilities import SQLDatabase
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
        """Execute OPTIMIZED SQL queries on Olist Brazilian E-Commerce database."""

        raw_engine = context.db
        model = context.llm

        # Configurar sample rows para reduzir overhead
        db = SQLDatabase(raw_engine, sample_rows_in_table_info=2)
        table_info = db.get_table_info()
        
        toolkit = SQLDatabaseToolkit(db=db, llm=model)
        sql_tools = toolkit.get_tools()

        sql_agent = create_agent(model, tools=sql_tools)

        result = sql_agent.invoke({
            "messages": [
                SystemMessage(content=f"""
You are a specialized OLIST E-COMMERCE DATA ANALYST with focus on FAST, OPTIMIZED queries.

{OLIST_SCHEMA}

{OLIST_METRICS}

=== PERFORMANCE OPTIMIZATION (CRITICAL) ===

**Query Speed Rules**:
1. ALWAYS use LIMIT (default 15 for details, 100 for aggregations)
2. Filter by date ranges when possible (e.g., WHERE order_purchase_timestamp >= '2017-01-01')
3. Use indexed columns in WHERE: order_id, customer_unique_id, seller_id, product_id
4. Avoid SELECT * (specify only needed columns)
5. Use EXPLAIN before complex queries (mentally) to check table scans
6. Prefer WHERE over HAVING when possible
7. Use EXISTS instead of IN for subqueries
8. Limit JOINs to necessary tables only

**Optimized Query Patterns**:

✅ GOOD (Fast):
```sql
-- Top categories by GMV (limited, indexed columns)
SELECT 
    t.product_category_name_english,
    COUNT(DISTINCT oi.order_id) as orders,
    ROUND(SUM(oi.price + oi.freight_value), 2) as gmv
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
WHERE oi.order_id IN (
    SELECT order_id FROM orders 
    WHERE order_purchase_timestamp >= '2017-01-01'
    LIMIT 10000
)
GROUP BY t.product_category_name_english
ORDER BY gmv DESC
LIMIT 15;
```

❌ BAD (Slow):
```sql
-- Full table scan, no limits, unnecessary columns
SELECT *
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN products p ON oi.product_id = p.product_id;
```

=== BRAZILIAN MARKET CONTEXT ===

Geographic Priorities:
- SP (São Paulo) = ~40% of orders (most important)
- RJ (Rio de Janeiro), MG (Minas Gerais) = ~10-15% each
- Focus on top 5 states only to reduce data scanned

Payment Methods:
- credit_card, boleto (main two), voucher, debit_card
- Group minor types as "others" to reduce granularity

=== QUERY STRATEGY (Optimized) ===

1. **Revenue/GMV Questions**
   → Use pre-filtered order_ids (by date)
   → Join only necessary tables
   → LIMIT results to top 15
   → Example: Top 10 categories, not all categories

2. **Customer Behavior**
   → Sample customers if analyzing behavior (LIMIT subquery)
   → Use customer_unique_id with WHERE filter
   → Focus on active customers only

3. **Product Performance**
   → ALWAYS join with product_category_name_translation
   → Filter to top categories (WHERE category IN (...))
   → Use LIMIT 15 for detailed results

4. **Delivery Performance**
   → Calculate only for delivered orders (WHERE order_status = 'delivered')
   → Sample if dataset is large (LIMIT in subquery)
   → Focus on recent dates

5. **Geographic Analysis**
   → Filter to top 5-7 states only
   → Use WHERE customer_state IN ('SP','RJ','MG','PR','SC','RS','BA')
   → This reduces scan by ~80%

6. **Time Trends**
   → Use monthly aggregation (DATE_FORMAT('%Y-%m'))
   → Filter to specific date range (last 12 months max)
   → Don't scan full timestamp history

=== EXECUTION RULES ===

1. ALWAYS add LIMIT clause (15 for details, 100 for aggregates)
2. ALWAYS filter by date when order_purchase_timestamp is available
3. ALWAYS use product_category_name_translation for English names
4. Specify columns explicitly (avoid SELECT *)
5. Use WHERE to filter early, before JOINs when possible
6. Calculate GMV as (price + freight_value)
7. Use customer_unique_id for customer counts
8. Order by most relevant metric DESC with LIMIT

{OLIST_QUERY_EXAMPLES}

=== CURRENT DATABASE SCHEMA ===
{table_info}

Remember: OPTIMIZE FOR SPEED. Use LIMIT, date filters, and indexed columns. Return top results only, not everything.
                """
                ),
                HumanMessage(content=query)
            ]
        })

        return {"response": result["messages"][-1].content}

    return do_sql_query