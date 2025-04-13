from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
init_db()


@app.route('/')
def landing_page():
    return render_template('Landing Page.html')  # This is your landing page

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('Dashboard.html', username=session['user'])
    flash('Please login first.', 'warning')
    return redirect(url_for('landing_page'))  # Redirect to landing page instead of home

@app.route('/ats-score')
def ats_score():
    return render_template('Ats score.html')

@app.route('/resume-score')
def resume_score():
    return render_template('Resume score.html')

@app.route('/missing-skills')
def missing_skills():
    return render_template('Missing skills.html')

@app.route('/course-recommendations')
def course_recommendations():
    return render_template('Course recommendations.html')

@app.route('/cover-letter')
def cover_letter():
    return render_template('Cover letter.html')

# ---------- AUTHENTICATION ROUTES ----------

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user'] = user['username']
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('landing_page'))  # Redirect to landing page instead of home

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['fullname']
    email = request.form['email']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                     (username, email, hashed_password))
        conn.commit()
        conn.close()

        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('landing_page'))  # Redirect to landing page after signup
    except sqlite3.IntegrityError:
        flash('Username or email already exists.', 'danger')
        return redirect(url_for('landing_page'))  # Redirect to landing page on error

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('landing_page'))  # Ensure logout redirects to landing page

# ---------- ERROR HANDLING ----------

@app.errorhandler(404)
@app.errorhandler(500)
def handle_errors(e):
    flash("Something went wrong. Redirected to home.", "warning")
    return redirect(url_for('landing_page'))  # Redirect to landing page on errors

# ---------- MAIN ----------

if __name__ == '__main__':
    app.run(debug=True)
