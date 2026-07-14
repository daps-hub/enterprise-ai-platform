import asyncio
import json
from pathlib import Path

from agents.email_agent.logger import logger
from agents.email_agent.openai_client import get_openai_client, get_model_name
from agents.email_agent.mcp_client import EmailMCPClient
from agents.email_agent.prompt import SYSTEM_PROMPT

class EmailAgent:
    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()
        self.mcp = EmailMCPClient()

    
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

    async def send_report_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        attachment_path: str,
    ) -> dict:
        path = Path(attachment_path)

        if not path.exists():
            return {
                "success": False,
                "message": f"Attachment not found: {path}",
            }

        raw_result = await self.mcp.send_email_with_attachment(
            recipient=recipient,
            subject=subject,
            body=body,
            attachment_path=str(path),
        )

        return self.normalize_mcp_result(raw_result)

        return await self.mcp.send_email_with_attachment(
            recipient=recipient,
            subject=subject,
            body=body,
            attachment_path=str(path),
        )







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
            "validate_email": lambda: self.mcp.validate_email(
                arguments["email"]  
            ),

            "send_email": lambda: self.mcp.send_email(
                to=arguments.get("to") or arguments.get("recipient"),
                subject=arguments["subject"],
                body=arguments["body"],
            ),
            "send_email_with_attachment": lambda: self.mcp.send_email_with_attachment(
                recipient=arguments.get("recipient") or arguments.get("to"),
                subject=arguments["subject"],
                body=arguments["body"],
                attachment_path=arguments["attachment_path"],
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
                    "content": "Send email results clearly. Never invent data.",
                },
                {
                    "role": "user",
                    "content": f"""
User question:
{user_question}

Email result:
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
            return "Please enter an email question."
        
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
    agent = EmailAgent()

    question = input("Ask email question: ")

    answer = await agent.process_request(question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())