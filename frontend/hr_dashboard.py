import streamlit as st
import os
import sys
import json
import dotenv
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Firebase configuration - get from session state
def get_firebase_db():
    """Get Firebase database from session state"""
    if 'firebase_db' not in st.session_state:
        # Load environment variables
        dotenv.load_dotenv()
        firebaseConfig = os.getenv("FIREBASE_CONFIG")
        
        if not firebaseConfig:
            st.error("❌ System configuration error. Please contact support.")
            return None
        
        try:
            import pyrebase
            if isinstance(firebaseConfig, str):
                firebaseConfig = json.loads(firebaseConfig)
            firebase = pyrebase.initialize_app(firebaseConfig)
            st.session_state.firebase_db = firebase.database()
            st.session_state.firebase_auth = firebase.auth()
        except Exception as e:
            st.error("❌ Unable to connect to database. Please try again later.")
            return None
    
    return st.session_state.firebase_db

def display_data_management():
    """Display data management options for HR"""
    st.subheader("🗄️ Data Management Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📊 **View Current Data**\nBelow you can see all interview results and analytics.")
    
    with col2:
        st.warning("⚠️ **Delete All Data**\nPermanently remove all interview data from the system.")
        
        if st.button("🗑️ Delete All Interview Data", type="secondary"):
            st.session_state.show_delete_confirmation = True
    
    # Show confirmation dialog if delete was clicked
    if st.session_state.get('show_delete_confirmation', False):
        st.error("⚠️ **DANGER ZONE** ⚠️")
        st.markdown("""
        **You are about to delete ALL interview data for ALL candidates!**
        
        This action will:
        - ❌ Remove all candidate interview results
        - ❌ Delete all questions and answers  
        - ❌ Clear all scores and feedback
        - ❌ Remove all analytics data
        
        **This action CANNOT be undone!**
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Yes, Delete Everything", type="primary"):
                delete_all_interview_data()
                
        with col2:
            if st.button("❌ Cancel", type="secondary"):
                st.session_state.show_delete_confirmation = False
                st.rerun()
        
        with col3:
            st.write("")  # Spacer

def delete_all_interview_data():
    """Delete all interview data from Firebase"""
    try:
        db = get_firebase_db()
        if not db:
            st.error("❌ Unable to connect to database.")
            return
        
        # Get user token for authentication
        if 'user' not in st.session_state or 'idToken' not in st.session_state.user:
            st.error("❌ Authentication required.")
            return
        
        user_token = st.session_state.user['idToken']
        
        with st.spinner("🗑️ Deleting all interview data..."):
            # Delete all interviews
            db.child("interviews").remove(user_token)
            
            # Clear the confirmation flag
            st.session_state.show_delete_confirmation = False
            
            # Show success message
            st.success("✅ All interview data has been permanently deleted!")
            st.balloons()
            
            # Force page refresh to update the display
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error deleting data: {str(e)}")
        st.session_state.show_delete_confirmation = False

def hr_dashboard():
    """Simple HR Dashboard to view and analyze interview results"""
    st.title("🏢 HR Dashboard")
    st.markdown("### 📊 Interview Results & Analysis")
    
    # Add management options
    with st.expander("🔧 Data Management"):
        display_data_management()
    
    st.markdown("---")
    
    display_interview_results()

def display_interview_results():
    """Display interview results section with analytics"""
    # Check authentication
    if 'user' not in st.session_state:
        st.warning("⚠️ Please log in to access the HR dashboard.")
        return
    
    # Get Firebase data
    db = get_firebase_db()
    if not db:
        return
    
    try:
        # Get all interviews from Firebase
        interviews_data = db.child("interviews").get().val()
        
        if not interviews_data:
            st.info("📋 No interview data available yet.")
            return
        
        # Process interview data for analytics
        all_interviews = []
        
        for user_id, user_interviews in interviews_data.items():
            for interview_id, interview_data in user_interviews.items():
                interview_info = {
                    'candidate_email': interview_data.get('user_email', 'Unknown'),
                    'total_score': interview_data.get('total_score', 0),
                    'average_score': interview_data.get('average_score', 0),
                    'total_questions': interview_data.get('total_questions', 0),
                    'status': interview_data.get('status', 'Unknown'),
                    'interview_date': interview_data.get('interview_date', 0),
                    'questions': interview_data.get('questions', {})
                }
                all_interviews.append(interview_info)
        
        if not all_interviews:
            st.info("📋 No completed interviews found.")
            return
        
        # Display analytics overview
        display_analytics_overview(all_interviews)
        
        st.markdown("---")
        
        # Display individual interview results
        st.subheader("📝 Individual Interview Results")
        
        for i, interview in enumerate(all_interviews, 1):
            with st.expander(f"Interview #{i} - {interview['candidate_email']} (Score: {interview['average_score']:.1f}/10)"):
                
                # Basic info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Score", f"{interview['total_score']}/100")
                    st.metric("Average Score", f"{interview['average_score']:.1f}/10")
                
                with col2:
                    st.metric("Questions Asked", interview['total_questions'])
                    st.metric("Status", interview['status'].title())
                
                with col3:
                    if interview['interview_date']:
                        date_str = datetime.fromtimestamp(interview['interview_date']/1000).strftime('%Y-%m-%d %H:%M')
                        st.write(f"**Date:** {date_str}")
                    st.write(f"**Email:** {interview['candidate_email']}")
                
                # Show category-wise performance
                if interview['questions']:
                    display_category_analysis(interview['questions'])
                
                # Show detailed Q&A
                st.markdown("#### 💬 Questions & Answers")
                for q_key, q_data in interview['questions'].items():
                    st.markdown(f"**{q_key.upper()}: {q_data.get('category', 'Unknown').replace('_', ' ').title()}**")
                    st.write(f"**Q:** {q_data.get('question', 'N/A')}")
                    st.write(f"**A:** {q_data.get('answer', 'N/A')}")
                    
                    score = q_data.get('score', 0)
                    if score >= 8:
                        st.success(f"**Score:** {score}/10 ✅")
                    elif score >= 6:
                        st.warning(f"**Score:** {score}/10 ⚠️")
                    else:
                        st.error(f"**Score:** {score}/10 ❌")
                    
                    st.write(f"**Feedback:** {q_data.get('justification', 'N/A')}")
                    st.markdown("---")
            
    except Exception as e:
        st.error("❌ Error loading interview data.")

def display_analytics_overview(interviews):
    """Display analytics overview of all interviews"""
    st.subheader("📈 Analytics Overview")
    
    # Calculate metrics
    total_interviews = len(interviews)
    avg_score = sum(interview['average_score'] for interview in interviews) / total_interviews
    completed_interviews = len([i for i in interviews if i['status'].lower() == 'completed'])
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interviews", total_interviews)
    with col2:
        st.metric("Average Score", f"{avg_score:.1f}/10")
    with col3:
        st.metric("Completed", completed_interviews)
    with col4:
        pass_rate = len([i for i in interviews if i['average_score'] >= 6]) / total_interviews * 100
        st.metric("Pass Rate (6+)", f"{pass_rate:.1f}%")
    
    # Score distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Score Distribution")
        scores = [interview['average_score'] for interview in interviews]
        
        try:
            import plotly.express as px
            fig = px.histogram(
                x=scores, 
                nbins=10, 
                title="Interview Score Distribution",
                labels={'x': 'Score', 'y': 'Number of Candidates'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            # Fallback to simple display if plotly not available
            st.bar_chart(pd.DataFrame({'Scores': scores}))
    
    with col2:
        st.markdown("##### 🎯 Performance Categories")
        
        # Categorize performance
        excellent = len([s for s in scores if s >= 9])
        good = len([s for s in scores if 7 <= s < 9])
        average = len([s for s in scores if 5 <= s < 7])
        poor = len([s for s in scores if s < 5])
        
        performance_data = {
            'Category': ['Excellent (9-10)', 'Good (7-8.9)', 'Average (5-6.9)', 'Poor (<5)'],
            'Count': [excellent, good, average, poor],
            'Percentage': [
                f"{excellent/total_interviews*100:.1f}%",
                f"{good/total_interviews*100:.1f}%", 
                f"{average/total_interviews*100:.1f}%",
                f"{poor/total_interviews*100:.1f}%"
            ]
        }
        
        df = pd.DataFrame(performance_data)
        st.dataframe(df, hide_index=True, use_container_width=True)

def display_category_analysis(questions):
    """Display category-wise performance for an interview"""
    st.markdown("#### 📊 Category Performance")
    
    # Calculate category scores
    categories = {}
    for q_data in questions.values():
        category = q_data.get('category', 'unknown').replace('_', ' ').title()
        score = q_data.get('score', 0)
        
        if category not in categories:
            categories[category] = []
        categories[category].append(score)
    
    # Display category averages
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

# Simple export functionality
def export_interview_data():
    """Export interview data as CSV"""
    try:
        db = get_firebase_db()
        if not db:
            return
        
        interviews_data = db.child("interviews").get().val()
        
        if not interviews_data:
            st.warning("No data to export.")
            return
        
        # Flatten data for CSV export
        export_rows = []
        
        for user_id, user_interviews in interviews_data.items():
            for interview_id, interview_data in user_interviews.items():
                row = {
                    'Candidate Email': interview_data.get('user_email', 'Unknown'),
                    'Total Score': interview_data.get('total_score', 0),
                    'Average Score': interview_data.get('average_score', 0),
                    'Total Questions': interview_data.get('total_questions', 0),
                    'Status': interview_data.get('status', 'Unknown'),
                    'Interview Date': datetime.fromtimestamp(interview_data.get('interview_date', 0)/1000).strftime('%Y-%m-%d %H:%M') if interview_data.get('interview_date') else 'N/A'
                }
                export_rows.append(row)
        
        df = pd.DataFrame(export_rows)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Interview Results (CSV)",
            data=csv,
            file_name=f"interview_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error("❌ Error exporting data.")

# Add export button at the bottom
if st.session_state.get('user'):
    st.markdown("---")
    st.subheader("📥 Export Data")
    if st.button("Download All Results as CSV", type="secondary"):
        export_interview_data()

if __name__ == "__main__":
    hr_dashboard()