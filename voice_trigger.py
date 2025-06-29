import speech_recognition as sr
from siren_player import play_siren
from location_tracker import get_live_location
from email_alert import send_email
import time

# Read user email
try:
    with open("user_email.txt", "r") as f:
        user_email = f.read().strip()
except:
    user_email = None

def listen_for_keywords():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    keywords = {"help", "leave", "bachao", "me"}
    distress_count = 0
    last_trigger_time = 0

    with mic as source:
        print("🎙️ Listening for distress words...")
        recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio).lower()
                print(f"🗣️ Recognized: {text}")

                words = text.split()
                count = sum(1 for word in words if word in keywords)

                if count > 0:
                    distress_count += count
                    print(f"⚠️ Matched distress words x{count} → Total: {distress_count}/3")

                if distress_count >= 3:
                    print("🚨 Emergency Detected! Triggering Siren + Email!")
                    play_siren()
                    location = get_live_location()
                    if location and user_email:
                        send_email(user_email, location)
                    distress_count = 0
                    last_trigger_time = time.time()

                if time.time() - last_trigger_time > 60:
                    distress_count = 0

            except sr.UnknownValueError:
                print("❌ Could not understand audio.")
            except sr.RequestError as e:
                print(f"❌ Google Error: {e}")
            except Exception as e:
                print(f"❌ Other Error: {e}")

if __name__ == "__main__":
    listen_for_keywords()
