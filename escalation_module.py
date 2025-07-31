import smtplib
from email.message import EmailMessage

# Define your escalation rules
ESCALATION_RULES = {
    "catering": "hello@bermudapiecompany.com",
    "large order": "hello@bermudapiecompany.com",
    "complaint": "hello@bermudapiecompany.com",
    "negative experience": "hello@bermudapiecompany.com",
    "legal": "hello@bermudapiecompany.com",
    "media": "hello@bermudapiecompany.com",
    "kris furbert": "chairman@bermudapiecompany.com"
}

# Basic email config – change according to your SMTP setup
EMAIL_FROM = "yourbot@bermudapiecompany.com"
SMTP_SERVER = "smtp.yourprovider.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-smtp-username"
SMTP_PASSWORD = "your-smtp-password"


def should_escalate(message_text: str) -> tuple[bool, str, str]:
    """
    Determines whether the message text should be escalated.
    Returns a tuple: (True/False, reason, recipient_email)
    """
    lowered = message_text.lower()
    for keyword, recipient in ESCALATION_RULES.items():
        if keyword in lowered:
            return True, keyword, recipient
    return False, "", ""


def send_escalation_email(subject: str, to_email: str, body: str):
    """
    Sends an escalation email using SMTP.
    """
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Escalation email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send escalation email: {e}")


def handle_escalation(message_text: str, sender_id: str):
    """
    Checks message and triggers escalation if needed.
    """
    should_flag, reason, to_email = should_escalate(message_text)
    if should_flag:
        subject = f"Escalation Triggered: {reason.title()}"
        body = f"""
        Escalation Alert:

        Reason: {reason}
        Message: {message_text}
        Sender ID: {sender_id}

        Please take action accordingly.
        """
        send_escalation_email(subject, to_email, body)
