import os
import random
import string
import csv
import io
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, Response)
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = 'change_this_to_a_random_secret_key_!@#123'

# ---------- Database Configuration ----------
DB_CONFIG = {
    'dbname': 'symposium_db',
    'user': 'postgres',
    'password': 'Vallarasu@#123',
    'host': 'localhost',
    'port': 5432
}

def get_db_connection():
    """Establish and return a PostgreSQL connection."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn

# ---------- Event List ----------
EVENTS = [
    "Paper Presentation",
    "Project Expo",
    "Coding Contest",
    "Robo-War",
    "Hackathon",
    "Quiz",
    "Debate",
    "Photography",
    "Gaming Tournament"
]

# ---------- Unique Registration ID Generator ----------
def generate_registration_id():
    """Generate a unique registration ID like SYM-2026-A3X9K2."""
    conn = get_db_connection()
    cur = conn.cursor()
    while True:
        # Year + 6 random chars
        rid = f"SYM-{datetime.now().year}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        cur.execute("SELECT 1 FROM registrations WHERE registration_id = %s", (rid,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return rid
        # If collision (extremely rare), loop again

# ---------- Admin Login Decorator ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please log in to access admin panel.", "error")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Routes ----------
@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html', events=EVENTS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle registration form submission."""
    if request.method == 'POST':
        try:
            # Fetch form data
            full_name = request.form['full_name'].strip()
            college_name = request.form['college_name'].strip()
            department = request.form['department'].strip()
            year = request.form['year'].strip()
            gender = request.form['gender'].strip()
            email = request.form['email'].strip().lower()
            phone = request.form['phone'].strip()
            event_name = request.form['event_name'].strip()
            accommodation = request.form.get('accommodation', 'No')
            accommodation = True if accommodation == 'Yes' else False

            # Basic server-side validations
            if not all([full_name, college_name, department, year, gender, email, phone, event_name]):
                flash("All fields are required.", "error")
                return render_template('register.html', events=EVENTS)

            if '@' not in email or '.' not in email.split('@')[-1]:
                flash("Invalid email address.", "error")
                return render_template('register.html', events=EVENTS)

            if not phone.isdigit() or len(phone) != 10:
                flash("Phone number must be 10 digits.", "error")
                return render_template('register.html', events=EVENTS)

            # Check for duplicate email
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM registrations WHERE email = %s", (email,))
            if cur.fetchone():
                flash("This email is already registered.", "error")
                cur.close()
                conn.close()
                return render_template('register.html', events=EVENTS)

            # Generate unique registration ID
            reg_id = generate_registration_id()

            # Insert record
            cur.execute("""
                INSERT INTO registrations
                (registration_id, full_name, college_name, department, year, gender,
                 email, phone, event_name, accommodation, registration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (reg_id, full_name, college_name, department, int(year), gender,
                  email, phone, event_name, accommodation, datetime.now()))
            cur.close()
            conn.close()

            flash("Registration successful!", "success")
            return render_template('success.html', registration_id=reg_id, name=full_name)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return render_template('register.html', events=EVENTS)

    # GET request
    return render_template('register.html', events=EVENTS)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Secure admin login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hardcoded credentials for demonstration – in production use hashed passwords
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash("Welcome, Admin!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid credentials.", "error")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Log out admin user."""
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin panel to view, search, filter, and delete registrations."""
    return render_template('admin_dashboard.html', events=EVENTS)

@app.route('/admin/registrations')
@login_required
def get_registrations():
    """API endpoint: return JSON of filtered registrations."""
    search = request.args.get('search', '').strip()
    event_filter = request.args.get('event', '').strip()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT * FROM registrations WHERE 1=1"
    params = []

    if search:
        query += """ AND (full_name ILIKE %s OR email ILIKE %s OR registration_id ILIKE %s)"""
        like = f"%{search}%"
        params.extend([like, like, like])
    if event_filter:
        query += " AND event_name = %s"
        params.append(event_filter)

    query += " ORDER BY registration_date DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert to list of dicts (already is, but ensure proper serialization)
    result = []
    for row in rows:
        result.append({
            'id': row['id'],
            'registration_id': row['registration_id'],
            'full_name': row['full_name'],
            'college_name': row['college_name'],
            'department': row['department'],
            'year': row['year'],
            'gender': row['gender'],
            'email': row['email'],
            'phone': row['phone'],
            'event_name': row['event_name'],
            'accommodation': row['accommodation'],
            'registration_date': row['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
        })
    return {'registrations': result, 'total': len(result)}

@app.route('/admin/delete/<int:reg_id>', methods=['DELETE'])
@login_required
def delete_registration(reg_id):
    """Delete a registration by its id (primary key)."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM registrations WHERE id = %s", (reg_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {'status': 'deleted'}

@app.route('/admin/export/csv')
@login_required
def export_csv():
    """Export all registrations as a CSV file."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM registrations ORDER BY registration_date DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Registration ID', 'Full Name', 'College', 'Department', 'Year',
                     'Gender', 'Email', 'Phone', 'Event', 'Accommodation', 'Registration Date'])
    for row in rows:
        writer.writerow([
            row['registration_id'],
            row['full_name'],
            row['college_name'],
            row['department'],
            row['year'],
            row['gender'],
            row['email'],
            row['phone'],
            row['event_name'],
            'Yes' if row['accommodation'] else 'No',
            row['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=symposium_registrations.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)