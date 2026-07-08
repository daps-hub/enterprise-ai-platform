import asyncio
import json

from agents.report_agent.logger import logger
from agents.report_agent.openai_client import get_openai_client, get_model_name
from agents.report_agent.prompt import SYSTEM_PROMPT
from agents.report_agent.pdf_generator import generate_pdf


class ReportAgent:
    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()

    async def generate_sections(self, user_request: str, source_data: str) -> dict:
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

Create the report sections as valid JSON.
""",
                },
            ],
            temperature=0,
        )

        sections_text = response.choices[0].message.content
        return json.loads(sections_text)

    def generate_report(self, sections: dict) -> dict:
        return generate_pdf(
            title=sections["title"],
            executive_summary=sections["executive_summary"],
            key_findings=sections["key_findings"],
            recommendations=sections["recommendations"],
        )

    async def process_request(self, user_request: str, source_data: str) -> dict:
        if not user_request.strip():
            logger.warning("Empty report request received.")
            return {
                "success": False,
                "message": "Please enter a report request.",
            }

        logger.info(f"Report request: {user_request}")

        sections = await self.generate_sections(user_request, source_data)
        logger.info("Report sections generated successfully.")

        report = self.generate_report(sections)
        logger.info(f"PDF report generated: {report}")

        return {
            "success": True,
            "title": sections["title"],
            "file_path": report["file_path"],
            "generated_at": report["generated_at"],
        }


async def main():
    agent = ReportAgent()

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
        user_request="Generate an executive sales analytics report.",
        source_data=source_data,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())