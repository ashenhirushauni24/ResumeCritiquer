import io
import os

import PyPDF2
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", page_icon="📄", layout="centered")

st.title("Ai Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

uploaded_file  = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you are targetting (optional)")

analyze = st.button("Analyze Resume")

def  extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("UTF-8")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback.
        focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job application'}

        resume content:
        {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations."""

        client = genai.Client(api_key=GOOGLE_API_KEY)

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are an expert resume reviewer with years of experience in HR and recruitment.",
                temperature=0.7
            )
        )

        st.markdown("### Analysis Results")
        st.markdown(response.text)

    except (UnicodeDecodeError, OSError, ValueError, PyPDF2.errors.PdfReadError) as e:
        st.error(f"An error occured: {e!s}")