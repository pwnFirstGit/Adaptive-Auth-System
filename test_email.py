from dotenv import load_dotenv
load_dotenv()

from app.services.email_service import send_otp_email

result = send_otp_email("youremail@gmail.com", "482910")
print("✅ Email sent!" if result else "❌ Failed.")