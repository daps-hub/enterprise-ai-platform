import asyncio
from pathlib import Path
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class PostgresMCPClient:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        postgres_mcp_dir = project_root / "mcp_servers" / "postgres-mcp"
        
        postgres_server = postgres_mcp_dir / "server.py"
        if os.name == "nt":
            postgres_python = (
                postgres_mcp_dir
                / "venv"
                / "Scripts"
                / "python.exe"
            )

            if not postgres_python.exists():
                postgres_python = Path(sys.executable)
        else:
            postgres_python = Path(sys.executable)
        self.server_params = StdioServerParameters(
            command=str(postgres_python),
            args=[str(postgres_server)],
            cwd=str(postgres_mcp_dir),
            env=os.environ.copy(),
        )

    async def get_sales_summary(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(
                    "get_sales_summary",
                    {}
                )

                return result.content
    async def list_tables(self):
      async with stdio_client(self.server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("list_tables", {})
            return result.content
     
        
    async def describe_table(self, table_name: str):
      async with stdio_client(self.server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "describe_table",
                {"table_name": table_name}
            )
            return result.content
    
    async def run_select_query(self, sql: str):
      async with stdio_client(self.server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "run_select_query",
                {"sql": sql}
            )
            return result.content
    async def get_customer_transactions(self, customer_name: str):
      async with stdio_client(self.server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_customer_transactions",
                {"customer_name": customer_name}
            )
            return result.content

if __name__ == "__main__":
    client = PostgresMCPClient()
    result = asyncio.run(
        client.run_select_query(
            "SELECT region, SUM(revenue) AS total_revenue FROM enterprise_transactions GROUP BY region LIMIT 5"
        )
    )
    print(result)