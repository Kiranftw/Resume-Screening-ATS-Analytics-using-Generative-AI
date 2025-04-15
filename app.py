from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from werkzeug.utils import secure_filename
import os
from ResumeAnalytice import ResumeAnalytics
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

result = {
    "RESUME_RELEVANCE_SCORE": 65,
    "ROLE_FIT_SCORE": 55,
    "ATS_SCORE": 60,
    "KEYWORD_MATCH_SCORE": 70,
    "MATCHED_KEYWORDS": [
        "Python",
        "Machine Learning",
        "AI",
        "Skills",
        "Projects",
        "Data Science",
        "Gemini API",
        "GenAI"
    ],
    "MISSING_KEYWORDS": [
        "Generative AI",
        "TensorFlow",
        "PyTorch",
        "Large Language Models",
        "Novel Generative Techniques"
    ],
    "MISSING_SKILLS": [
        "Deploying Large Language Models",
        "Researching Novel Generative Techniques"
    ],
    "RESUME_TIPS": [
        "Add 'Generative AI' to the skills section.",
        "Include specific projects showcasing experience with TensorFlow or PyTorch.",
        "Quantify experience with AI projects using metrics.",
        "Expand on the description of AI-related projects, explicitly mentioning the application of Large Language Models.",
        "Add 'LLM' and 'Large Language Models' as keywords in your resume.",
        "Detail the process of deploying AI models in project descriptions.",
        "Include 'model deployment' as a keyword in your skills section.",
        "Mention any research experience related to generative techniques.",
        "Elaborate on experience with responsible AI development, if applicable.",
        "Highlight experience with specific Google AI technologies like PaLM 2 or Gemini, if available."
    ],
    "COURSE_RECOMMENDATIONS": {
        "Deploying Large Language Models": [
            {
                "COURSE_NAME": "TensorFlow Developer Professional Certificate",
                "PLATFORM": "Coursera",
                "DESCRIPTION": "Learn to build and deploy TensorFlow models in various environments.",
                "DIFFICULTY": "Intermediate",
                "COURSE_LINK": "https://www.coursera.org/professional-certificates/tensorflow-in-practice"
            },
            {
                "COURSE_NAME": "AI Product Management",
                "PLATFORM": "Udacity",
                "DESCRIPTION": "Learn how to manage the product lifecycle for AI products, including deployment considerations.",
                "DIFFICULTY": "Advanced",
                "COURSE_LINK": "https://www.udacity.com/course/ai-product-manager--nd088"
            },
            {
                "COURSE_NAME": "Full Stack Deep Learning",
                "PLATFORM": "Fullstackdeeplearning.com",
                "DESCRIPTION": "A practical course covering the entire deep learning lifecycle, from data collection to deployment.",
                "DIFFICULTY": "Advanced",
                "COURSE_LINK": "https://fullstackdeeplearning.com/"
            }
        ],
        "Researching Novel Generative Techniques": [
            {
                "COURSE_NAME": "Generative Adversarial Networks (GANs) Specialization",
                "PLATFORM": "Coursera",
                "DESCRIPTION": "Learn the fundamentals of GANs and implement various generative models.",
                "DIFFICULTY": "Intermediate",
                "COURSE_LINK": "https://www.coursera.org/specializations/generative-adversarial-networks-gans"
            },
            {
                "COURSE_NAME": "Deep Learning Specialization",
                "PLATFORM": "Coursera",
                "DESCRIPTION": "Covers fundamental concepts of deep learning and neural networks.",
                "DIFFICULTY": "Intermediate",
                "COURSE_LINK": "https://www.coursera.org/specializations/deep-learning"
            },
            {
                "COURSE_NAME": "Natural Language Processing Specialization",
                "PLATFORM": "Coursera",
                "DESCRIPTION": "This specialization covers the elements of natural language processing (NLP).",
                "DIFFICULTY": "Intermediate",
                "COURSE_LINK": "https://www.coursera.org/specializations/natural-language-processing"
            }
        ]
    }
}
print(result["ATS_SCORE"])
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


analytics = ResumeAnalytics()

@app.route('/')
def landing_page():
    return render_template('Landing Page.html')  # This is your landing page

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import logging

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('landing_page'))

    ats_score = None
    resume_score = None
    keyword_match = None
    
    ats_score = result['ATS_SCORE']
    resume_score = result['RESUME_RELEVANCE_SCORE']
    keyword_match = result['KEYWORD_MATCH_SCORE']
        
     
    return render_template(
        'Dashboard.html',
        username=session['user'],
        ats_score=ats_score,
        resume_score=resume_score,
        keyword_match=keyword_match
    )


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


