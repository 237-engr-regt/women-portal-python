from flask import Flask, render_template, request, jsonify, send_file, redirect, session, send_from_directory
import os
from dotenv import load_dotenv
import random
import base64
from openpyxl import Workbook, load_workbook
from threading import Lock
from datetime import datetime, timedelta
from supabase import create_client

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "secret123"

print("🔥 FINAL SUPABASE + EXCEL VERSION RUNNING")

# 🔐 ADMIN LOGIN
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# 🔥 SUPABASE CONFIG
SUPABASE_URL = "https://ygqibfiqnpikejimqzsp.supabase.co"
SUPABASE_KEY = "sb_publishable_xAwyjDC9kfowKyi-akhTgQ_s0aT1X5p"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== PATH ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "audio_files")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXCEL_FILE = os.path.join(BASE_DIR, "complaints.xlsx")

# ================== EXCEL ==================
excel_lock = Lock()

def create_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = Workbook()
        ws = wb.active

        ws.append([
            "ID", "Complaint ID", "Name", "Address", "Contact", "Email",
            "Unit", "WO", "Quarter", "Complaint", "Category",
            "Subcategory", "Reply", "Audio", "Date"
        ])

        wb.save(EXCEL_FILE)

create_excel()

def save_to_excel(data):
    with excel_lock:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active

        next_id = ws.max_row
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ws.append([next_id, *data[1:], now])
        wb.save(EXCEL_FILE)

        print("✅ Saved to Excel")

# ================== ROUTES ==================

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

            # 🔥 SUPABASE SAVE
            data = {
                "id": complaint_id,
                "name": name,
                "address": address,
                "contact": contact,
                "email": email,
                "unit": unit,
                "wo": wo,
                "quarter": quarter,
                "complaint": complaint_text,
                "category": category,
                "subcategory": subcategory,
                "reply": "Pending",
                "audio": audio_path
            }

            supabase.table("complaints").insert(data).execute()

            # EXCEL SAVE
            save_to_excel([
                "", complaint_id, name, address, contact, email,
                unit, wo, quarter, complaint_text,
                category, subcategory, "Pending", audio_path
            ])

            return jsonify({"status": "success", "id": complaint_id})

        except Exception as e:
            print("❌ ERROR:", e)
            return jsonify({"status": "error", "message": str(e)})

    return render_template("complaint.html")

# -------- ADMIN LOGIN --------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and request.form.get("password") == ADMIN_PASS:
            session['admin'] = True
            return redirect("/dashboard")
        return "Wrong Credentials"
    return render_template("login.html")

# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect("/admin")

    res = supabase.table("complaints").select("*").execute()
    data = res.data

    return render_template("admin.html", data=data)

# -------- REPLY --------
@app.route('/reply/<id>', methods=['POST'])
def reply(id):
    reply_text = request.form.get('reply')

    supabase.table("complaints").update({
        "reply": reply_text
    }).eq("id", id).execute()

    return jsonify({"status": "success"})

# -------- DELETE --------
@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    supabase.table("complaints").delete().eq("id", id).execute()
    return jsonify({"status": "success"})

# -------- DOWNLOAD (LAST 24 HOURS) --------
@app.route('/download')
def download():
    if not os.path.exists(EXCEL_FILE):
        return "No data found"

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    new_wb = Workbook()
    new_ws = new_wb.active

    new_ws.append([cell.value for cell in ws[1]])

    now = datetime.now()
    last_24 = now - timedelta(hours=24)

    for row in ws.iter_rows(min_row=2, values_only=True):
        try:
            row_date = datetime.strptime(row[-1], "%Y-%m-%d %H:%M:%S")
            if row_date >= last_24:
                new_ws.append(row)
        except:
            continue

    file_path = os.path.join(BASE_DIR, "last_24_hours.xlsx")
    new_wb.save(file_path)

    return send_file(file_path, as_attachment=True)

# -------- AUDIO --------
@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/admin")

# -------- RUN --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)