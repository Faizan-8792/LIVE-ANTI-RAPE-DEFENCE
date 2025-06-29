import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash
import threading
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "mysecret")

TO_EMAIL = None

# Start gesture and voice detection
def launch_emergency_monitor(email):
    global TO_EMAIL
    TO_EMAIL = email
    os.environ["TO_EMAIL"] = email
    print("📥 Loaded TO_EMAIL:", TO_EMAIL)

    import subprocess
    subprocess.Popen([sys.executable, "gesture_detector.py"])
    subprocess.Popen([sys.executable, "voice_trigger.py"])

@app.route("/")
def home():
    return render_template("index0.html")

@app.route("/defence", methods=["GET", "POST"])
def defence():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            flash("✅ Emergency Monitoring Started", "success")
            threading.Thread(target=launch_emergency_monitor, args=(email,)).start()
            return redirect(url_for("defence"))
        else:
            flash("❌ Please enter a valid email address", "danger")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
