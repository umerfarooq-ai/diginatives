import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email: str, subject: str, body: str):
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_user or not gmail_password:
        raise Exception("GMAIL_USER and GMAIL_APP_PASSWORD environment variables must be set.")
    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_otp_email(to_email: str, otp: str, purpose: str):
    subject = f"Your OTP for {purpose}"
    body = f"Your OTP is: {otp}\nIt is valid for 10 minutes."
    send_email(to_email, subject, body) 