from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'doc', 'jpeg', 'jpg', 'png', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    resume_filename = None
    jd_filename = None
    show_dashboard = False

    ats_score = 75  # Example static value for ATS score
    rrs_score = 65  # Example static value for RRS score
    rfs_score = 80  # Example static value for RFS score

    resume_components = {
        "Transliterate": True,
        "Spelling & Grammar": True,
        "Summary": False,
        "Skills": True,
        "Experience": True,
        "Certification": False,
        "Education": True,
        "Contact Details": True,
    }

    missing_keywords = 5  # Example value
    missing_skills = 3  # Example value

    if request.method == 'POST':
        resume = request.files.get('resume')
        jd = request.files.get('jd')

        if resume and allowed_file(resume.filename):
            resume_filename = secure_filename(resume.filename)
            resume.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))

        if jd and allowed_file(jd.filename):
            jd_filename = secure_filename(jd.filename)
            jd.save(os.path.join(app.config['UPLOAD_FOLDER'], jd_filename))

        show_dashboard = True  # Set show_dashboard to True after form submission and analysis
        return render_template('DASHBOARD.html',
                               resume_filename=resume_filename,
                               jd_filename=jd_filename,
                               show_dashboard=show_dashboard,
                               ats_score=ats_score,
                               rrs_score=rrs_score,
                               rfs_score=rfs_score,
                               resume_components=resume_components,
                               missing_keywords=missing_keywords,
                               missing_skills=missing_skills)

    return render_template('DASHBOARD.html')

if __name__ == '__main__':
    app.run(debug=True)
