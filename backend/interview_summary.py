"""
Interview Summary Module
Provides summary functionality using the same data structure as HR dashboard
"""

import streamlit as st
from datetime import datetime
from backend.speech_io import SpeechIO
import uuid


def get_firebase_db():
    """Get Firebase database from session state"""
    if 'firebase_db' not in st.session_state:
        return None
    return st.session_state.firebase_db


def show_interview_summary():
    """Show final interview results - uses same data HR sees"""
    st.subheader("🎉 Interview Completed!")
    st.balloons()
    
    # Voice congratulations
    try:
        speech_io = SpeechIO()
        speech_io.speak("Congratulations! Your interview has been completed successfully. Here are your results.")
    except:
        pass
    
    # Get interview data using SAME logic as HR dashboard
    try:
        db = get_firebase_db()
        if not db or 'user' not in st.session_state:
            st.error("❌ Unable to load results.")
            return
        
        candidate_uid = st.session_state.user['localId']
        
        # Get interviews data using same HR logic
        interviews_data = db.child("interviews").get().val()
        
        if not interviews_data:
            st.info("📋 No interview data available yet.")
            return
        
        # Process interview data using EXACT same logic as HR
        user_interview = None
        
        # Find current user's interview data
        if candidate_uid in interviews_data:
            user_interviews = interviews_data[candidate_uid]
            current_interview_id = st.session_state.interview_data['interview_id']
            
            if current_interview_id in user_interviews:
                interview_data = user_interviews[current_interview_id]
                
                # Use EXACT same data structure as HR sees
                user_interview = {
                    'candidate_email': interview_data.get('user_email', 'Unknown'),
                    'total_score': interview_data.get('total_score', 0),
                    'average_score': interview_data.get('average_score', 0),
                    'total_questions': interview_data.get('total_questions', 0),
                    'status': interview_data.get('status', 'Unknown'),
                    'interview_date': interview_data.get('interview_date', 0),
                    'questions': interview_data.get('questions', {})
                }
        
        if not user_interview:
            st.error("❌ No interview data found.")
            return
        
        # Display results using HR data structure
        display_performance_summary(user_interview)
        display_category_performance(user_interview)
        display_detailed_qa(user_interview)
        display_overall_assessment(user_interview)
        display_next_steps(user_interview)
        
    except Exception:
        st.error("❌ Error loading results. Your responses were saved but cannot be displayed right now.")
    
    # Action buttons
    display_action_buttons()


def display_performance_summary(user_interview):
    """Display performance summary metrics"""
    st.subheader("📊 Your Performance Summary")
    
    # Basic metrics - same as HR sees
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Score", f"{user_interview['total_score']}/100")
    
    with col2:
        st.metric("Average Score", f"{user_interview['average_score']:.1f}/10")
    
    with col3:
        st.metric("Questions Answered", user_interview['total_questions'])
    
    with col4:
        # Performance rating
        avg_score = user_interview['average_score']
        if avg_score >= 8:
            rating = "Excellent ⭐"
        elif avg_score >= 6:
            rating = "Good ✅"
        elif avg_score >= 4:
            rating = "Average 📊"
        else:
            rating = "Needs Improvement 📈"
        st.metric("Performance", rating)
    
    # Progress bar
    progress_value = min(user_interview['average_score'] / 10, 1.0)
    st.progress(progress_value, text=f"Overall Performance: {user_interview['average_score']:.1f}/10")


def display_category_performance(user_interview):
    """Display category-wise performance using HR logic"""
    if not user_interview['questions']:
        return
        
    st.subheader("📂 Performance by Category")
    
    # Calculate category scores using HR logic
    categories = {}
    for q_data in user_interview['questions'].values():
        category = q_data.get('category', 'unknown').replace('_', ' ').title()
        score = q_data.get('score', 0)
        
        if category not in categories:
            categories[category] = []
        categories[category].append(score)
    
    # Display category averages - same as HR sees
    if len(categories) > 0:
        cols = st.columns(len(categories))
        for i, (category, scores) in enumerate(categories.items()):
            with cols[i]:
                avg_score = sum(scores) / len(scores)
                
                if avg_score >= 8:
                    st.success(f"**{category}**\n{avg_score:.1f}/10 ✅")
                elif avg_score >= 6:
                    st.warning(f"**{category}**\n{avg_score:.1f}/10 ⚠️")
                else:
                    st.error(f"**{category}**\n{avg_score:.1f}/10 ❌")


def display_detailed_qa(user_interview):
    """Display detailed Q&A - same format as HR dashboard"""
    st.subheader("📝 Detailed Questions & Answers")
    st.info("💡 This is the exact same data that HR will review for your assessment.")
    
    for q_key, q_data in user_interview['questions'].items():
        score = q_data.get('score', 0)
        category_title = q_data.get('category', 'Unknown').replace('_', ' ').title()
        
        # Color code the expander based on score
        score_indicator = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"
        
        with st.expander(f"{score_indicator} {q_key.upper()}: {category_title} - Score: {score}/10"):
            
            st.markdown(f"**{q_key.upper()}: {category_title}**")
            st.write(f"**Q:** {q_data.get('question', 'N/A')}")
            st.write(f"**A:** {q_data.get('answer', 'N/A')}")
            
            # Score display with same color coding as HR
            if score >= 8:
                st.success(f"**Score:** {score}/10 ✅")
            elif score >= 6:
                st.warning(f"**Score:** {score}/10 ⚠️")
            else:
                st.error(f"**Score:** {score}/10 ❌")
            
            st.write(f"**Feedback:** {q_data.get('justification', 'N/A')}")


def display_overall_assessment(user_interview):
    """Display overall performance assessment"""
    st.subheader("🎯 Overall Assessment")
    
    avg_score = user_interview['average_score']
    if avg_score >= 8:
        st.success("🌟 **Excellent Performance!** You demonstrated strong skills across multiple areas. Your responses showed deep understanding and good communication abilities.")
    elif avg_score >= 6:
        st.info("👍 **Good Performance!** You showed solid understanding in most areas. Focus on strengthening areas where you scored lower to improve further.")
    elif avg_score >= 4:
        st.warning("📊 **Average Performance.** You have a foundation to build on. Consider focusing on improving your responses and expanding your knowledge in key areas.")
    else:
        st.error("📈 **Room for Improvement.** This interview highlighted areas where you can grow. Use this feedback to prepare better for future opportunities.")


def display_next_steps(user_interview):
    """Display next steps information"""
    st.subheader("🚀 What's Next?")
    st.info("✅ Your interview results have been saved and will be reviewed by HR. They will contact you regarding next steps in the hiring process.")
    
    # Interview date display - same format as HR
    if user_interview['interview_date']:
        date_str = datetime.fromtimestamp(user_interview['interview_date']/1000).strftime('%Y-%m-%d %H:%M')
        st.write(f"**Interview Completed:** {date_str}")
    
    st.write(f"**Your Email:** {user_interview['candidate_email']}")
    st.write(f"**Interview Status:** {user_interview['status'].title()}")


def display_action_buttons():
    """Display action buttons for user"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Send Results to Email"):
            st.success("📧 Results will be sent to your registered email address.")
    
    with col2:
        if st.button("🔄 Take New Interview"):
            # Reset for new interview
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
            st.rerun()


def show_question_feedback(score, justification, category):
    """Show feedback after each question - simplified version"""
    st.success("✅ Answer processed successfully!")
    
    # Detailed feedback display
    with st.container():
        st.markdown("---")
        st.subheader(f"📊 Question Results")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Score display with color coding
            if score >= 8:
                st.success(f"🎉 Excellent Score: {score}/10")
            elif score >= 6:
                st.info(f"👍 Good Score: {score}/10")
            else:
                st.warning(f"📈 Score: {score}/10")
            
            st.write(f"**Category:** {category.replace('_', ' ').title()}")
        
        with col2:
            st.markdown("**🤖 AI Feedback:**")
            st.write(justification)
        
        # Progress update
        if 'interview_data' in st.session_state:
            questions_completed = st.session_state.interview_data['question_count']
            st.progress(questions_completed / 10, text=f"Progress: {questions_completed}/10 questions completed")
        
        st.markdown("---")