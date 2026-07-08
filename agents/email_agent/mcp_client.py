import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class EmailMCPClient:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        email_mcp_dir = project_root / "mcp_servers" / "email-mcp"
        email_python = email_mcp_dir / "venv" / "Scripts" / "python.exe"
        email_server = email_mcp_dir / "server.py"

        self.server_params = StdioServerParameters(
            command=str(email_python),
            args=[str(email_server)],
            cwd=str(email_mcp_dir),
        )

    async def call_tool(self, tool_name: str, arguments: dict):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content

    async def validate_email(self, email: str):
        return await self.call_tool(
            "validate_email",
            {"email": email},
        )

    async def send_email(self, to: str, subject: str, body: str):
        return await self.call_tool(
            "send_email",
            {
                "to": to,
                "subject": subject,
                "body": body,
            },
        )

    async def send_email_with_attachment(
        self,
        to: str,
        subject: str,
        body: str,
        attachment_path: str,
    ):
        return await self.call_tool(
            "send_email_with_attachment",
            {
                "to": to,
                "subject": subject,
                "body": body,
                "attachment_path": attachment_path,
            },
        )

    async def list_tools(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return result.tools


if __name__ == "__main__":
    client = EmailMCPClient()
    result = asyncio.run(
        client.send_email(
            to="dapo40@gmail.com",
            subject="Test Email",
            body="This is a test email.",
        )
    )
    print(result)