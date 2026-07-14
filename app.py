import asyncio
import streamlit as st
import re
from agents.planner_agent.planner_agent import PlannerAgent


st.set_page_config(
    page_title="Enterprise AI Platform",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Enterprise AI Platform")
st.write("Multi-agent AI platform with PostgreSQL, Salesforce, Email, Reports, Reviewer, and Jira.")

user_question = st.text_area(
    "Ask Enterprise AI",
    placeholder="Generate today's sales report and email it to dapo40@gmail.com",
    height=120,
)

if st.button("Run Workflow"):
    if not user_question.strip():
        st.warning("Please enter a request.")
    else:
        with st.spinner("Running agents..."):
            planner = PlannerAgent()
            result = asyncio.run(planner.route_request(user_question))

            if isinstance(result, str):
                st.write(result)

            elif result.get("success"):
                st.success(result.get("message"))

            else:
                st.error(result.get("message"))
                
                
            st.markdown("""
            ### Workflow Status

            - [x] Database Agent
            - [x] Analytics Agent
            - [x] Report Agent
            - [x] Reviewer Agent
            - [x] Email Agent
            - [x] Jira Agent
            """)
            if "report" in result:
                st.subheader("📄 Report")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Report",
                        result["report"]["title"]
                    )

                with col2:
                    
                        generated = result["report"]["generated_at"]

                        formatted = (
                            f"{generated[:4]}-{generated[4:6]}-{generated[6:8]} "
                            f"{generated[9:11]}:{generated[11:13]}:{generated[13:15]}"
                        )

                        st.metric(
                            "Generated",
                            formatted
                        )

                st.write("PDF generated successfully.")
                
                pdf_path = result["report"]["file_path"]

                with open(pdf_path, "rb") as file:
                    st.download_button(
                            "📥 Download Report",
                            data=file,
                            file_name="sales_report.pdf",
                            mime="application/pdf",
                        )
            

        if "review" in result:
            st.subheader("🧠 Reviewer")
            score = result["review"]["overall_score"]

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
                    result["review"]["overall_score"]
                )

            with col2:
                st.metric(
                    "Approved",
                    str(result["review"]["approved"])
                )

            st.write(
                result["review"]["recommendation"]
            )

        if "email" in result:
            
            st.subheader("📧 Email")

            email_result = result["email"]

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

            else:
                st.write(email_result)
        if "jira" in result:
            
            st.subheader("Jira")

            jira_result = result["jira"]

            if isinstance(jira_result, dict):
                if jira_result.get("success"):
                    issue_key = jira_result.get("issue_key")

                    if issue_key:
                        st.success(f"Issue Created: {issue_key}")
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

            else:
                jira_text = str(jira_result)
                match = re.search(r"KAN-\d+", jira_text)

                if match:
                    st.success(f"Issue Created: {match.group(0)}")

                st.write(jira_text)
    
    
     
        
    st.divider()

    st.caption(
        "Enterprise AI Platform v1.0 • Multi-Agent Architecture • PostgreSQL • Salesforce • Email • Jira"
    )