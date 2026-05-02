import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_otp_email(to_email: str, otp_code: str, user_name: str = "User") -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your Login Verification Code"
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = to_email

        html_body = f"""
        <div style="font-family: sans-serif; max-width: 480px; margin: auto;">
            <h2>🔐 Verification Required</h2>
            <p>Hi {user_name},</p>
            <p>A login attempt was flagged. Use this code to verify:</p>
            <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px;
                        background: #f4f4f4; padding: 20px; text-align: center;
                        border-radius: 8px; margin: 20px 0;">
                {otp_code}
            </div>
            <p>Expires in <strong>10 minutes</strong>.</p>
            <p style="color: #999; font-size: 12px;">
                If this wasn't you, secure your account immediately.
            </p>
        </div>
        """

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"[Email] OTP sent to {to_email}")
        return True

    except Exception as e:
        print(f"[Email Error] {e}")
        return False