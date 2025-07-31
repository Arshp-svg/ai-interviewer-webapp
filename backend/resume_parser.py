import os
import re
import fitz  # PyMuPDF

class ResumeParser:
    def __init__(self):
        self.skill_categories = {
            "programming_languages": ["python", "java", "c", "c++", "c#", "javascript", "typescript", "ruby", "go", "swift", "kotlin"],
            "web_development": ["html", "css", "javascript", "react", "angular", "vue", "django", "flask", "node.js", "express"],
            "database": ["mysql", "postgresql", "sqlite", "mongodb", "redis", "oracle"],
            "tools_and_platforms": ["git", "docker", "kubernetes", "aws", "azure", "gcp", "firebase", "linux"],
            "machine_learning": ["tensorflow", "pytorch", "scikit-learn", "keras", "pandas", "numpy", "opencv", "matplotlib"],
            "soft_skills": ["communication", "teamwork", "problem solving", "leadership", "time management", "adaptability"]
        }

    def extract_skills(self, resume_text: str, grouped=False):
        resume_text = resume_text.lower()
        extracted = {} if grouped else set()

        for category, skills in self.skill_categories.items():
            found = []
            for skill in skills:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, resume_text):
                    if grouped:
                        found.append(skill)
                    else:
                        extracted.add(skill)
            if grouped and found:
                extracted[category] = found

        return extracted if grouped else list(extracted)

    def extract_projects(self, resume_text: str) -> list:
        resume_text = resume_text.lower()
        project_keywords = ["project", "developed", "built", "created", "implemented", "designed"]
        lines = resume_text.split("\n")
        projects = []

        for line in lines:
            if any(kw in line for kw in project_keywords) and len(line.strip()) > 20:
                projects.append(line.strip())

        return list(set(projects))


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
    parser = ResumeParser()
    test_file = "data/sample_resume.pdf"  # Replace with your test file
    text = read_resume_text(test_file)

    skills = parser.extract_skills(text, grouped=True)
    projects = parser.extract_projects(text)
    

    print("Extracted Skills by Category:")
    for category, skill_list in skills.items():
        print(f"{category}: {skill_list}")

    print("\nExtracted Projects:")
    for proj in projects:
        print(f"- {proj}")
