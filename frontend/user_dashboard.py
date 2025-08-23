import streamlit as st
import os
import sys
import uuid
from backend.question_generator import QuestionGenerator
from backend.resume_parser import ResumeParser, read_resume_text
from backend.speech_io import SpeechIO
from backend.answer_analyzer import analyze_answer_with_ai


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(DATA_DIR, exist_ok=True)

def start_interview():
    st.title("📄 AI Interviewer - Resume Upload")

    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file:
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = os.path.join(DATA_DIR, unique_filename)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Resume saved to: `{file_path}`")

        parser = ResumeParser()
        resume_text = read_resume_text(file_path)

        try:
            os.remove(file_path)
            st.info(f"Temporary resume file deleted: `{file_path}`")
        except Exception as e:
            st.warning(f"Could not delete file: {e}")

        # Extract skills and projects
        skills = parser.extract_skills(resume_text, grouped=True)
        projects = parser.extract_projects(resume_text)

        st.subheader("🧠 Extracted Skills (Grouped by Category)")
        for category, items in skills.items():
            st.markdown(f"**{category.replace('_', ' ').title()}**: {', '.join(items)}")

        # Display projects
        if projects:
            st.subheader("💼 Detected Projects")
            for proj in projects:
                st.write(f"- {proj}")
        else:
            st.warning("No projects found in the resume.")

        if st.button("Generate AI Question"):
            st.success("Ready to start the voice interview!")
            question_generator = QuestionGenerator()
            question, _ = question_generator.generate_ai_question(skills, projects)
            st.session_state.generated_question = question
            st.success(f"Generated question: {question}")
            sio = SpeechIO()
            sio.speak(question)
            answer = sio.listen_for_answer()
            st.session_state.candidate_answer = answer
            groq_client = question_generator.client

            # Analyze the answer using AI
            if answer and groq_client:
                result = analyze_answer_with_ai(answer, question, groq_client)
                st.session_state.analysis_result = result
                st.success(f"Communication Score: {result['Communication']['score']}")
                st.success(f"Technical Score: {result['Technical']['score']}")
                st.success(f"Problem Solving Score: {result['Problem_Solving']['score']}")
                st.success(f"Confidence Score: {result['Confidence']['score']}")
                # You can also access justifications:
            else:
                st.warning("No answer detected.")

if __name__ == "__main__":
    start_interview()