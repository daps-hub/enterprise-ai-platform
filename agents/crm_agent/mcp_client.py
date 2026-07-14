
import asyncio
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys

class SalesforceMCPClient:

    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        salesforce_mcp_dir = project_root / "mcp_servers" / "salesforce-mcp"
        salesforce_python = salesforce_mcp_dir / "venv" / "Scripts" / "python.exe"
        salesforce_server = salesforce_mcp_dir / "server.py"

        self.server_params = StdioServerParameters(
           command=str(salesforce_python),
           args=[str(salesforce_server)],
           cwd=str(salesforce_mcp_dir),
        )

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):

        async with stdio_client(
            self.server_params
        ) as (read, write):

            async with ClientSession(
                read,
                write,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments,
                )

                return result.content

    async def search_accounts(
        self,
        account_name: str,
    ):
        return await self.call_tool(
            "search_accounts",
            {
                "account_name": account_name
            },
        )

    async def get_account(
        self,
        account_id: str,
    ):
        return await self.call_tool(
            "get_account",
            {
                "account_id": account_id
            },
        )

    async def search_contacts(
        self,
        contact_name: str,
    ):
        return await self.call_tool(
            "search_contacts",
            {
                "contact_name": contact_name
            },
        )

    async def search_opportunities(
        self,
        opportunity_name: str,
    ):
        return await self.call_tool(
            "search_opportunities",
            {
                "opportunity_name": opportunity_name
            },
        )

    async def list_open_opportunities(
        self,
    ):
        return await self.call_tool(
            "list_open_opportunities",
            {},
        )