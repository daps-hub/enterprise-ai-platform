import os
from typing import Any
import sys
import pandas as pd
from database import get_connection
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("postgres-mcp-server")


# def get_connection():
#     return psycopg2.connect(
#         host=os.getenv("DB_HOST"),
#         database=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         port=os.getenv("DB_PORT", "5432"),
#     )


@mcp.tool()
def list_tables() -> list[str]:
    """List public tables in PostgreSQL."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            return [row[0] for row in cur.fetchall()]


@mcp.tool()
def describe_table(table_name: str) -> list[dict[str, Any]]:
    """Describe columns for a table."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            rows = cur.fetchall()

    return [
        {"column": r[0], "type": r[1], "nullable": r[2]}
        for r in rows
    ]


@mcp.tool()
def run_select_query(sql: str) -> list[dict[str, Any]]:
    """Run SELECT-only SQL safely."""
    clean_sql = sql.strip().lower()

    if not clean_sql.startswith("select"):
        return [{"error": "Only SELECT queries are allowed."}]

    blocked_words = ["insert", "update", "delete", "drop", "alter", "truncate", "create"]

    if any(word in clean_sql for word in blocked_words):
        return [{"error": "Unsafe SQL detected."}]

    with get_connection() as conn:
        df = pd.read_sql(sql, conn)

    return df.head(100).to_dict(orient="records")


@mcp.tool()
def get_sales_summary() -> list[dict[str, Any]]:
    """Get sales summary by region."""
    sql = """
        SELECT region, SUM(revenue) AS total_revenue
        FROM enterprise_transactions
        GROUP BY region
        ORDER BY total_revenue DESC;
    """

    with get_connection() as conn:
        df = pd.read_sql(sql, conn)

    return df.to_dict(orient="records")


@mcp.tool()
def get_customer_transactions(customer_name: str) -> list[dict[str, Any]]:
    """Get transactions for one customer."""
    sql = """
        SELECT *
        FROM enterprise_transactions
        WHERE customer_name ILIKE %s
        ORDER BY transaction_date DESC
        LIMIT 50;
    """

    with get_connection() as conn:
        df = pd.read_sql(sql, conn, params=(f"%{customer_name}%",))

    return df.to_dict(orient="records")



if __name__ == "__main__":
    print("Postgres MCP Server started...", file=sys.stderr)
    mcp.run(transport="stdio")