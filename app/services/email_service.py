import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def send_otp_email(to_email: str, otp: str):
    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": to_email,
            "subject": "Your Login Verification Code",
            "html": f"""
                <h2>Your OTP Code</h2>
                <p>Your verification code is:</p>
                <h1>🔐 {otp}</h1>
                <p>This code expires in 5 minutes.</p>
            """
        })
        print(f"[Email] OTP sent to {to_email}")
        return True
    except Exception as e:
        print(f"[Email Error] {e}")
        return False
