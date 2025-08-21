import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="HR Dashboard - AI Interviewer",
    page_icon="📊",
    layout="wide",
)

# ------------------ HEADER ------------------
st.title("📊 HR Dashboard")
st.markdown("### Student Interview Performance Overview")
st.markdown("---")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    # 🚀 FUTURE: Replace this with real-time interview data
    data = pd.DataFrame({
        "Name": ["Amit", "Sneha", "Rahul", "Priya", "Arjun"],
        "Communication": [75, 60, 85, 90, 55],
        "Technical": [80, 70, 60, 95, 50],
        "Problem_Solving": [70, 65, 75, 85, 45],
        "Confidence": [85, 55, 70, 90, 60],
    })
    return data

df = load_data()

# ------------------ DROPDOWN TO SELECT STUDENT ------------------
st.subheader("🎓 Select a Student")
student_list = ["All Students"] + df["Name"].tolist()
selected_student = st.selectbox("Choose student", student_list)

# ------------------ SHOW DATA BASED ON SELECTION ------------------
if selected_student != "All Students":
    st.markdown(f"### 📖 Performance Report: **{selected_student}**")

    student_data = df[df["Name"] == selected_student].melt(
        id_vars=["Name"], var_name="Category", value_name="Score"
    )

    # Bar chart for selected student
    fig_student = px.bar(
        student_data,
        x="Category",
        y="Score",
        text="Score",
        color="Score",
        color_continuous_scale="greens",
        title=f"{selected_student}'s Scores",
    )
    fig_student.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_student.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_student, use_container_width=True)

    # Show metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🗣️ Communication", int(student_data[student_data["Category"]=="Communication"]["Score"]))
    with col2:
        st.metric("🧠 Technical", int(student_data[student_data["Category"]=="Technical"]["Score"]))
    with col3:
        st.metric("🤔 Problem Solving", int(student_data[student_data["Category"]=="Problem_Solving"]["Score"]))
    with col4:
        st.metric("💪 Confidence", int(student_data[student_data["Category"]=="Confidence"]["Score"]))

else:
    st.markdown("### 📊 Average Performance Across All Students")

    avg_scores = df.drop(columns=["Name"]).mean().reset_index()
    avg_scores.columns = ["Category", "Average Score"]

    # Bar chart for averages
    fig_avg = px.bar(
        avg_scores,
        x="Category",
        y="Average Score",
        text="Average Score",
        color="Average Score",
        color_continuous_scale="greens",
        title="Average Interview Scores by Category"
    )
    fig_avg.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_avg.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_avg, use_container_width=True)

    # Suggestion section
    weak_area = avg_scores.loc[avg_scores["Average Score"].idxmin(), "Category"]
    st.success(f"✅ Strongest Area: {avg_scores.loc[avg_scores['Average Score'].idxmax(), 'Category']}")
    st.error(f"⚠️ Weakest Area: {weak_area} → Consider focused training")
