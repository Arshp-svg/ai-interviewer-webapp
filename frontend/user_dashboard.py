import streamlit as st
import os
import sys
import uuid
import time
import json
import dotenv
from backend.question_generator import QuestionGenerator
from backend.resume_parser import ResumeParser, read_resume_text
from backend.speech_io import SpeechIO
from backend.answer_analyzer import analyze_answer_with_ai
from backend.interview_summary import show_interview_summary, show_question_feedback

# Firebase configuration - get from session state instead of reloading
def get_firebase_db():
    """Get Firebase database from session state"""
    if 'firebase_db' not in st.session_state:
        # Initialize Firebase if not already done
        dotenv.load_dotenv()
        firebaseConfig = os.getenv("FIREBASE_CONFIG")
        if not firebaseConfig:
            st.error("❌ System configuration error. Please contact support.")
            return None
        
        try:
            import pyrebase
            firebaseConfig = json.loads(firebaseConfig)
            firebase = pyrebase.initialize_app(firebaseConfig)
            st.session_state.firebase_db = firebase.database()
            st.session_state.firebase_auth = firebase.auth()
        except Exception:
            st.error("❌ Unable to connect to database. Please try again later.")
            return None
    
    return st.session_state.firebase_db

def get_firebase_auth():
    """Get Firebase auth from session state"""
    if 'firebase_auth' not in st.session_state:
        get_firebase_db()  # This will initialize both db and auth
    return st.session_state.firebase_auth

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
os.makedirs(DATA_DIR, exist_ok=True)

def store_answer_to_firebase(db, candidate_uid, interview_id, question_data):
    """Store answer to Firebase - simplified version"""
    try:
        if 'user' not in st.session_state or 'idToken' not in st.session_state.user:
            st.error("❌ Session expired. Please log in again.")
            return False
        
        user_token = st.session_state.user['idToken']
        
        # Store individual question with minimal data
        question_key = f"q{question_data['question_number']}"
        simple_question_data = {
            "category": question_data['category'],
            "question": question_data['question_text'],
            "answer": question_data['answer'],
            "score": question_data['score'],
            "justification": question_data['justification']
        }
        
        # Store question
        db.child("interviews").child(candidate_uid).child(interview_id).child("questions").child(question_key).set(simple_question_data, user_token)
        
        # Update total score and average
        current_interview = db.child("interviews").child(candidate_uid).child(interview_id).get(user_token).val()
        
        if current_interview:
            current_total = current_interview.get('total_score', 0)
            current_questions = current_interview.get('total_questions', 0)
        else:
            current_total = 0 
            current_questions = 0
        
        # Calculate new totals
        new_total = current_total + question_data['score']
        new_question_count = current_questions + 1
        new_average = round(new_total / new_question_count, 1) if new_question_count > 0 else 0
        
        # Update interview summary
        interview_summary = {
            "user_email": st.session_state.user['email'],
            "total_score": new_total,
            "total_questions": new_question_count,
            "average_score": new_average,
            "interview_date": int(time.time() * 1000),
            "status": "completed" if new_question_count >= 10 else "in_progress"
        }
        
        db.child("interviews").child(candidate_uid).child(interview_id).update(interview_summary, user_token)
        
        # Update user profile
        user_update = {
            "email": st.session_state.user['email'],
            "total_interviews": 1,
            "last_interview": int(time.time() * 1000)
        }
        db.child("users").child(candidate_uid).update(user_update, user_token)
        
        return True
    except Exception as e:
        st.error("❌ Unable to save your response. Please continue with the interview.")
        return False



def timed_interview_session():
    """Simple interview function - exactly 10 questions (2 per category) - Voice Only"""
    # Initialize interview data
    if 'interview_data' not in st.session_state:
        st.session_state.interview_data = {
            'question_count': 0,
            'interview_id': str(uuid.uuid4()),
            'current_question': None,
            'categories_used': {
                'technical_skills': 0,
                'communication': 0,
                'problem_solving': 0,
                'leadership': 0,
                'experience': 0
            },
            'total_score': 0,
            'voice_welcome': False
        }

    st.subheader("🎤 Voice-Only AI Interview - 10 Questions Total")
    
    # Welcome message for voice interview
    if not st.session_state.interview_data.get('voice_welcome', False):
        st.info("🔊 **Voice Interview Mode**: Questions will be spoken aloud, and you'll provide answers using your microphone. Make sure your speakers and microphone are working properly.")
        st.session_state.interview_data['voice_welcome'] = True
    
    # Check if interview is completed
    if st.session_state.interview_data['question_count'] >= 10:
        show_interview_summary()
        return
    
    # Progress bar - show current question number (already answered + 1)
    current_question_num = st.session_state.interview_data['question_count'] + 1
    progress = current_question_num / 10
    st.progress(progress, text=f"Question {current_question_num}/10")
    
    # Current question display
    if st.session_state.interview_data.get('current_question'):
        st.subheader(f"❓ Question {current_question_num}")
        
        # Show question text for reference
        with st.expander("📖 Question Text (for reference)"):
            st.write(st.session_state.interview_data['current_question'])
        
        # Voice answer input only
        st.subheader("🎤 Voice Answer")
        st.info("🔊 Click the button below and speak your answer clearly into the microphone.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🎙️ Record Answer", type="primary"):
                with st.spinner("🎧 Listening... Please speak your answer clearly."):
                    try:
                        speech_io = SpeechIO()
                        voice_answer = speech_io.listen_for_answer(timeout=30)
                        
                        if voice_answer and voice_answer.strip():
                            st.success("✅ Answer recorded successfully!")
                            st.write(f"**Your Answer:** {voice_answer}")
                            process_answer(voice_answer.strip())
                        else:
                            st.warning("⚠️ No speech detected or couldn't understand. Please try again.")
                    except Exception as e:
                        st.error("❌ Voice recording failed. Please try again.")
        
        with col2:
            if st.button("� Repeat Question"):
                try:
                    speech_io = SpeechIO()
                    speech_io.speak(st.session_state.interview_data['current_question'])
                    st.success("🔊 Question repeated!")
                except Exception as e:
                    st.warning("⚠️ Voice output failed.")
    else:
        # Generate first question or next question
        if st.button("🚀 Start/Next Question", type="primary"):
            generate_and_ask_question()

# show_interview_summary function moved to backend/interview_summary.py

def generate_and_ask_question():
    """Generate next question - 2 questions per category"""
    if 'user' not in st.session_state or 'idToken' not in st.session_state.user:
        st.error("❌ Session expired. Please refresh the page and log in again.")
        return
    
    if 'extracted_skills' not in st.session_state or 'extracted_projects' not in st.session_state:
        st.error("❌ Please upload your resume first before starting the interview.")
        return
    
    # Determine which category to ask next
    categories = ['technical_skills', 'communication', 'problem_solving', 'leadership', 'experience']
    current_category = None
    
    # Find category that needs more questions (each category should have exactly 2)
    for category in categories:
        if st.session_state.interview_data['categories_used'][category] < 2:
            current_category = category
            break
    
    if not current_category:
        st.error("❌ All categories completed!")
        return
    
    try:
        question_generator = QuestionGenerator()
        skills = st.session_state.get('extracted_skills', {})
        projects = st.session_state.get('extracted_projects', [])
        
        # Generate question for specific category
        question, _ = question_generator.generate_ai_question(skills, projects, set(), current_category)
        
        if question:
            # Update question data and category counter, but don't increment question_count yet
            # question_count will be incremented after the answer is processed
            st.session_state.interview_data['categories_used'][current_category] += 1
            st.session_state.interview_data['current_question'] = question
            st.session_state.interview_data['current_category'] = current_category
            
            # Speak the question aloud
            try:
                speech_io = SpeechIO()
                speech_io.speak(question)
                # Show which question number this will be (current count + 1)
                next_question_num = st.session_state.interview_data['question_count'] + 1
                st.success(f"🔊 Speaking Question {next_question_num}/10 - {current_category.replace('_', ' ').title()}")
            except Exception as e:
                st.warning("⚠️ Voice output failed, but question is ready.")
            
            st.rerun()
        else:
            st.warning("⚠️ Unable to generate question. Please try again.")
            
    except Exception:
        st.error("❌ Error generating question. Please try again.")

def process_answer(answer):
    """Process and analyze the candidate's answer"""
    if not answer or not answer.strip():
        st.warning("⚠️ Please provide an answer.")
        return
    
    current_question = st.session_state.interview_data.get('current_question')
    current_category = st.session_state.interview_data.get('current_category')
    
    if not current_question:
        st.error("❌ No question to answer. Please generate a question first.")
        return
    
    try:
        # Analyze answer with AI
        question_generator = QuestionGenerator()
        score, justification, category = analyze_answer_with_ai(
            answer, current_question, question_generator.client
        )
        
        if score is not None:
            # Use the category from question generation if available
            final_category = current_category or category
            
            # Prepare simplified question data
            question_data = {
                "question_text": current_question,
                "category": final_category,
                "answer": answer,
                "score": score,
                "justification": justification,
                "timestamp": int(time.time() * 1000),
                "question_number": st.session_state.interview_data['question_count'] + 1
            }
            
            # Store to Firebase
            db = get_firebase_db()
            if db:
                candidate_uid = st.session_state.user['localId']
                interview_id = st.session_state.interview_data['interview_id']
                store_answer_to_firebase(db, candidate_uid, interview_id, question_data)
            
            # Update total score and increment question counter
            st.session_state.interview_data['total_score'] += score
            st.session_state.interview_data['question_count'] += 1
            
            # Clear current question
            st.session_state.interview_data['current_question'] = None
            st.session_state.interview_data['current_category'] = None
            
            # Show feedback using modular function
            show_question_feedback(score, justification, final_category)
            
            # Provide voice feedback for the score
            try:
                speech_io = SpeechIO()
                if score >= 8:
                    speech_io.speak(f"Excellent answer! You scored {score} out of 10.")
                elif score >= 6:
                    speech_io.speak(f"Good answer. You scored {score} out of 10.")
                else:
                    speech_io.speak(f"You scored {score} out of 10. Keep going!")
            except:
                pass  # Continue if voice feedback fails
            
            # Check if interview is complete
            if st.session_state.interview_data['question_count'] >= 10:
                st.success("🎉 Interview completed! Scroll down to see your complete results.")
                try:
                    speech_io = SpeechIO()
                    speech_io.speak("Congratulations! Your interview is now complete. Please review your detailed results below.")
                except:
                    pass
            else:
                # Show progress info for next question
                questions_completed = st.session_state.interview_data['question_count']
                st.info(f"✨ Ready for question {questions_completed + 1}? Click 'Start/Next Question' above to continue.")
            
            st.rerun()  # Refresh to show next question or summary
        else:
            st.error("❌ Unable to analyze your answer. Please try again.")
            
    except Exception:
        st.error("❌ Error analyzing answer. Please try again.")

def end_interview():
    """End the interview manually (before 10 questions)"""
    question_count = st.session_state.interview_data['question_count']
    
    # Reset interview data
    st.session_state.interview_data = {
        'question_count': 0,
        'interview_id': str(uuid.uuid4()),
        'current_question': None,
        'categories_used': {
            'technical_skills': 0,
            'communication': 0,
            'problem_solving': 0,
            'leadership': 0,
            'experience': 0
        },
        'total_score': 0
    }
    
    st.success(f"✅ Interview ended! You answered {question_count} questions.")
    st.rerun()

def start_interview():
    st.title("📄 AI Interviewer - Resume Upload")

    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file:
        try:
            unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            file_path = os.path.join(DATA_DIR, unique_filename)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success("✅ Resume uploaded successfully!")

            parser = ResumeParser()
            resume_text = read_resume_text(file_path)

            # Clean up file after processing
            try:
                os.remove(file_path)
            except Exception:
                # Silently handle file cleanup errors
                pass

            if not resume_text.strip():
                st.error("❌ Unable to read resume content. Please check your file and try again.")
                return

            # Extract skills and projects
            skills = parser.extract_skills(resume_text, grouped=True)
            projects = parser.extract_projects(resume_text)
            
            # Store in session state for interview use
            st.session_state.extracted_skills = skills
            st.session_state.extracted_projects = projects

            if not skills and not projects:
                st.warning("⚠️ No skills or projects detected in your resume. Please ensure your resume contains relevant information.")
                return

            st.subheader("🧠 Extracted Information")
            
            # Display skills in a more user-friendly way
            if skills:
                st.write("**Skills Found:**")
                for category, items in skills.items():
                    if items:
                        st.write(f"• **{category.replace('_', ' ').title()}**: {', '.join(items[:5])}{'...' if len(items) > 5 else ''}")
            
            # Display projects
            if projects:
                st.write("**Projects Found:**")
                for i, proj in enumerate(projects[:3], 1):  # Show only first 3 projects
                    if isinstance(proj, dict):
                        st.write(f"{i}. {proj.get('title', 'Unnamed Project')}")
                    else:
                        st.write(f"{i}. {str(proj)[:100]}...")
                if len(projects) > 3:
                    st.write("...")

            # Start timed interview
            timed_interview_session()
            
        except Exception:
            st.error("❌ Error processing your resume. Please try uploading again or contact support.")

if __name__ == "__main__":
    start_interview()