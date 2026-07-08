import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("Available tools:")

            for tool in tools.tools:
                print("-", tool.name)

            print("\nTesting list_open_opportunities...\n")

            result = await session.call_tool(
                 "search_opportunities",
                 {"opportunity_name": "Edge"}
            )
            print(result.content)
asyncio.run(main())