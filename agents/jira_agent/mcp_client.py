import asyncio
import os
from pathlib import Path
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class JiraMCPClient:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]

        jira_mcp_dir = project_root / "mcp_servers" / "jira-mcp"
        jira_python = sys.executable
        jira_server = jira_mcp_dir / "server.py"

        if os.name == "nt":
            # Local Windows development
            jira_python = (
                jira_mcp_dir
                / "venv"
                / "Scripts"
                / "python.exe"
            )
        else:
            # Docker and AWS Linux container
            jira_python = Path(sys.executable)

        if not jira_python.exists():
            raise FileNotFoundError(
                f"Python executable not found: {jira_python}"
            )

        if not jira_server.exists():
            raise FileNotFoundError(
                f"Jira MCP server not found: {jira_server}"
            )

        self.server_params = StdioServerParameters(
            command=str(jira_python),
            args=[str(jira_server)],
            cwd=str(jira_mcp_dir),
            env=os.environ.copy(),
        )

    async def call_tool(self, tool_name: str, arguments: dict):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content
    
    async def create_issue(self, project: str, summary: str, description: str, issue_type: str):
        return await self.call_tool(
            "create_issue",
            {
                "project": project,
                "summary": summary,
                "description": description,
                "issue_type": issue_type,
            },
        )
    async def search_issues(self, jql: str):
        return await self.call_tool(
            "search_issues",
            {
                "jql": jql,
            },
        )      
        
    async def get_issue(self, issue_key: str):
        return await self.call_tool(
            "get_issue",
            {
                "issue_key": issue_key
            },
        )
        
    async def add_comment(self, issue_key: str, comment: str):
        return await self.call_tool(
            "add_comment",
            {
                "issue_key": issue_key,
                "comment": comment
            },
        )
        
        
    async def transition_issue(self, issue_key: str, transition_name: str):
        return await self.call_tool(
            "transition_issue",
            {
                "issue_key": issue_key,
                "transition_name": transition_name
            },
        )
    

    async def list_tools(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return result.tools


if __name__ == "__main__":
    client = JiraMCPClient()
    result = asyncio.run(
        client.get_issue(
            issue_key="KAN-4"
        )
    )
    print(result)