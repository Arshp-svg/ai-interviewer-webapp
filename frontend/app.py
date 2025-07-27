import streamlit as st
import tempfile
import os
import sys

# Add the parent directory to path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.resume_parser import ResumeParser, read_resume_text
def main():
    st.title("AI Interviewer - Upload Your Resume")

    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        st.info(f"File uploaded: {uploaded_file.name}")

        # Parse resume and extract skills
        parser = ResumeParser()
        resume_text = read_resume_text(tmp_path)
        skills = parser.extract_skills(resume_text)

        # Show extracted skills
        if skills:
            st.success("Extracted Skills:")
            for skill in skills:
                st.write(f"- {skill}")
        else:
            st.warning("No skills detected. Please try another resume.")

        # Clean up temp file after processing
        os.remove(tmp_path)

        # TODO: Add a button to start interview here after skills extraction
        if skills:
            if st.button("Start Interview"):
                st.write("Interview starting... (You can implement next steps here)")
                pass

if __name__ == "__main__":
    main()
