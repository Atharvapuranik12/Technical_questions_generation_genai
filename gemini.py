import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()


def post_process_text(text):
    cleaned_text = text.replace("**", "")
    return cleaned_text


def generate_custom_tech_questions(skills):
    genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
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
    genai.configure(api_key = os.getenv("GEMINI_API_KEY"))
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
