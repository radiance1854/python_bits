import smtplib
from email.message import EmailMessage

def send_email_with_optional_attachment(smtp_server, smtp_port, sender, recipient, subject, body, attachment_bytes=None, attachment_filename=None):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    # Optional File Attachment (Memory)
    if attachment_bytes and attachment_filename:
        msg.add_attachment(
            attachment_bytes,
            maintype="text", 
            subtype="csv",
            filename=attachment_filename
        )

    # Send
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.send_message(msg)