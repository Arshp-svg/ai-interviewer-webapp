import random
import os
import re
from backend.resume_parser import ResumeParser
import groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class QuestionGenerator:
    def __init__(self, groq_api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile"):
        self.parser = ResumeParser()
        # Fix: Remove the incorrect assignment
        self.groq_api_key = groq_api_key
        self.model = model
        if groq_api_key:
            self.client = groq.Groq(api_key=groq_api_key)
        else:
            self.client = None

    def _normalize_question(self, question):
        """Normalize question for better duplicate detection."""
        # Remove extra whitespace, convert to lowercase, remove punctuation
        normalized = re.sub(r'[^\w\s]', '', question.lower().strip())
        return ' '.join(normalized.split())

    def generate_ai_question(self, skills, projects, asked_questions=None, category=None):
        if not self.client:
            raise ValueError("AI service unavailable. Please try again later.")
        if asked_questions is None:
            asked_questions = set()
        
        # Normalize existing questions for comparison
        normalized_asked = {self._normalize_question(q) for q in asked_questions}
        
        max_attempts = 5  # Limit attempts to avoid infinite loop
        
        for attempt in range(max_attempts):
            # Flatten skills dict for prompt
            if isinstance(skills, dict):
                flat_skills = []
                for v in skills.values():
                    flat_skills.extend(v)
            else:
                flat_skills = skills
            
            # Create category-specific prompt
            if category:
                category_prompts = {
                    'technical_skills': "Focus on technical knowledge, programming languages, frameworks, or tools.",
                    'communication': "Focus on teamwork, explanation abilities, or presentation skills.",
                    'problem_solving': "Focus on analytical thinking, debugging, or approach to challenges.",
                    'leadership': "Focus on leadership experience, decision making, or guiding others.",
                    'experience': "Focus on project experience, internships, or practical applications."
                }
                category_instruction = category_prompts.get(category, "")
            else:
                category_instruction = ""
            
            prompt = (
                "You are an HR manager conducting a technical interview. "
                "Consider the candidate is a fresh graduate with no prior experience. "
                f"Generate a simple interview question for the {category.replace('_', ' ') if category else 'general'} category. "
                f"{category_instruction} "
                "Do not ask to implement any code or algorithms. "
                "Keep it simple and appropriate for a fresh graduate. "
                "Just ask the question, no other information needed. "
                f"Skills: {flat_skills}\nProjects: {projects}\n"
                "Question:"
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.9,  # Increased temperature for more variety
                n=1,
            )
            
            question = response.choices[0].message.content.strip()
            normalized_question = self._normalize_question(question)
            
            # Check if this is truly a new question
            if normalized_question not in normalized_asked:
                asked_questions.add(question)
                return question, asked_questions
        
        # If AI fails to generate unique question, fall back to template
        return self.generate_random_template_question(skills, projects, asked_questions)

    def generate_random_template_question(self, skills, projects, asked_questions=None):
        """
        Fallback: Generate a random question from templates if AI is not available.
        """
        SKILL_QUESTIONS = [
            "Can you explain your experience with {skill}?",
            "What challenges have you faced using {skill}?",
            "How have you applied {skill} in your projects?",
            "What is the most advanced thing you've done with {skill}?",
            "How would you explain {skill} to someone who's never heard of it?",
            "What resources did you use to learn {skill}?",
            "How comfortable are you with {skill} on a scale of 1-10?",
            "What's one thing you'd like to improve about your {skill} knowledge?"
        ]
        PROJECT_QUESTIONS = [
            "Tell me more about your project: {project}.",
            "What was your role in the project: {project}?",
            "What challenges did you overcome in {project}?",
            "How did you use your skills in {project}?",
            "What did you learn from working on {project}?",
            "If you could redo {project}, what would you do differently?",
            "What technologies did you use in {project}?",
            "How long did it take you to complete {project}?"
        ]
        
        if asked_questions is None:
            asked_questions = set()
        
        # Normalize existing questions for comparison
        normalized_asked = {self._normalize_question(q) for q in asked_questions}
        
        options = []
        
        # Generate skill-based questions
        if skills:
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    for skill in skill_list:
                        for template in SKILL_QUESTIONS:
                            q = template.format(skill=skill)
                            if self._normalize_question(q) not in normalized_asked:
                                options.append(q)
            else:
                for skill in skills:
                    for template in SKILL_QUESTIONS:
                        q = template.format(skill=skill)
                        if self._normalize_question(q) not in normalized_asked:
                            options.append(q)
        
        # Generate project-based questions
        if projects:
            for project in projects:
                for template in PROJECT_QUESTIONS:
                    q = template.format(project=project)
                    if self._normalize_question(q) not in normalized_asked:
                        options.append(q)
        
        if not options:
            # If all specific questions exhausted, generate generic ones
            generic_questions = [
                "What motivates you to work in technology?",
                "How do you stay updated with new technologies?",
                "Describe a time when you had to learn something new quickly.",
                "What's your favorite programming language and why?",
                "How do you approach debugging a problem?",
                "What's the most interesting project you've worked on?",
                "How do you handle working under pressure?",
                "What are your career goals in technology?"
            ]
            
            for q in generic_questions:
                if self._normalize_question(q) not in normalized_asked:
                    options.append(q)
        
        if not options:
            return None, asked_questions  # All questions have been asked
        
        question = random.choice(options)
        asked_questions.add(question)
        print(f"Generated question: {question}")
        return question, asked_questions
