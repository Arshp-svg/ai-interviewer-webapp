import os
import re
import fitz  # PyMuPDF

class ResumeParser:
    def __init__(self):
        self.skills_db = [
            "python", "java", "c++", "machine learning", "deep learning", "nlp",
            "data analysis", "sql", "javascript", "react", "docker",
            "aws", "azure", "git", "html", "css", "tensorflow", "pytorch",
            "flask", "django", "linux", "excel", "communication", "teamwork"
        ]

    def extract_skills(self, resume_text: str) -> list:
        resume_text = resume_text.lower()
        extracted_skills = set()
        for skill in self.skills_db:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, resume_text):
                extracted_skills.add(skill)
        return list(extracted_skills)


def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text


def read_resume_text(file_path):
    ext = file_path.lower().split('.')[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_path)
    elif ext == "txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"Unsupported file format: {file_path}")
        return ""


if __name__ == "__main__":
    data_folder = "data"
    parser = ResumeParser()

    for filename in os.listdir(data_folder):
        if filename.lower().endswith((".pdf", ".txt")):
            filepath = os.path.join(data_folder, filename)
            text = read_resume_text(filepath)
            if text.strip():
                skills = parser.extract_skills(text)
                print(f"Resume: {filename}")
                print(f"Extracted Skills: {skills}")
                print("-" * 40)
            else:
                print(f"No text extracted from {filename}")
