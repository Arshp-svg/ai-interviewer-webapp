import streamlit as st
import os
import sys
import uuid

# Add the parent directory to path so we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.resume_parser import ResumeParser, read_resume_text



DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    st.title("📄 AI Interviewer - Resume Upload")

    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file:
        # Save uploaded resume to /data/ with a unique name
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = os.path.join(DATA_DIR, unique_filename)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Resume saved to: `{file_path}`")

        # Parse resume
        parser = ResumeParser()
        resume_text = read_resume_text(file_path)

        # Delete the file immediately after reading
        try:
            os.remove(file_path)
            st.info(f"Temporary resume file deleted: `{file_path}`")
        except Exception as e:
            st.warning(f"Could not delete file: {e}")

        # Extract skills and projects
        skills = parser.extract_skills(resume_text, grouped=True)
        projects = parser.extract_projects(resume_text)

        # Display grouped skills
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

        # Optionally: Add "Start Interview" button
        if st.button("🎙️ Start Interview"):
            st.success("Ready to start the voice interview!")
            # Proceed to next step — use `skills` + `projects` in AI engine

if __name__ == "__main__":
    main()