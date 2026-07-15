import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class SalesforceMCPClient:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        salesforce_mcp_dir = project_root / "mcp_servers" / "salesforce-mcp"
        salesforce_server = salesforce_mcp_dir / "server.py"

        if os.name == "nt":
            salesforce_python = (
                salesforce_mcp_dir
                / "venv"
                / "Scripts"
                / "python.exe"
            )

            if not salesforce_python.exists():
                salesforce_python = Path(sys.executable)
        else:
            salesforce_python = Path(sys.executable)

        self.server_params = StdioServerParameters(
            command=str(salesforce_python),
            args=[str(salesforce_server)],
            cwd=str(salesforce_mcp_dir),
            env=os.environ.copy(),
        )

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict | None = None,
    ):
        async with stdio_client(
            self.server_params
        ) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                return await session.call_tool(
                    tool_name,
                    arguments or {},
                )

    async def search_accounts(
        self,
        account_name: str,
    ):
        return await self.call_tool(
            "search_accounts",
            {
                "account_name": account_name,
            },
        )

    async def get_account(
        self,
        account_id: str,
    ):
        return await self.call_tool(
            "get_account",
            {
                "account_id": account_id,
            },
        )

    async def search_contacts(
        self,
        contact_name: str,
    ):
        return await self.call_tool(
            "search_contacts",
            {
                "contact_name": contact_name,
            },
        )

    async def search_opportunities(
        self,
        opportunity_name: str,
    ):
        return await self.call_tool(
            "search_opportunities",
            {
                "opportunity_name": opportunity_name,
            },
        )

    async def list_open_opportunities(self):
        return await self.call_tool(
            "list_open_opportunities",
            {},
        )