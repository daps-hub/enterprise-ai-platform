import asyncio
import re
from pathlib import Path

import streamlit as st

from agents.planner_agent.planner_agent import PlannerAgent


st.set_page_config(
    page_title="Enterprise AI Platform",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Enterprise AI Platform")
st.write(
    "Multi-agent AI platform with PostgreSQL, Salesforce, "
    "Email, Reports, Reviewer, and Jira."
)

user_question = st.text_area(
    "Ask Enterprise AI",
    placeholder=(
        "Generate today's sales report and email it "
        "to dapo40@gmail.com"
    ),
    height=120,
)


def format_generated_at(generated_at: str) -> str:
    """
    Convert a timestamp such as 20260714_204528 into
    2026-07-14 20:45:28.
    """
    if not generated_at:
        return "Unknown"

    try:
        return (
            f"{generated_at[:4]}-"
            f"{generated_at[4:6]}-"
            f"{generated_at[6:8]} "
            f"{generated_at[9:11]}:"
            f"{generated_at[11:13]}:"
            f"{generated_at[13:15]}"
        )
    except (TypeError, IndexError):
        return str(generated_at)


def render_workflow_status(result: dict) -> None:
    """
    Show only the agents that are relevant to the returned result.
    """
    completed_agents = []

    if "analysis" in result:
        completed_agents.extend(
            [
                "Database Agent",
                "Analytics Agent",
            ]
        )

    if "report" in result:
        completed_agents.extend(
            [
                "Database Agent",
                "Analytics Agent",
                "Report Agent",
            ]
        )

    if "review" in result:
        completed_agents.append("Reviewer Agent")

    if "email" in result:
        completed_agents.append("Email Agent")

    if "jira" in result:
        completed_agents.append("Jira Agent")

    completed_agents = list(dict.fromkeys(completed_agents))

    if not completed_agents:
        return

    st.markdown("### Workflow Status")

    for agent_name in completed_agents:
        st.markdown(f"- [x] {agent_name}")


def render_analysis(analysis_result) -> None:
    st.subheader("📊 Analysis")

    if not isinstance(analysis_result, dict):
        st.write(analysis_result)
        return

    summary = analysis_result.get("summary")
    key_insights = analysis_result.get("key_insights")
    risks = analysis_result.get("risks")
    recommendations = analysis_result.get("recommendations")
    assumptions = analysis_result.get("assumptions")

    if summary:
        st.markdown("#### Summary")
        st.write(summary)

    if key_insights:
        st.markdown("#### Key Insights")
        st.write(key_insights)

    if risks:
        st.markdown("#### Risks")
        st.write(risks)

    if recommendations:
        st.markdown("#### Recommendations")
        st.write(recommendations)

    if assumptions:
        st.markdown("#### Assumptions and Limitations")
        st.write(assumptions)


def render_report(report_result) -> None:
    st.subheader("📄 Report")

    if not isinstance(report_result, dict):
        st.write(report_result)
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Report",
            report_result.get(
                "title",
                "Executive Sales Report",
            ),
        )

    with col2:
        generated_at = report_result.get(
            "generated_at",
            "",
        )

        st.metric(
            "Generated",
            format_generated_at(generated_at),
        )

    if report_result.get("success"):
        st.success("PDF generated successfully.")
    else:
        st.error(
            report_result.get(
                "message",
                "Report generation failed.",
            )
        )

    pdf_path_value = report_result.get("file_path")

    if not pdf_path_value:
        return

    pdf_path = Path(pdf_path_value)

    if not pdf_path.exists():
        st.warning(
            f"Report file was not found at: {pdf_path}"
        )
        return

    with pdf_path.open("rb") as file:
        st.download_button(
            "📥 Download Report",
            data=file,
            file_name=pdf_path.name,
            mime="application/pdf",
        )


def render_review(review_result) -> None:
    st.subheader("🧠 Reviewer")

    if not isinstance(review_result, dict):
        st.write(review_result)
        return

    score = review_result.get(
        "overall_score",
        review_result.get("score"),
    )

    approved = review_result.get("approved")

    if score is not None:
        if score >= 8:
            st.success(f"Review Score: {score}/10")
        elif score >= 6:
            st.warning(f"Review Score: {score}/10")
        else:
            st.error(f"Review Score: {score}/10")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Score",
                score,
            )

        with col2:
            st.metric(
                "Approved",
                str(approved),
            )

    recommendation = review_result.get("recommendation")

    if recommendation:
        st.write(recommendation)

    strengths = review_result.get("strengths")

    if strengths:
        st.markdown("#### Strengths")

        for strength in strengths:
            st.markdown(f"- {strength}")

    issues = review_result.get("issues")

    if issues:
        st.markdown("#### Issues")

        for issue in issues:
            st.markdown(f"- {issue}")


def render_email(email_result) -> None:
    st.subheader("📧 Email")

    if isinstance(email_result, dict):
        if email_result.get("success"):
            st.success(
                email_result.get(
                    "message",
                    "Email sent successfully.",
                )
            )
        else:
            st.error(
                email_result.get(
                    "message",
                    "Email sending failed.",
                )
            )

        st.json(email_result)
        return

    st.write(str(email_result))


def render_jira(jira_result) -> None:
    st.subheader("Jira")

    if isinstance(jira_result, dict):
        if jira_result.get("success"):
            issue_key = jira_result.get("issue_key")

            if issue_key:
                st.success(
                    f"Issue Created: {issue_key}"
                )
            else:
                st.success(
                    jira_result.get(
                        "message",
                        "Jira issue created successfully.",
                    )
                )
        else:
            st.error(
                jira_result.get(
                    "message",
                    "Jira operation failed.",
                )
            )

        st.json(jira_result)
        return

    jira_text = str(jira_result)
    match = re.search(r"KAN-\d+", jira_text)

    if match:
        st.success(
            f"Issue Created: {match.group(0)}"
        )

    st.write(jira_text)


if st.button("Run Workflow"):
    if not user_question.strip():
        st.warning("Please enter a request.")

    else:
        with st.spinner("Running agents..."):
            try:
                planner = PlannerAgent()

                result = asyncio.run(
                    planner.route_request(user_question)
                )

            except Exception as exc:
                st.exception(exc)
                result = None

        if result is None:
            st.error(
                "The workflow did not return a result."
            )

        elif isinstance(result, str):
            # CRM, database, Jira, and other single-agent
            # responses may return plain text.
            st.write(result)

        elif isinstance(result, dict):
            message = result.get("message")
            success = result.get("success")

            if message:
                if success is True:
                    st.success(message)
                elif success is False:
                    st.error(message)
                else:
                    st.info(message)

            render_workflow_status(result)

            if "analysis" in result:
                render_analysis(
                    result["analysis"]
                )

            if "report" in result:
                render_report(
                    result["report"]
                )

            if "review" in result:
                render_review(
                    result["review"]
                )

            if "email" in result:
                render_email(
                    result["email"]
                )

            if "jira" in result:
                render_jira(
                    result["jira"]
                )

        else:
            st.write(result)


st.divider()

st.caption(
    "Enterprise AI Platform v1.0 • Multi-Agent Architecture "
    "• PostgreSQL • Salesforce • Email • Jira"
)