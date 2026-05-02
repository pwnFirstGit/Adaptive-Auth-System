import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_otp_email(to_email: str, otp: str):
    """Send OTP to user's email via Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = to_email
        msg["Subject"] = "Your Login Verification Code"

        body = f"""
        Hello,

        Your one-time verification code is:

        🔐 {otp}

        This code expires in 5 minutes.
        If you didn't request this, please ignore this email.

        — Adaptive Auth System
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"[Email] OTP sent to {to_email}")
        return True

    except Exception as e:
        print(f"[Email] Failed to send: {e}")
        return False