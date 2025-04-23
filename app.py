from flask import Flask, render_template, request, redirect, url_for
from ResumeAnalytics import ResumeAnalytics
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024



resumeOBJECT = ResumeAnalytics()
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        resume = request.files.get('resume')
        jd = request.files.get('jd')

        if resume:
            resume_filename = secure_filename(resume.filename)
            resume.save(os.path.join('uploads', resume_filename))  # Save to /uploads folder

        if jd:
            jd_filename = secure_filename(jd.filename)
            jd.save(os.path.join('uploads', jd_filename))

        # Trigger analysis function here
        data = resumeOBJECT.resumeanalytics(resume_filename, jd_filename)
        resumescore = data["resume_score"]
        
    return render_template('DASHBOARD.html', resumescore=resumescore)


if __name__ == '__main__':
    app.run(debug=True)