import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from jira import JIRA
from mcp.server.fastmcp import FastMCP

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

mcp = FastMCP("jira-mcp")
def get_jira_client():
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")

    if not jira_url:
        raise ValueError("JIRA_URL environment variable is missing")

    if not jira_email:
        raise ValueError("JIRA_EMAIL is missing from .env")

    if not jira_token:
        raise ValueError("JIRA_API_TOKEN is missing from .env")

    return JIRA(
        server=jira_url,
        basic_auth=(jira_email, jira_token),
    )


@mcp.tool()
def create_issue(
    project: str,
    summary: str,
    description: str,
    issue_type: str,
):
    """
    Create a Jira issue.
    """

    try:
        jira = get_jira_client()

        issue = jira.create_issue(
            fields={
                "project": {
                    "key": project,
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": issue_type,
                },
            }
        )

        return {
            "success": True,
            "issue_key": issue.key,
            "message": "Issue created successfully.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }

@mcp.tool()
def search_issues(jql: str):
    """
    Search Jira issues using JQL.
    """

    try:
        jira = get_jira_client()

        issues = jira.search_issues(jql)

        results = []

        for issue in issues:
            results.append(
                {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "issue_type": issue.fields.issuetype.name,
                }
            )

        return {
            "success": True,
            "count": len(results),
            "issues": results,
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }

@mcp.tool()
def get_issue(issue_key: str):
    """
    Get details for a Jira issue.
    """

    try:
        jira = get_jira_client()

        issue = jira.issue(issue_key)

        return {
            "success": True,
            "issue": {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": (
                    issue.fields.description
                    if issue.fields.description
                    else ""
                ),
                "status": issue.fields.status.name,
                "issue_type": issue.fields.issuetype.name,
                "reporter": issue.fields.reporter.displayName,
                "assignee": (
                    issue.fields.assignee.displayName
                    if issue.fields.assignee
                    else None
                ),
            },
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }
        
@mcp.tool()
def add_comment(issue_key: str, comment: str):
    """
    Add a comment to a Jira issue.
    """

    try:
        jira = get_jira_client()

        jira.add_comment(issue_key, comment)

        return {
            "success": True,
            "message": f"Comment added to {issue_key}.",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
        }
        
@mcp.tool()
def transition_issue(
    issue_key: str,
    transition_name: str,
):
    """
    Transition a Jira issue.
    """

    try:
        jira = get_jira_client()

        transitions = jira.transitions(issue_key)

        transition_id = None

        for transition in transitions:

            if (
                transition["name"].lower()
                == transition_name.lower()
            ):
                transition_id = transition["id"]
                break

        if not transition_id:
            return {
                "success": False,
                "message": f"Transition '{transition_name}' not found.",
            }

        jira.transition_issue(
            issue_key,
            transition_id,
        )

        return {
            "success": True,
            "message": f"{issue_key} moved to {transition_name}.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        logger.info("Jira MCP server starting")
if __name__ == "__main__":
    mcp.run(transport="stdio")