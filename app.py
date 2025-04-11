from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Landing Page.html')

@app.route('/dashboard')
def dashboard():
    return render_template('Dashboard.html')


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



@app.route('/login', methods=['POST'])
def login():
    return redirect(url_for('dashboard'))

@app.route('/signup', methods=['POST'])
def signup():
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
