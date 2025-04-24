from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from ResumeAnalytics import ResumeAnalytics

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'doc', 'jpeg', 'jpg', 'png', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

analytics = ResumeAnalytics()  # Instantiate your analytics object

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    resume_filename = None
    jd_filename = None
    show_dashboard = False

    # Default values
    ats_score = rrs_score = rfs_score = None
    total_ats_score = breakdown = None
    resume_components = {}
    missing_keywords = missing_skills = None
    resume_tips = course_recommendations = None

    if request.method == 'POST':
        resume = request.files.get('resume')
        jd = request.files.get('jd')

        resume_path = jd_path = None

        if resume and allowed_file(resume.filename):
            resume_filename = secure_filename(resume.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
            resume.save(resume_path)

        if jd and allowed_file(jd.filename):
            jd_filename = secure_filename(jd.filename)
            jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_filename)
            jd.save(jd_path)

        # === Resume Relevance + Role Fit + ATS + Recommendations ===
        result = analytics.resumeanalytics(resume_path, jd_path)
        if result is None:
            return render_template('DASHBOARD.html', error="Error in analysis. Please try again.")

        ats_score = result.get('ATS_SCORE')
        rrs_score = result.get('RESUME_RELEVANCE_SCORE')
        rfs_score = result.get('ROLE_FIT_SCORE')
        missing_keywords = len(result.get('MISSING_KEYWORDS', []))
        missing_skills = len(result.get('MISSING_SKILLS', []))
        resume_tips = result.get('RESUME_TIPS', [])
        course_recommendations = result.get('COURSE_RECOMMENDATIONS', {})

        # === ATS Analysis ===
        atsresult = analytics.ATSanalytics(resume_path)
        if atsresult is None:
            return render_template('DASHBOARD.html', error="Error in ATS analysis. Please try again.")

        resume_components = atsresult.get('Extracted Data', {})
        ats_score_data = atsresult.get('ATS Score', {})
        total_ats_score = ats_score_data.get('Total Score')
        breakdown = ats_score_data.get('Breakdown', {})

        show_dashboard = True

        return render_template('DASHBOARD.html',
                               resume_filename=resume_filename,
                               jd_filename=jd_filename,
                               show_dashboard=show_dashboard,
                               ats_score=ats_score,
                               total_ats_score=total_ats_score,
                               breakdown=breakdown,
                               rrs_score=rrs_score,
                               rfs_score=rfs_score,
                               resume_components=resume_components,
                               missing_keywords=missing_keywords,
                               missing_skills=missing_skills,
                               resume_tips=resume_tips,
                               course_recommendations=course_recommendations)

    return render_template('DASHBOARD.html', show_dashboard=False)

@app.route('/chatbot', methods=['POST'])
def chatbot_route():
    data = request.get_json()
    query = data.get("query", "")
    response = analytics.chatbot(Query=query)  # Fixed: use the instance
    return jsonify({"response": response})

@app.route('/course-recommendations')
def show_course_recommendations():
    missing_technical_skills = [
        "Python (Advanced)",
        "TensorFlow",
        "PyTorch",
        "Natural Language Processing",
        "Computer Vision"
    ]

    missing_soft_skills = [
        "Technical Leadership",
        "Stakeholder Management",
        "Agile Methodology",
        "Project Planning"
    ]

    role_matches = {
        "Data Scientist": 92,
        "Machine Learning Engineer": 89,
        "AI Research Engineer": 87,
        "Data Engineer": 85
    }

    return render_template(
        'course_recommendations.html',
        missing_technical_skills=missing_technical_skills,
        missing_soft_skills=missing_soft_skills,
        role_matches=role_matches
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
