import os

# Define file structure directly in current directory
structure = [
    "app.py",
    "requirements.txt",
    "README.md",
    "config/config.py",
    "config/serviceAccountKey.json",     # Placeholder for Firebase Admin SDK
    "data/sample_resumes/.keep",         # .keep file to track empty folder
    "assets/.keep",
    "pages/1_User_Resume_Upload.py",
    "pages/2_Interview.py",
    "pages/3_Results.py",
    "pages/4_HR_Dashboard.py",
    "modules/auth.py",
    "modules/firebase_handler.py",
    "modules/resume_parser.py",
    "modules/question_generator.py",
    "modules/voice_utils.py",
    "modules/answer_evaluator.py",
    "modules/feedback_generator.py",
]

def create_structure(paths):
    for file_path in paths:
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        # Create file unless it's a .keep (used to track empty dirs)
        if not file_path.endswith(".keep"):
            with open(file_path, "w") as f:
                f.write("# " + os.path.basename(file_path))

if __name__ == "__main__":
    create_structure(structure)
    print("✅ Project structure created in current directory.")
