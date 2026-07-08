import asyncio
import json

from agents.crm_agent.logger import logger
from agents.crm_agent.openai_client import get_openai_client, get_model_name
from agents.crm_agent.mcp_client import SalesforceMCPClient
from agents.crm_agent.prompt import SYSTEM_PROMPT
class CRMAgent:
    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()
        self.mcp = SalesforceMCPClient()

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
            "search_accounts": lambda: self.mcp.search_accounts(
                arguments["account_name"]
            ),
            "get_account": lambda: self.mcp.get_account(
                arguments["account_id"]
            ),
            "search_contacts": lambda: self.mcp.search_contacts(
                arguments["contact_name"]
            ),
            "search_opportunities": lambda: self.mcp.search_opportunities(
                arguments["opportunity_name"]
            ),
            "list_open_opportunities": lambda: self.mcp.list_open_opportunities(),
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
                    "content": "Explain Salesforce CRM results clearly. Never invent data.",
                },
                {
                    "role": "user",
                    "content": f"""
User question:
{user_question}

Salesforce CRM result:
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
            return "Please enter a CRM question."

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
    agent = CRMAgent()

    question = input("Ask CRM question: ")

    answer = await agent.process_request(question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())