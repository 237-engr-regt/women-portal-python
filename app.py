from flask import Flask, render_template, request
import os

app = Flask(__name__)

# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- SUBMIT FORM ----------------
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

            print("Form Data:", name, email, message)

            return f"""
            <h2>✅ Form Submitted Successfully!</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Message:</b> {message}</p>
            <a href="/">⬅ Back</a>
            """

        except Exception as e:
            return f"❌ Error: {str(e)}"

    return "⚠️ Please submit form from homepage"


# ---------------- ADMIN PAGE ----------------
@app.route('/admin')
def admin():
    return render_template('admin.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# ---------------- VIEW PAGE ----------------
@app.route('/view')
def view():
    return render_template('view.html')


# ---------------- RUN (RENDER SAFE) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)