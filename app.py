from flask import Flask, render_template, request
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# ==============================
# CONFIG (IMPORTANT)
# ==============================

ADMIN_EMAIL = "yourgmail@gmail.com"   # 👈 yahan apna gmail daal
APP_PASSWORD = "your_app_password"    # 👈 Gmail App Password (NOT normal password)


# ==============================
# HOME PAGE
# ==============================

@app.route('/')
def home():
    return render_template('index.html')


# ==============================
# SEND EMAIL FUNCTION
# ==============================

def send_email(name, email, message):
    try:
        subject = "New Form Submission"
        body = f"""
New submission received:

Name: {name}
Email: {email}
Message: {message}
"""

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = ADMIN_EMAIL
        msg['To'] = ADMIN_EMAIL

        # Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(ADMIN_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email error:", e)


# ==============================
# FORM SUBMIT
# ==============================

@app.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        print("📩 New Form Data:")
        print(name, email, message)

        # Send email to admin
        send_email(name, email, message)

        return "✅ Form submitted successfully!"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ==============================
# RUN (RENDER COMPATIBLE)
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)