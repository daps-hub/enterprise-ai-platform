import asyncio
from unittest import result

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

            print("\nTesting send_email...\n")

            # result = await session.call_tool(
            #      "search_opportunities",
            #      {"opportunity_name": "Edge"}
            # )
            
        #     result = await session.call_tool(
        #         "send_email",
        #         {
        #              "to": "dapo40@gmail.com",
        #              "subject": "Enterprise AI Platform Test",
        #              "body": "Congratulations! Your Email MCP Server is working."
        #         },
        #    )
            result = await session.call_tool(
                "send_email_with_attachment",
                {
                    "to": "dapo40@gmail.com",
                    "subject": "Sales Report PDF Test",
                    "body": "Attached is the generated sales report from the Enterprise AI Platform.",
                    "attachment_path": r"C:\enterprise-ai-platform\agents\report_agent\reports\sales_report_20260705_011050.pdf",
                },
            )


            print(result.content)

            
            
asyncio.run(main())