import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL       = os.getenv("EMAIL_ADDRESS")

def send_otp_email(to_email: str, otp: str):
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject="Your Login Verification Code",
            html_content=f"""
                <h2>Adaptive Auth System</h2>
                <p>Your one-time verification code is:</p>
                <h1 style="color: #4F46E5;">🔐 {otp}</h1>
                <p>This code expires in <b>5 minutes</b>.</p>
                <p>If you didn't request this, please ignore this email.</p>
            """
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"[Email] OTP sent to {to_email}")
        return True

    except Exception as e:
        print(f"[Email Error] {e}")
        return False
