import asyncio
import json


from agents.jira_agent.logger import logger
from agents.jira_agent.openai_client import get_openai_client, get_model_name
from agents.jira_agent.mcp_client import JiraMCPClient
from agents.jira_agent.prompt import SYSTEM_PROMPT

class JiraAgent:
    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()
        self.mcp = JiraMCPClient()
    def normalize_mcp_result(self, result) -> dict:
        if isinstance(result, dict):
            return result

        if isinstance(result, list) and result:
            first_item = result[0]

            if hasattr(first_item, "text"):
                try:
                    return json.loads(first_item.text)
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "message": first_item.text,
                    }

        return {
            "success": False,
            "message": str(result),
        }

    async def create_report_review_issue(self) -> dict:
        raw_result = await self.mcp.create_issue(
            project="KAN",
            summary="Review Executive Sales Report",
            description="Review the latest executive sales report.",
            issue_type="Task",
        )

        return self.normalize_mcp_result(raw_result)
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
            "create_issue": lambda: self.mcp.create_issue(**arguments),           
            "search_issues": lambda: self.mcp.search_issues(**arguments),
            "get_issue": lambda: self.mcp.get_issue(**arguments),
            "add_comment": lambda: self.mcp.add_comment(**arguments),
            "transition_issue": lambda: self.mcp.transition_issue(**arguments),
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
                    "content": "Create and manage issues.",
                },
                {
                    "role": "user",
                    "content": f"""
User question:
{user_question}

Issue result:
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
            return "Please enter a question about creating or managing issues."
        
        logger.info(f"User Question: {user_question}")

        decision = await self.choose_tool(user_question)
        print("Tool decision:", decision)
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
    agent = JiraAgent()

    question = input("Ask about creating or managing issues: ")

    answer = await agent.process_request(question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())