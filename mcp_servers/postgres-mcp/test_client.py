import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print("-", tool.name)

            result = await session.call_tool("list_tables", {})
            print("\nlist_tables result:")
            print(result.content)

            result = await session.call_tool(
                "describe_table",
                {"table_name": "enterprise_transactions"}
            )
            print(result.content)
            result = await session.call_tool("get_sales_summary", {})
            print(result.content)
if __name__ == "__main__":
    asyncio.run(main())