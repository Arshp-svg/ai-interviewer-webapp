import pyrebase
import streamlit as st
import os
from frontend.user_dashboard import start_interview
import dotenv
import json
import time 

dotenv.load_dotenv()
firebaseConfig = os.getenv("FIREBASE_CONFIG")
firebaseConfig = json.loads(firebaseConfig)
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

st.set_page_config(page_title="CelestiQ", page_icon="🧑‍💼", layout="centered")

# App title
st.markdown("## 👤 Welcome to CelestiQ ")

# Only show login/signup if user is NOT logged in
if 'user' not in st.session_state:
    st.markdown("### 🔐 Login or Sign up to access candidate insights")
    role = st.radio("Select your role:", ["Candidate", "HR"], horizontal=True)
    st.markdown("---")
    if role == "Candidate":
        st.markdown("### 👤 Candidate Portal")
        choice = st.radio("Choose an option:", ["Login", "Signup"], horizontal=True)
        email = st.text_input("📧 Candidate Email Address")
        password = st.text_input("🔑 Password (Min. 6 characters)", type="password")
        st.markdown("")
        if choice == "Signup":
            if st.button("🆕 Create Candidate Account"):
                try:
                    user = auth.create_user_with_email_and_password(email, password)
                    uid = user['localId']
                    # Save user info to Realtime Database
                    db.child("users").child(uid).set({
                        "email": email,
                        "role": "candidate",
                        "name": "",
                        "created_at": int(time.time() * 1000)
                    })
                    st.success("✅ Candidate account created! You can now log in.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        elif choice == "Login":
            if st.button("🔓 Candidate Login"):
                try:
                    user = auth.sign_in_with_email_and_password(email, password)
                    uid = user['localId']
                    user_data = db.child("users").child(uid).get().val()
                    if user_data and user_data.get("role") == "candidate":
                        st.session_state.user = user
                        st.session_state.role = "Candidate"
                        st.success("✅ Candidate login successful!")
                        st.rerun()
                    else:
                        st.error("❌ You are not authorized to log in as Candidate.")
                except Exception as e:
                    st.error(f"❌ Login failed: {e}")

    elif role == "HR":
        st.markdown("### 🧑‍💼 HR Portal")
        email = st.text_input("📧 HR Email Address")
        password = st.text_input("🔑 Password (Min. 6 characters)", type="password")
        st.markdown("")
        if st.button("🔓 HR Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                uid = user['localId']
                user_data = db.child("users").child(uid).get().val()
                if user_data and user_data.get("role") == "hr":
                    st.session_state.user = user
                    st.session_state.role = "HR"
                    st.success("✅ HR login successful!")
                    st.rerun()
                else:
                    st.error("❌ You are not authorized to log in as HR.")
            except Exception as e:
                st.error(f"❌ Login failed: {e}")

if 'user' in st.session_state:
    st.markdown("---")
    if st.session_state.get("role") == "HR":
        st.markdown("## 📊 HR Candidate Dashboard")
        st.success(f"👋 Hello, `{st.session_state.user['email']}`")
        st.info("🧾 Candidate profiles, scores, and analytics will appear here.")
    elif st.session_state.get("role") == "Candidate":
        start_interview()