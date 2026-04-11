from flask import Flask, render_template, request, jsonify, send_file, redirect, session, send_from_directory
import sqlite3
import os
from dotenv import load_dotenv
import random
import base64
from openpyxl import Workbook
import threading
import requests

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "secret123"

print("🔥 FINAL RESEND FIX VERSION RUNNING")

# 🔐 ADMIN LOGIN
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ✅ API CONFIG
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

print("📧 KEY:", RESEND_API_KEY)
print("📧 ADMIN:", ADMIN_EMAIL)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "audio_files")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- DATABASE --------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT,
            name TEXT,
            address TEXT,
            contact TEXT,
            email TEXT,
            unit TEXT,
            wo TEXT,
            quarter TEXT,
            complaint TEXT,
            category TEXT,
            subcategory TEXT,
            reply TEXT,
            audio TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -------- AUDIO --------
@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# -------- EMAIL FUNCTION --------
def send_email(data, audio_link=None):
    try:
        print("📤 SENDING EMAIL...")

        if not RESEND_API_KEY:
            print("❌ NO API KEY")
            return

        if not ADMIN_EMAIL:
            print("❌ NO ADMIN EMAIL")
            return

        body = f"""
🚨 New Complaint

ID: {data[0]}
Name: {data[1]}
Contact: {data[3]}
Category: {data[8]}
Complaint: {data[10]}
"""

        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "onboarding@resend.dev",
                "to": [ADMIN_EMAIL],   # ✅ FIX
                "subject": f"Complaint {data[0]}",
                "html": f"<pre>{body}</pre>"
            }
        )

        print("📧 STATUS:", res.status_code)
        print("📧 BODY:", res.text)

    except Exception as e:
        print("❌ ERROR:", str(e))

# -------- HOME --------
@app.route('/')
def landing():
    return render_template("landing.html")

# -------- SUBMIT --------
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if request.method == 'POST':
        try:
            complaint_id = "CMP" + str(random.randint(10000, 99999))

            name = request.form.get('name')
            address = request.form.get('address')
            contact = request.form.get('contact')
            email = request.form.get('email')
            unit = request.form.get('unit')
            wo = request.form.get('wo')
            quarter = request.form.get('quarter')
            category = request.form.get('category')
            subcategory = request.form.get('subcategory')
            complaint_text = request.form.get('complaint')

            audio_data = request.form.get("audio_data")
            audio_path = ""

            if audio_data:
                header, encoded = audio_data.split(",", 1)
                file_data = base64.b64decode(encoded)

                filename = f"{complaint_id}.webm"
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                with open(filepath, "wb") as f:
                    f.write(file_data)

                audio_path = f"/audio/{filename}"

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute("""
                INSERT INTO complaints 
                (complaint_id, name, address, contact, email, unit, wo, quarter, complaint, category, subcategory, reply, audio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                complaint_id, name, address, contact, email,
                unit, wo, quarter, complaint_text,
                category, subcategory, "", audio_path
            ))

            conn.commit()
            conn.close()

            # 🔥 THREAD FIX
            t = threading.Thread(
                target=send_email,
                args=((complaint_id, name, address, contact, email,
                       unit, wo, quarter, category, subcategory, complaint_text), audio_path)
            )
            t.daemon = True
            t.start()

            return jsonify({"status": "success", "id": complaint_id})

        except Exception as e:
            print("❌ ERROR:", e)
            return jsonify({"status": "error", "message": str(e)})

    return render_template("complaint.html")

# -------- ADMIN --------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and request.form.get("password") == ADMIN_PASS:
            session['admin'] = True
            return redirect("/dashboard")
        return "❌ Wrong Credentials"
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect("/admin")

    conn = sqlite3.connect(DB_PATH)
    data = conn.execute("SELECT * FROM complaints").fetchall()
    conn.close()

    return render_template("admin.html", data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/admin")

# -------- RUN --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)