import asyncio
import json
from json import tool
# from logger import logger
# from openai_client import get_openai_client, get_model_name
# from mcp_client import PostgresMCPClient
# from prompt import SYSTEM_PROMPT
from agents.database_agent.logger import logger
from agents.database_agent.openai_client import get_openai_client, get_model_name
from agents.database_agent.mcp_client import PostgresMCPClient
from agents.database_agent.prompt import SYSTEM_PROMPT

class DatabaseAgent:
    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()
        self.mcp = PostgresMCPClient()

    async def choose_tool(self, user_question: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_question},
            ],
            temperature=0,
        )

        tool_decision = response.choices[0].message.content
        return json.loads(tool_decision)
    
    
    async def execute_tool(self, decision: dict):
        tool = decision["tool"]
        arguments = decision.get("arguments", {})

        tool_map = {
            "list_tables": lambda: self.mcp.list_tables(),
            "describe_table": lambda: self.mcp.describe_table(
                arguments["table_name"]
            ),
            "get_sales_summary": lambda: self.mcp.get_sales_summary(),
            "run_select_query": lambda: self.mcp.run_select_query(
                arguments["sql"]
            ),
        }

        if tool not in tool_map:
            raise ValueError(f"Unknown tool: {tool}")

        return await tool_map[tool]()
    
    async def explain_result(self, user_question: str, tool_result):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Explain database results clearly. Never invent data.",
                },
                {
                    "role": "user",
                    "content": f"""
User question:
{user_question}

Database result:
{tool_result}

Explain the result in plain English.
""",
                },
            ],
            temperature=0,
        )

        return response.choices[0].message.content

    async def process_request(self, user_question: str):
        if not user_question.strip():
            logger.warning("Empty user question received.")
            return "Please enter a database question."
        
        logger.info(f"User Question: {user_question}")

        decision = await self.choose_tool(user_question)
        logger.info(f"Tool Selected: {decision}")

        tool_result = await self.execute_tool(decision)
        logger.info("Tool executed successfully.")
        final_answer = await self.explain_result(
            user_question,
            tool_result,
        )
        logger.info("Answer returned to user.")
        return final_answer
async def main():
    agent = DatabaseAgent()

    question = input("Ask database question: ")

    answer = await agent.process_request(question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())