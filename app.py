
import os
import streamlit as st
import pdfplumber
from openai import OpenAI

# 🌐 Configure the Page
st.set_page_config(
    page_title="AI Resume Screening Assistant",
    page_icon="🤖",
    layout="wide"
)

# 🔑 Load the API Key safely
try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not API_KEY:
    st.error("API key not found. Please add OPENROUTER_API_KEY to the secrets.")
    st.stop()

# 🎯 Application Title
st.title("🤖 AI Resume Screening Assistant")

st.write(
    "Upload a resume, enter a job description, and let AI analyze the candidate's suitability for the role."
)

# 🎛️ Input Controls
uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("Enter Job Description", height=200)
analyze_button = st.button("Analyze Resume")

# 📄 Function to Extract Text from a PDF Resume
def extract_resume_text(uploaded_resume):
    resume_text = ""
    with pdfplumber.open(uploaded_resume) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                resume_text += text + "\n"
    return resume_text

# 🤖 Function to Analyze Resume
def analyze_resume(resume_text, job_description):
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    MODEL_NAME = "openrouter/free"

    prompt = f"""
You are an experienced HR Recruiter.

Compare the following resume with the job description and generate a professional screening report.

Resume:
{resume_text}

Job Description:
{job_description}

Include the following sections:

1. Candidate Summary
2. Matching Skills
3. Missing Skills
4. Strengths
5. Areas for Improvement
6. Overall Recommendation
7. Suitability Score (out of 100)
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# 🚀 Analyze Resume Action
if analyze_button:
    if uploaded_resume is None:
        st.warning("⚠️ Please upload a resume.")
        st.stop()

    if not job_description.strip():
        st.warning("⚠️ Please enter the job description.")
        st.stop()

    with st.spinner("🤖 Analyzing Resume..."):
        resume_text = extract_resume_text(uploaded_resume)

        if not resume_text.strip():
            st.warning("⚠️ No text found in this PDF. It may be a scanned image. Please upload a text-based PDF.")
            st.stop()

        try:
            report = analyze_resume(resume_text, job_description)
        except Exception as e:
            st.error(f"⚠️ The AI service returned an error: {e}")
            st.stop()

    st.success("✅ Resume Analysis Completed!")
    st.header("📊 Resume Screening Report")
    st.markdown(report)
