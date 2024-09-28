from flask import Flask, render_template, request
import gemini_1
import PyPDF2
import os
app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    resume_file = request.files['resume']
    job_description_file = request.files['job_description']

    resume_text = extract_text_from_pdf(resume_file)
    job_description_text = extract_text_from_pdf(job_description_file)
    skills = "Machine Learning, Python, Deep Learning, AI, LLM ";

    custom_ntquestions = gemini.generate_custom_non_tech_questions(resume_text, job_description_text)
    custom_tquestions = gemini.generate_custom_tech_questions(skills)
    return render_template('result.html', custom_questions=custom_ntquestions + "\n\n" + custom_tquestions)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
