import fitz  # PyMuPDF
import spacy
from spacy.matcher import PhraseMatcher

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Skill list (customizable)
skill_list = [
    "python", "java", "c++", "javascript", "html", "css",
    "machine learning", "deep learning", "data analysis",
    "communication", "teamwork", "sql", "pandas", "numpy", "tensorflow"
]

# Phrase Matcher Setup
matcher = PhraseMatcher(nlp.vocab)
patterns = [nlp.make_doc(skill.lower()) for skill in skill_list]
matcher.add("Skills", patterns)

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Extract skills from text
def extract_skills(text):
    doc = nlp(text.lower())
    matches = matcher(doc)
    skills = set([doc[start:end].text for _, start, end in matches])
    return list(skills)

# Combined function (like an API)
def extract_resume_skills(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    skills = extract_skills(text)
    return skills

# Example usage
skills_found = extract_resume_skills(r"C:\Users\koret\Mini Project\Resume-Sample-2.pdf")
print("Skills:", skills_found)
