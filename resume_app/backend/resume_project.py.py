from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_info(text):
    # Simple regex-based extraction for demo
    skills = re.findall(r'\b(Python|JavaScript|Java|C\+\+|NLP|Machine Learning|AI|Data Science)\b', text, re.IGNORECASE)
    experience = re.findall(r'(\d+)\s*years?\s*of?\s*experience', text, re.IGNORECASE)
    education = re.findall(r'(Bachelor|Bachelor\'s|Master|Master\'s|PhD|Doctorate)\s*(of|in)?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
    keywords = re.findall(r'\b[A-Za-z]{3,}\b', text)[:10]  # Top 10 words as keywords

    # Ensure experience is a list of strings
    experience = [f"{exp} years of experience" for exp in experience]

    return {
        'skills': list(set(skills)),
        'experience': experience,
        'education': education,
        'keywords': list(set(keywords))
    }

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['resume']
    location = request.form.get('location', 'us')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save file temporarily
    file_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(file_path)

    # Extract text based on file type
    if file.filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file.filename.lower().endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

    # Extract information
    extracted_info = extract_info(text)
    print("Extracted info:", extracted_info)  # Debug log

    # Mock job recommendations based on skills
    job_recommendations = []
    if 'python' in [s.lower() for s in extracted_info['skills']]:
        job_recommendations.append({
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': 'Remote',
            'description': 'Develop applications using Python.',
            'url': '#'
        })
    if 'nlp' in [s.lower() for s in extracted_info['skills']]:
        job_recommendations.append({
            'title': 'NLP Engineer',
            'company': 'AI Solutions',
            'location': 'San Francisco, CA',
            'description': 'Work on natural language processing projects.',
            'url': '#'
        })

    # Clean up
    os.remove(file_path)

    return jsonify({
        'extracted_info': extracted_info,
        'job_recommendations': job_recommendations
    })

if __name__ == '__main__':
    app.run(debug=True)
