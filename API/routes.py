from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from ..utils.pdf_handler import pdf_to_string
from ..utils.resume_optimizer import process_and_annotate_pdf  # Assuming this is the function for processing
from ..utils.prompt import welcome_users, comments, revise, keywords
import os

routes = Blueprint('routes', __name__)

# Define a directory to save uploaded files temporarily
UPLOAD_FOLDER = 'tmp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/result')
def result():
    return render_template('result.html')

@routes.route('/jobmatch')
def jobmatch():
    return render_template('jobmatch.html')

@routes.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['pdf_file']
    job_title = request.form.get('job_title')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "File is not a PDF"}), 400
    
    if not job_title:
        return jsonify({"error": "Job title is required"}), 400
    
    # Secure the filename and save it to the UPLOAD_FOLDER
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    # Read the pdf file content and save it to the session
    session['pdf_context'] = pdf_to_string(file_path)
    session['pdf_file_path'] = file_path
    session['job_title'] = job_title

    # Redirect to the result page
    return redirect(url_for('routes.result'))

@routes.route('/prompt', methods=['POST'])
def prompt():
    action = request.form.get('action')
    pdf_text = session.get('pdf_context')
    if action == 'welcome':
        response = welcome_users(pdf_text)
    elif action == 'comments':
        response = comments(pdf_text)
    elif action == 'revise':
        response = revise(pdf_text)
    elif action == 'keywords':
        response = keywords(pdf_text)
    else:
        response = "Invalid action."

    return jsonify({"response": response})

@routes.route('/process_pdf', methods=['POST'])
def process_pdf():
    pdf_file_path = session.get('pdf_file_path')
    job_title = session.get('job_title')
    if not pdf_file_path or not os.path.exists(pdf_file_path):
        return jsonify({"error": "No PDF file uploaded or file path does not exist"}), 400
    
    if not job_title:
        return jsonify({"error": "Job title is required"}), 400

    try:
        revised_pdf_path = process_and_annotate_pdf(pdf_file_path, job_title)
        session['revised_pdf_path'] = revised_pdf_path
        return jsonify({"revised_pdf_url": url_for('routes.download_revised_pdf')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route('/download_revised_pdf')
def download_revised_pdf():
    revised_pdf_path = session.get('revised_pdf_path')
    if not revised_pdf_path or not os.path.exists(revised_pdf_path):
        print(f"Revised PDF Path Not Found: {revised_pdf_path}")  # Debug print
        return jsonify({"error": "No revised PDF available or file path does not exist"}), 400
    
    try:
        # Ensure the path is absolute for sending the file
        absolute_path = os.path.abspath(revised_pdf_path)
        print(f"Sending file from: {absolute_path}")  # Debug print
        return send_file(absolute_path, as_attachment=True)
    except Exception as e:
        print(f"Error in download_revised_pdf: {e}")
        return jsonify({"error": str(e)}), 500