import os

def create_directory_structure(base_path="ai_interviewer"):
    structure = {
        "backend": [
            "__init__.py",
            "resume_parser.py",
            "question_generator.py",
            "speech_io.py",
            "answer_analyzer.py",
            "notifications.py",
            "firebase_client.py",
            "utils.py"
        ],
        "frontend": [
            "user_dashboard.py",
            "hr_panel.py",
            "app.py",
            os.path.join("components")  # folder inside frontend
        ],
        "data": [],
        "tests": [
            "test_resume_parser.py",
            "test_question_generator.py",
            "test_answer_analyzer.py"
        ],
        "": [  # Files in root directory
            "requirements.txt",
            "README.md",
            ".gitignore"
        ]
    }

    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)
        if folder and not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created directory: {folder_path}")
        for file in files:
            # If the file is actually a subdirectory (like frontend/components)
            if '.' not in file and not file.endswith('.py'):
                subfolder_path = os.path.join(folder_path, file)
                os.makedirs(subfolder_path, exist_ok=True)
                print(f"Created subdirectory: {subfolder_path}")
            else:
                file_path = os.path.join(folder_path, file)
                # Create empty files if they don't exist
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        # Optionally add basic content to __init__.py files
                        if file == "__init__.py":
                            f.write("# Init file\n")
                        else:
                            f.write("")
                    print(f"Created file: {file_path}")

if __name__ == "__main__":
    create_directory_structure()
    print("Directory structure created successfully.")
