from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import PyPDF2
import os
import fitz
import boto3
from urllib.parse import urlparse
from botocore.exceptions import NoCredentialsError
import json
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Add CORS support
CORS(app, origins=["https://app.rework.club"])

port = int(os.environ.get("PORT", 5000))

def post_process_text(text):
    cleaned_text = text.replace("**", "")
    return cleaned_text

def generate_custom_tech_questions(skills):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    prompt = (f"""can you give me with 10 interview questions for freshers based on the mandatory skills mentioned
    the job description as follows {skills}
    I need response in a structure as
        [
            {{
                "question_id": 1,
                "response": ""
            }},
            ...
        ]
    """)
    response = model.generate_content(prompt)
    return post_process_text(response.text)

def generate_custom_non_tech_questions(resume_text, job_description_text):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    prompt = (f"""Imagine you are conducting an interview with a candidate who has submitted a resume highlighting their
              work experience and projects relevant to the position. Craft a set of questions that delve into their
              past experiences and assess their technical skills based on the requirements outlined in the job
              description. Work Experience: Review the candidate's work experience as outlined in their resume.
              Craft questions that explore specific accomplishments, challenges faced, and roles undertaken in their
              previous positions. Project Experience: Analyze the projects listed on the candidate's resume. Develop
              questions that probe into the methodologies employed, the candidate's contributions, problem-solving
              strategies, and lessons learned from these projects. Technical Skills: Referencing the technical
              skills mentioned in the job description, devise questions to evaluate the candidate's proficiency in
              these areas. These questions should assess not only theoretical knowledge but also practical
              application and problem-solving abilities. Integration of Experience and Skills: Formulate questions
              that require the candidate to integrate their past work experiences and technical skills. This could
              involve hypothetical scenarios or real-world challenges relevant to the role they are applying for
              here is the resume \n{resume_text} \n\n here is the job description \n{job_description_text}
              I need response in a structure as
                    [
                        {{
                            "question_id": 1,
                            "response": ""
                        }},
                        ...
                    ]
              """)
    response = model.generate_content(prompt)
    return post_process_text(response.text)

def extract_text_from_pdf(pdf_data):
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    return text

S3_BUCKET = 'sandbox-file-upload'
# PDF_KEY = os.getenv("PDF_KEY")

# AWS credentials
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")

def get_pdf_data_from_s3(bucket_name, object_name):
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_KEY,
                          region_name=AWS_REGION)
        temp_pdf_path = './temp_pdf_file.pdf'
        s3.download_file(bucket_name, object_name, temp_pdf_path)
        pdf_document = fitz.open(temp_pdf_path)
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text
        pdf_document.close()
    except NoCredentialsError:
        print("Credentials not available or incorrect.")

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    try:
        if 'pdf_file' in request.files:
            pdf_file = request.files['pdf_file']
            pdf_data = pdf_file.read()
            resume_text = extract_text_from_pdf(pdf_data)
        else:
            return jsonify({"error": "No PDF file uploaded"}), 400

        PDF_KEY = request.form.get("pdf_key")
        job_description_text = get_pdf_data_from_s3(S3_BUCKET, PDF_KEY)
        skills = "Nodesjs, Reactsjs, AWS, JavaScript"
        custom_ntquestions = generate_custom_non_tech_questions(resume_text, job_description_text)
        custom_tquestions = generate_custom_tech_questions(skills)

        # Parse the generated questions into Python lists of dictionaries
        nt_questions_list = json.loads(custom_ntquestions)
        t_questions_list = json.loads(custom_tquestions)

        # Create a dictionary with both sets of questions
        json_response = {
            "custom_questions": {
                "non_technical": nt_questions_list,
                "technical": t_questions_list
            }
        }
        return jsonify(json_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
