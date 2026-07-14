import os
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv()

mcp = FastMCP("email-mcp")


def validate_email_address(email: str) -> dict:
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


def get_email_configuration() -> dict:
    """Read and validate SMTP configuration."""

    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_value = os.getenv("SMTP_PORT", "587")

    if not sender:
        return {
            "success": False,
            "message": "EMAIL_ADDRESS environment variable is missing.",
        }

    if not password:
        return {
            "success": False,
            "message": "EMAIL_PASSWORD environment variable is missing.",
        }

    try:
        smtp_port = int(smtp_port_value)
    except (TypeError, ValueError):
        return {
            "success": False,
            "message": f"Invalid SMTP_PORT value: {smtp_port_value}",
        }

    return {
        "success": True,
        "sender": sender,
        "password": password,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
    }


@mcp.tool()
def validate_email(email: str) -> dict:
    """Validate an email address."""

    return validate_email_address(email)


@mcp.tool()
def send_email_with_attachment(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: str,
) -> dict:
    """Send an email with an attachment."""

    validation = validate_email_address(recipient)

    if not validation["valid"]:
        return {
            "success": False,
            "message": validation["message"],
        }

    config = get_email_configuration()

    if not config["success"]:
        return config

    attachment = Path(attachment_path)

    if not attachment.exists():
        return {
            "success": False,
            "message": f"Attachment not found: {attachment}",
        }

    message = MIMEMultipart()
    message["From"] = config["sender"]
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with attachment.open("rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{attachment.name}"',
        )

        message.attach(part)

        with smtplib.SMTP(
            config["smtp_server"],
            config["smtp_port"],
            timeout=30,
        ) as server:
            server.starttls()
            server.login(
                config["sender"],
                config["password"],
            )
            server.sendmail(
                config["sender"],
                recipient,
                message.as_string(),
            )

        return {
            "success": True,
            "message": "Email sent successfully.",
            "recipient": recipient,
            "attachment": str(attachment),
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Email sending failed: {exc}",
        }


@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
) -> dict:
    """Send an email without an attachment."""

    validation = validate_email_address(to)

    if not validation["valid"]:
        return {
            "success": False,
            "message": validation["message"],
        }

    config = get_email_configuration()

    if not config["success"]:
        return config

    message = MIMEMultipart()
    message["From"] = config["sender"]
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(
            config["smtp_server"],
            config["smtp_port"],
            timeout=30,
        ) as server:
            server.starttls()
            server.login(
                config["sender"],
                config["password"],
            )
            server.sendmail(
                config["sender"],
                to,
                message.as_string(),
            )

        return {
            "success": True,
            "message": "Email sent successfully.",
            "recipient": to,
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Email sending failed: {exc}",
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")