from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database create (auto run)
def init_db():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        relation TEXT,
        qtr TEXT,
        address TEXT,
        complaint TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Submit Complaint
@app.route('/submit', methods=['POST'])
def submit():
    email = request.form['email']
    relation = request.form['relation']
    qtr = request.form['qtr']
    address = request.form['address']
    complaint = request.form['complaint']

    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO complaints (email, relation, qtr, address, complaint)
        VALUES (?, ?, ?, ?, ?)
    ''', (email, relation, qtr, address, complaint))

    conn.commit()
    conn.close()

    return redirect('/view')

# View Complaints
@app.route('/view')
def view():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints")
    data = cursor.fetchall()

    conn.close()

    return render_template('view.html', data=data)

# Delete Complaint
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM complaints WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/view')

if __name__ == '__main__':
    app.run(debug=True)