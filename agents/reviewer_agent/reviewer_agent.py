import asyncio
import json

from agents.reviewer_agent.logger import logger
from agents.reviewer_agent.openai_client import (
    get_openai_client,
    get_model_name,
)
from agents.reviewer_agent.prompt import SYSTEM_PROMPT


class ReviewerAgent:

    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()

    async def review_report(
        self,
        report_text: str,
    ) -> dict:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": report_text,
                },
            ],
            temperature=0,
        )

        return json.loads(
            response.choices[0].message.content
        )

    async def process_request(
        self,
        report_text: str,
    ):

        logger.info("Reviewing report.")

        review = await self.review_report(
            report_text
        )

        logger.info("Review complete.")

        return review


async def main():

    agent = ReviewerAgent()

    report = """
Executive Sales Report

West Region leads revenue.

South Region requires attention.

Recommendations:

Increase marketing spend.
Improve customer retention.
"""

    result = await agent.process_request(
        report
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())