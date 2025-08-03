import random
import os
from backend.resume_parser import ResumeParser
import groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class QuestionGenerator:
    def __init__(self, groq_api_key=GROQ_API_KEY, model="gemma2-9b-it"):
        
        self.parser = ResumeParser()
        skills = self.parser
        self.groq_api_key = groq_api_key
        self.model = model
        if groq_api_key:
            self.client = groq.Groq(api_key=groq_api_key)
        else:
            self.client = None

    def generate_ai_question(self, skills, projects, asked_questions=None):
        if not self.client:
            raise ValueError(" maybe you forgot to add api key.")
        if asked_questions is None:
            asked_questions = set()
        # Flatten skills dict for prompt
        if isinstance(skills, dict):
            flat_skills = []
            for v in skills.values():
                flat_skills.extend(v)
        else:
            flat_skills = skills
        prompt = (
            "You are an HR manager conducting a technical interview. "
            "consider the candidate is a fresh graduate with no prior experience. "
            "Given the following candidate skills and projects, generate a unique, realistic, simple interview question based on skills and projects. "
            "do not ask to implement any code or algorithms."
            "Do not repeat previous questions. "
            "Just ask question no other information is needed."
            f"Skills: {flat_skills}\nProjects: {projects}\n"
            f"Already asked: {list(asked_questions)}\n"
            "Question:"
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.8,
            n=1,
        )
        question = response.choices[0].message.content.strip()
        asked_questions.add(question)
        return question, asked_questions

    def generate_random_template_question(self, skills, projects, asked_questions=None):
        """
        Fallback: Generate a random question from templates if AI is not available.
        """
        SKILL_QUESTIONS = [
            "Can you explain your experience with {skill}?",
            "What challenges have you faced using {skill}?",
            "How have you applied {skill} in your projects?",
            "What is the most advanced thing you've done with {skill}?"
        ]
        PROJECT_QUESTIONS = [
            "Tell me more about your project: {project}.",
            "What was your role in the project: {project}?",
            "What challenges did you overcome in {project}?",
            "How did you use your skills in {project}?"
        ]
        if asked_questions is None:
            asked_questions = set()
        options = []
        if skills:
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    for skill in skill_list:
                        for template in SKILL_QUESTIONS:
                            q = template.format(skill=skill)
                            if q not in asked_questions:
                                options.append(q)
            else:
                for skill in skills:
                    for template in SKILL_QUESTIONS:
                        q = template.format(skill=skill)
                        if q not in asked_questions:
                            options.append(q)
        if projects:
            for project in projects:
                for template in PROJECT_QUESTIONS:
                    q = template.format(project=project)
                    if q not in asked_questions:
                        options.append(q)
        if not options:
            return None, asked_questions  # All questions have been asked
        question = random.choice(options)
        asked_questions.add(question)
        print(f"Generated question: {question}")
        return question, asked_questions