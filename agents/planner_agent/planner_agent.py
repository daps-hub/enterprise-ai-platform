import asyncio
import json


from agents.planner_agent.logger import logger
from agents.planner_agent.openai_client import get_openai_client, get_model_name
from agents.planner_agent.prompt import SYSTEM_PROMPT
from agents.email_agent.email_agent import EmailAgent
from agents.database_agent.database_agent import DatabaseAgent
from agents.crm_agent.crm_agent import CRMAgent
from agents.report_agent.report_agent import ReportAgent
from agents.jira_agent.jira_agent import JiraAgent
from agents.analytics_agent.analytics_agent import AnalyticsAgent
from agents.reviewer_agent.reviewer_agent import ReviewerAgent
class PlannerAgent:
    def __init__(self):
        self.client = get_openai_client()
        self.analytics_agent = AnalyticsAgent()
        self.model = get_model_name()
        self.jira_agent = JiraAgent()
        self.database_agent = DatabaseAgent()
        self.crm_agent = CRMAgent()
        self.email_agent = EmailAgent()
        self.report_agent = ReportAgent()
        self.reviewer_agent = ReviewerAgent()
    async def choose_agent(self, user_question: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_question},
            ],
            temperature=0,
        )

        decision_text = response.choices[0].message.content
        return json.loads(decision_text)

    async def route_request(self, user_question: str):
        if not user_question.strip():
            return "Please enter a question."

        logger.info(f"User Question: {user_question}")

        # Special workflow: generate report and email it
        if "report" in user_question.lower() and "email" in user_question.lower():
            return await self.generate_report_and_email(user_question)

        decision = await self.choose_agent(user_question)
        print("Planner decision:", decision)
        logger.info(f"Agent Selected: {decision}")
        if "workflow" in decision:
            workflow_agents = [
                step["agent"] for step in decision["workflow"]
            ]

            if "database_agent" in workflow_agents and "report_agent" in workflow_agents:
                sales_summary = await self.database_agent.process_request(
                    "Show me the sales summary"
                )

                analysis_result = await self.analytics_agent.process_request(
                    "Analyze the sales summary.",
                    sales_summary,
                )

                return await self.report_agent.process_request(
                    user_question,
                    analysis_result["analysis"],
                )
        
        if "workflow" in decision:
            step = decision["workflow"][0]
            agent = step["agent"]
            task = step["task"]

            if agent == "jira_agent":
                return await self.jira_agent.process_request(task)

            if agent == "database_agent":
                return await self.database_agent.process_request(task)

            if agent == "crm_agent":
                return await self.crm_agent.process_request(task)

            if agent == "email_agent":
                return await self.email_agent.process_request(task)

            if agent == "report_agent":
                summary = await self.database_agent.process_request(
                    "Show me the sales summary"
                )
                return await self.report_agent.process_request(task, summary)

        agent = decision["agent"]
        if "report" in user_question.lower() and "email" in user_question.lower():
            return await self.generate_report_and_email(user_question)
        if agent == "database_agent":
            return await self.database_agent.process_request(user_question)
        if agent == "jira_agent":
            return await self.jira_agent.process_request(user_question)
        
        if agent == "report_agent":
            summary = await self.database_agent.process_request(
                "Show me the sales summary"
            )

            return await self.report_agent.process_request(
                user_question,
                summary,
            )
        if agent == "crm_agent":
            return await self.crm_agent.process_request(user_question)
        if agent == "email_agent":
            return await self.email_agent.process_request(user_question)
        raise ValueError(f"Unknown agent: {agent}")

    async def generate_report_and_email(
        self,
        user_question: str,
    ) -> dict:

        # Database
        sales_summary = await self.database_agent.process_request(
            "Show me the sales summary"
        )

        # Analytics
        analysis_result = await self.analytics_agent.process_request(
            "Analyze the sales summary.",
            sales_summary,
        )

        # Report
        report_result = await self.report_agent.process_request(
            "Generate an executive sales report",
            analysis_result["analysis"],
        )

        # Review
        review = await self.reviewer_agent.process_request(
            json.dumps(
                analysis_result["analysis"],
                indent=2,
            )
        )

        if not review["approved"]:
            return {
                "success": False,
                "message": "Reviewer rejected report.",
                "review": review,
            }

        # Email
        email_result = await self.email_agent.process_request(
            f"""
    Send an email to dapo40@gmail.com
    with subject Executive Sales Report
    and body Attached is today's executive sales report
    and attachment_path {report_result['file_path']}
    """
        )

        # Jira
        jira_result = await self.jira_agent.process_request(
            "Create a Jira task called Review Executive Sales Report"
        )

        return {
            "success": True,
            "report": report_result,
            "review": review,
            "email": email_result,
            "jira": jira_result,
        }

async def main():
    planner = PlannerAgent()

    question = input("Ask Enterprise AI: ")

    answer = await planner.route_request(question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())