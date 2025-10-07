import pyrebase
import streamlit as st
import os
from frontend.user_dashboard import start_interview
from frontend.hr_dashboard import hr_dashboard
import dotenv
import json
import time

# Configure the Streamlit page
st.set_page_config(
    page_title="CelestiQ - AI Interviewer", 
    page_icon="🧑‍💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables and initialize Firebase
@st.cache_resource
def init_firebase():
    """Initialize Firebase connection (cached)"""
    try:
        # Try to get Firebase config from Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets') and 'FIREBASE_CONFIG' in st.secrets:
            config = dict(st.secrets["FIREBASE_CONFIG"])
        else:
            # Fallback to environment variables (for local development)
            dotenv.load_dotenv()
            firebaseConfig = os.getenv("FIREBASE_CONFIG")
            if not firebaseConfig:
                # Try to read from secrets.toml directly for local development
                try:
                    import toml
                    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
                    if os.path.exists(secrets_path):
                        secrets = toml.load(secrets_path)
                        if 'FIREBASE_CONFIG' in secrets:
                            config = secrets['FIREBASE_CONFIG']
                        else:
                            st.error("❌ Firebase configuration not found in secrets.toml")
                            st.stop()
                    else:
                        st.error("❌ System configuration error. Please contact support.")
                        st.stop()
                except ImportError:
                    st.error("❌ Missing toml package. Install with: pip install toml")
                    st.stop()
            else:
                config = json.loads(firebaseConfig)
        
        firebase = pyrebase.initialize_app(config)
        auth = firebase.auth()
        db = firebase.database()
        return auth, db
    except Exception as e:
        st.error(f"❌ Failed to connect to authentication service: {str(e)}")
        st.info("💡 Check your Firebase configuration in .streamlit/secrets.toml")
        st.stop()
        st.stop()

# Initialize Firebase
auth, db = init_firebase()

def create_enhanced_user_profile(uid, email, role, name=""):
    """Create simple user profile"""
    user_data = {
        "email": email,
        "role": role,
        "name": name,
        "created_at": int(time.time() * 1000)
    }
    
    if role == "candidate":
        user_data.update({
            "total_interviews": 0,
            "last_interview": None,
            "profile": {
                "skills_extracted": False,
                "resume_uploaded": False,
                "interview_status": "not_started"
            }
        })
    # HR users just have basic profile with role - no complex permissions
    
    return user_data

def logout_user():
    """Logout user and clear session"""
    for key in ['user', 'role', 'interview_active', 'interview_data', 'extracted_skills', 'extracted_projects', 'user_data']:
        if key in st.session_state:
            del st.session_state[key]
    st.success("✅ Logged out successfully!")
    st.rerun()

def main():
    """Main application function"""
    # Show sidebar if user is logged in
    if 'user' in st.session_state:
        with st.sidebar:
            user_data = st.session_state.get('user_data', {})
            st.markdown(f"### 👋 Welcome!")
            
            # Show user info
            if user_data.get('name'):
                st.markdown(f"**Name:** {user_data['name']}")
            st.markdown(f"**Email:** {st.session_state.user['email']}")
            st.markdown(f"**Role:** {st.session_state.get('role', 'Unknown')}")
            
            # Show role-specific info
            if st.session_state.get("role") == "HR":
                st.markdown("---")
                st.markdown("### � HR Access")
                st.info("• View all interview results\n• Analyze candidate performance\n• Export data reports")
                
            elif st.session_state.get("role") == "Candidate":
                st.markdown("---")
                st.markdown("### 🎯 Your Progress")
                st.metric("Total Interviews", user_data.get('total_interviews', 0))
                profile = user_data.get('profile', {})
                status = profile.get('interview_status', 'not_started').replace('_', ' ').title()
                st.markdown(f"**Status:** {status}")
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()

    # Main content area
    if 'user' not in st.session_state:
        # Landing page for non-logged-in users
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1>🚀 Welcome to CelestiQ</h1>
            <h3>AI-Powered Interview Assessment Platform</h3>
            <p style="font-size: 1.2em; color: #666;">
                Experience the future of recruitment with our intelligent interview system
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features showcase
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            ### 🤖 AI-Powered Questions
            Dynamic question generation based on your resume and skills
            """)
        with col2:
            st.markdown("""
            ### 📊 Real-time Scoring
            Instant performance analysis with detailed feedback
            """)
        with col3:
            st.markdown("""
            ### 🎯 Category-wise Assessment
            Technical, Communication, Analytical, Leadership evaluation
            """)
        
        st.markdown("---")
        
        # Login/Signup section
        st.markdown("### 🔐 Access Your Account")
        role = st.radio("Select your role:", ["Candidate", "HR"], horizontal=True, key="role_selector")
        
        # Create two columns for login and signup
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 🔓 {role} Login")
            with st.form("login_form"):
                email = st.text_input("📧 Email Address")
                password = st.text_input("🔑 Password", type="password")
                login_submit = st.form_submit_button("Login", use_container_width=True)
                
                if login_submit:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        try:
                            with st.spinner("Logging in..."):
                                user = auth.sign_in_with_email_and_password(email, password)
                                uid = user['localId']
                                user_data = db.child("users").child(uid).get().val()
                                
                                # If user data exists in Firebase, use it
                                if user_data:
                                    user_role = user_data.get("role", "").lower()
                                    if user_role == role.lower():
                                        st.session_state.user = user
                                        st.session_state.role = role
                                        st.session_state.user_data = user_data
                                        
                                        # Update last login for HR users
                                        if role.lower() == "hr":
                                            db.child("users").child(uid).child("last_login").set(int(time.time() * 1000))
                                        
                                        st.success(f"✅ {role} login successful!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Account exists but role mismatch. Expected: {role}, Found: {user_role.title()}")
                                else:
                                    # For new users or missing data, create profile
                                    user_profile = create_enhanced_user_profile(uid, email, role.lower())
                                    db.child("users").child(uid).set(user_profile)
                                    st.session_state.user = user
                                    st.session_state.role = role
                                    st.session_state.user_data = user_profile
                                    st.success(f"✅ {role} login successful! Profile created.")
                                    st.rerun()
                                    
                        except Exception as e:
                            st.error("❌ Login failed. Please check your credentials and try again.")
        
        with col2:
            if role == "Candidate":
                st.markdown("#### 🆕 Create Candidate Account")
                with st.form("signup_form"):
                    signup_email = st.text_input("📧 Email Address", key="signup_email")
                    signup_name = st.text_input("👤 Full Name (Optional)", key="signup_name")
                    signup_password = st.text_input("🔑 Password (Min. 6 characters)", type="password", key="signup_password")
                    confirm_password = st.text_input("🔑 Confirm Password", type="password", key="confirm_password")
                    signup_submit = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if signup_submit:
                        if not signup_email or not signup_password:
                            st.error("Please fill in required fields")
                        elif len(signup_password) < 6:
                            st.error("Password must be at least 6 characters")
                        elif signup_password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            try:
                                with st.spinner("Creating account..."):
                                    user = auth.create_user_with_email_and_password(signup_email, signup_password)
                                    uid = user['localId']
                                    
                                    # Create enhanced user profile
                                    user_data = create_enhanced_user_profile(uid, signup_email, "candidate", signup_name)
                                    db.child("users").child(uid).set(user_data)
                                    
                                    st.success("✅ Account created successfully! You can now log in.")
                            except Exception:
                                st.error("❌ Account creation failed. Please try again or contact support if the issue persists.")
            else:
                st.info("🔒 HR accounts are created by administrators. Please contact your system administrator for access.")
    
    else:
        # User is logged in - show appropriate dashboard
        if st.session_state.get("role") == "HR":
            # HR Dashboard
            hr_dashboard()
            
        elif st.session_state.get("role") == "Candidate":
            # Candidate Dashboard
            start_interview()

if __name__ == "__main__":
    main()