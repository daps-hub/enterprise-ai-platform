import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("email-mcp")

@mcp.tool()
def send_email_with_attachment(
    to: str,
    subject: str,
    body: str,
    attachment_path: str,
):
    """
    Send an email with an attachment.
    """

    validation = validate_email(to)

    if not validation["valid"]:
        return {
            "success": False,
            "message": validation["message"],
        }

    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))

    message = MIMEMultipart()

    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    try:
        
        if not os.path.exists(attachment_path):
            return {
                "success": False,
                "message": f"Attachment not found: {attachment_path}",
            }
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(attachment_path)}",
        )

        message.attach(part)

        server = smtplib.SMTP(
            smtp_server,
            smtp_port,
        )

        server.starttls()

        server.login(
            sender,
            password,
        )

        server.sendmail(
            sender,
            to,
            message.as_string(),
        )

        server.quit()

        return {
            "success": True,
            "message": "Email sent successfully.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }
@mcp.tool()
def validate_email(email: str):
    """Validate an email address."""
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if re.match(pattern, email):
        return {
            "valid": True,
            "message": "Valid email address.",
        }

    return {
        "valid": False,
        "message": "Invalid email address.",
    }

@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
):
    """
    Send an email.
    """

    validation = validate_email(to)

    if not validation["valid"]:
        return {
            "success": False,
            "message": validation["message"],
        }

    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))

    message = MIMEMultipart()

    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject

    message.attach(
        MIMEText(body, "plain")
    )

    try:

        server = smtplib.SMTP(
            smtp_server,
            smtp_port,
        )

        server.starttls()

        server.login(
            sender,
            password,
        )

        server.sendmail(
            sender,
            to,
            message.as_string(),
        )

        server.quit()

        return {
            "success": True,
            "message": "Email sent successfully.",
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e),
        }
if __name__ == "__main__":
    mcp.run(transport="stdio")