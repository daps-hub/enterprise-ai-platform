import asyncio
import json

from agents.analytics_agent.logger import logger
from agents.analytics_agent.openai_client import get_openai_client, get_model_name
from agents.analytics_agent.prompt import SYSTEM_PROMPT


class AnalyticsAgent:
    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()

    async def analyze_data(self, user_request: str, source_data: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"""
User request:
{user_request}

Source data:
{source_data}

Analyze the data and return valid JSON.
""",
                },
            ],
            temperature=0,
        )

        result = response.choices[0].message.content
        return json.loads(result)

    async def process_request(self, user_request: str, source_data: str) -> dict:
        if not user_request.strip():
            logger.warning("Empty analytics request received.")
            return {
                "success": False,
                "message": "Please enter an analytics request.",
            }

        logger.info(f"Analytics request: {user_request}")

        analysis = await self.analyze_data(user_request, source_data)

        logger.info("Analysis completed successfully.")

        return {
            "success": True,
            "analysis": analysis,
        }


async def main():
    agent = AnalyticsAgent()

    source_data = """
    Region Revenue:
    West: $47,871,327.22
    Southwest: $45,048,117.60
    Northeast: $43,369,958.37
    APAC: $43,138,579.70
    Midwest: $42,996,513.03
    South: $38,393,995.79
    """

    result = await agent.process_request(
        user_request="Analyze regional sales performance.",
        source_data=source_data,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())