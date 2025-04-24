from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'fines.db')

# Initialize database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS fines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                timestamp TEXT,
                image_path TEXT,
                status TEXT,
                appeal_reason TEXT
            )
        ''')

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        fines = conn.execute("SELECT * FROM fines").fetchall()
    return render_template('index.html', fines=fines)

@app.route('/appeal/<int:fine_id>', methods=['GET', 'POST'])
def appeal(fine_id):
    if request.method == 'POST':
        reason = request.form['reason']
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("UPDATE fines SET status='appealed', appeal_reason=? WHERE id=?", (reason, fine_id))
        return redirect(url_for('index'))

    return render_template('appeal.html', fine_id=fine_id)

@app.route('/reject/<int:fine_id>', methods=['POST'])
def reject(fine_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE fines SET status='rejected' WHERE id=?", (fine_id,))
    return redirect(url_for('index'))

# Route to view the image
@app.route('/view_image/<path:image_path>')
def view_image(image_path):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), image_path)

# Add new fine from Python script
def add_fine(vehicle_id, image_path):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            INSERT INTO fines (vehicle_id, timestamp, image_path, status, appeal_reason)
            VALUES (?, datetime('now'), ?, 'pending', '')
        ''', (vehicle_id, image_path))

@app.route('/confirm_clear_fines', methods=['GET', 'POST'])
def confirm_clear_fines():
    if request.method == 'POST':
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("DELETE FROM fines")
        return redirect(url_for('index'))  # Redirect to index page after deletion

    return render_template('confirm_clear_fines.html')  # Render confirmation page

if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True)
