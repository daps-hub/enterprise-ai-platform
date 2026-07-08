import asyncio
from pathlib import Path
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    current_dir = Path(__file__).parent

    python_path = current_dir / "venv" / "Scripts" / "python.exe"
    server_path = current_dir / "server.py"

    server = StdioServerParameters(
        command=str(python_path),
        args=[str(server_path)],
        cwd=str(current_dir),
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("Available tools:")

            for tool in tools.tools:
                print("-", tool.name)

            print("\nTesting transition_issue...\n")

            result = await session.call_tool(
                "transition_issue",
                {
                    "issue_key": "KAN-4",
                    "transition_name": "In Progress",
                },
            )

            print(result.content)


if __name__ == "__main__":
    asyncio.run(main())
    
# print("JIRA_URL:", os.getenv("JIRA_URL"))
# print("JIRA_EMAIL:", os.getenv("JIRA_EMAIL"))
# print("JIRA_API_TOKEN:", "***" if os.getenv("JIRA_API_TOKEN") else None)