from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import smtplib
from datetime import datetime

load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

print(f"📨 FROM Email: {EMAIL_ADDRESS}")

def send_email(to_email, location_url, source="voice"):
    print(f"📨 Email function called to: {to_email}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"🚨 Emergency Alert via {source.capitalize()} [{now}]"

    msg = MIMEText(f"""🚨 URGENT EMERGENCY ALERT 🚨

Someone has triggered a distress signal and might be in immediate danger.

📍 Location: {location_url}

Please take immediate action and reach the location as soon as possible.

This could be a life-saving response.
""")
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email  # ✅ Important for Gmail filters

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Email failed:", e)
