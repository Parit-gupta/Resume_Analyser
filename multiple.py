import re
import spacy
import pandas as pd
from PyPDF2 import PdfReader
import docx
import os

def extract_text_from_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text

def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    return match[0] if match else None

def extract_phone(text):
    match = re.findall(r"\+?\d[\d -]{8,}\d", text)
    return match[0] if match else None

def extract_name(text, nlp):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return text.split("\n")[0]

def extract_skills(text, skills_db):
    text = text.lower()
    found_skills = [skill for skill in skills_db if skill.lower() in text]
    return list(set(found_skills))

def analyze_resume(file_path, skills_db, nlp):
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return None
    name = extract_name(text, nlp)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text, skills_db)
    return {
        "File": os.path.basename(file_path),
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Skills Found": ", ".join(skills)
    }

def analyze_folder(folder_path, skills_db):
    nlp = spacy.load("en_core_web_sm")
    results = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.lower().endswith((".pdf", ".docx")):
            data = analyze_resume(file_path, skills_db, nlp)
            if data:
                results.append(data)
    return pd.DataFrame(results)

if __name__ == "__main__":
    skills_db = [
        "Python", "C++", "HTML", "CSS", "Machine Learning", "Deep Learning",
        "SQL", "Git", "GitHub", "TensorFlow", "Keras", "NLP", "Data Analysis",
        "Streamlit", "Speech Recognition", "LangChain", "Cohere"
    ]
    folder = "resume"
    df = analyze_folder(folder, skills_db)
    print("\n--- Resume Analysis for All Files ---\n")
    print(df)
    df.to_csv("resume_analysis_results.csv", index=False)
