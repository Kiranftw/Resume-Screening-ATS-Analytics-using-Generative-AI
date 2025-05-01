from flask import Flask, render_template, request, jsonify, make_response
import os
import pdfkit
from werkzeug.utils import secure_filename
from ResumeAnalytics import ResumeAnalytics
import markdown
app = Flask(__name__)
import datetime
import time
# === Configuration ===
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'doc', 'jpeg', 'jpg', 'png', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB
config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Global Variables ===
analytics = ResumeAnalytics()
shared_data = {}  # For sharing state between routes

# === Helper Function ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Routes ===
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    resume_filename = jd_filename = None
    show_dashboard = False

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
            print(f"[DEBUG] Job description uploaded: {jd_filename}")
        
        rolematch = analytics.getJobRecommendations(resume_path)
        print(f"[DEBUG] Raw rolematch: {rolematch}")

        # Ensure we store as dictionary in shared_data
        if isinstance(rolematch, dict):
            if 'ROLEMATCHES' in rolematch:
                # If format is {'ROLEMATCHES': {...}}
                shared_data['rolematch'] = rolematch['ROLEMATCHES']
            else:
                # If already in direct dictionary format
                shared_data['rolematch'] = rolematch
        else:
            # Fallback to empty dict if not in expected format
            shared_data['rolematch'] = {}

        # === Resume Analysis ===
# === Resume Analysis ===
        result = analytics.resumeanalytics(resume_path, jd_path)
        if jd_path and resume_path:
            cover_letter = analytics.getCoverLetter(resume_path, jd_path)
            shared_data['cover_letter'] = cover_letter
            # Store preview (first 150 characters + ellipsis)
            shared_data['cover_letter_preview'] = cover_letter[:150] + "..." if len(cover_letter) > 150 else cover_letter
        if result is None:
            return render_template('DASHBOARD.html', error="Error in analysis. Please try again.")

        ats_score = result.get('ATS_SCORE')
        rrs_score = result.get('RESUME_RELEVANCE_SCORE')
        rfs_score = result.get('ROLE_FIT_SCORE')
        resume_tips = result.get('RESUME_TIPS', [])
        course_recommendations = result.get('COURSE_RECOMMENDATIONS', {})

        missing_keywordslist = result.get('MISSING_KEYWORDS', [])
        missing_skillslist = result.get('MISSING_SKILLS', [])
        missing_keywords = len(missing_keywordslist)
        missing_skills = len(missing_skillslist)

        # Store in shared_data
        shared_data['missing_keywords'] = missing_keywordslist
        shared_data['missing_skills'] = missing_skillslist
        shared_data['resume_tips'] = resume_tips  
        shared_data['course_recommendations'] = course_recommendations


        print("[DEBUG] Course Recommendations:", course_recommendations)  # <<=== (Optional) Print to debug
        # === ATS Analysis ===
        atsresult = analytics.ATSanalytics(resume_path)
        if atsresult is None:
            return render_template('DASHBOARD.html', error="Error in ATS analysis. Please try again.")

        resume_components = atsresult.get('Extracted Data', {})
        ats_score_data = atsresult.get('ATS Score', {})
        total_ats_score = ats_score_data.get('Total Score')
        breakdown = ats_score_data.get('Breakdown', {})
        shared_data['ats_tips'] = atsresult.get('Recommendations', []) 

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
    response = analytics.chatbot(query=query)
    return jsonify({"response": response})


@app.route('/resume-insights')
def show_course_recommendations():
    missing_technical_skills = shared_data.get('missing_keywords', [])
    missing_soft_skills = shared_data.get('missing_skills', [])
    resume_tips = shared_data.get('resume_tips', [])
    courseRecommendations = shared_data.get('course_recommendations', {})

    # Fetch cover letter preview first
    cover_letter_preview = shared_data.get(
        'cover_letter_preview',
        'No cover letter available. Please upload resume and job description to generate one.'
    )
    print("[DEBUG] Course Recommendations:", courseRecommendations)
    print("[DEBUG] Cover Letter Preview:", cover_letter_preview)

    
    resume_tips = shared_data.get('resume_tips', []) + shared_data.get('ats_tips', [])
    import random
    random.shuffle(resume_tips)
    resume_tips_html = [markdown.markdown(tip) for tip in resume_tips]
    role_matches = shared_data.get('rolematch', {})
    # Render the page
    return render_template(
        'course_recommendations.html',
        missing_technical_skills=missing_technical_skills,
        missing_soft_skills=missing_soft_skills,
        role_matches=role_matches,
        resume_tips=resume_tips_html,
        cover_letter_preview=cover_letter_preview
    )


@app.route('/course-recommendations')
def courseRecommendations():
    raw_course_data = shared_data.get('course_recommendations', {})
    paid_course_recommendations = {}

    # Process all courses as paid courses
    for topic, courses in raw_course_data.items():
        paid_courses = []
        for course in courses:
            # Skip YouTube courses or process all as paid
            if course['PLATFORM'].lower() != 'youtube':
                paid_courses.append(course)
        
        if paid_courses:
            paid_course_recommendations[topic] = paid_courses

    return render_template(
        'recommendations.html',  # Make sure this matches your template file name
        paid_course_recommendations=paid_course_recommendations
    )

# === Helper Function ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Routes ===
@app.route('/PDFChatbot', methods=['GET', 'POST'])
def PDFChatbot():
    global current_documents
    current_documents = []
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    
    if request.method == 'POST':
        # Handle file uploads
        uploaded_files = request.files.getlist('documents')
        query = request.form.get('query', '').strip()
        
        # Save uploaded files
        new_files = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                new_files.append(filepath)
        
        # Update current documents
        if new_files:
            current_documents = new_files
        
        # Default query if empty
        if not query and current_documents:
            query = "Please analyze my resume."
        elif not query:
            return jsonify({"response": "Please upload a resume or ask a question."})
        
        # Process the query
        try:
            response = analytics.pdfchatbot(current_documents, query)
            return jsonify({"response": response})
        except Exception as e:
            app.logger.error(f"Error in PDFChatbot: {str(e)}")
            return jsonify({"response": f"An error occurred: {str(e)}"}), 500
    
    # GET request - render the chat interface
    return render_template('chatbot.html', 
                         current_time=current_time,
                         uploaded_files=current_documents,
                         messages=[])

@app.route('/remove-file', methods=['POST'])
def remove_file():
    global current_documents
    data = request.get_json()
    filename = data.get('filename')
    
    if filename in current_documents:
        current_documents.remove(filename)
        try:
            os.remove(filename)
        except OSError:
            pass
    
    return jsonify({"status": "success"})

from flask import Flask, render_template, request, make_response
import pdfkit
from werkzeug.utils import secure_filename
import json

@app.route('/download-cover-letter', methods=['POST'])
def download_cover_letter():
    try:
        # Configure pdfkit
        config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
        
        # Get HTML content from form
        html_content = request.form.get('html')
        
        # Generate PDF
        pdf = pdfkit.from_string(html_content, False, configuration=config)
        
        # Create response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=cover_letter.pdf'
        return response
    except Exception as e:
        return str(e), 500

@app.route('/customcoverletter', methods=['GET', 'POST'])
def custom_cover_letter():
    if request.method == 'POST':
        job_title = request.form.get('jobTitle')
        company_name = request.form.get('companyName')
        your_name = request.form.get('yourName')
        additional_info = request.form.get('coverLetterContent')

        # Get the raw cover letter text (not JSON)
        cover_letter_content = analytics.getCustomCoverLetter(
            job_title, company_name, your_name, additional_info
        )

        # If the response is JSON, extract the actual content
        if cover_letter_content.startswith('{'):
            try:
                data = json.loads(cover_letter_content)
                if 'cover_letter' in data:
                    cover_letter_content = data['cover_letter']
            except json.JSONDecodeError:
                pass

        return render_template("Cover letter.html", 
                            generated=True,
                            letter_content=cover_letter_content)
    
    return render_template("Cover letter.html", generated=False)

# Add your other routes here...

@app.route('/')
def landing_page():
    return render_template('Landing Page.html')
# ... (keep your other routes the same)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)