
import io
import os
import time

import PyPDF2
import streamlit as st
from dotenv import load_dotenv

from resumecritiquer.ai_analyzer import analyze_resume

load_dotenv()

st.set_page_config(
    page_title="AI Resume Critiquer",
    page_icon="📄",
    layout="centered",
)

st.title("AI Resume Critiquer")
st.markdown(
    "Upload your resume and get AI-powered feedback tailored to your needs!"
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

uploaded_file = st.file_uploader(
    "Upload your resume (PDF or TXT)",
    type=["pdf", "txt"],
)

job_role = st.text_input(
    "Enter the job role you are targeting (optional)"
)

analyze = st.button("Analyze Resume")


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""

    for page in pdf_reader.pages:
        text += (page.extract_text() or "") + "\n"

    return text


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(
            io.BytesIO(uploaded_file.getvalue())
        )

    return uploaded_file.getvalue().decode("utf-8")


if analyze:
    if not uploaded_file:
        st.warning("Please upload a resume first.")

    elif not GOOGLE_API_KEY:
        st.error(
            "GOOGLE_API_KEY is missing. Check your .env file."
        )

    else:
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error(
                    "The uploaded file contains no readable text."
                )

            else:
                feedback = None

                feedback = analyze_resume(file_content, job_role)

                if feedback:
                    st.success("Resume analysis completed!")
                    st.markdown("## Analysis Results")
                    st.markdown(feedback)

                else:
                    st.warning(
                        "The AI returned an empty response. "
                        "Please try again."
                    )

        except PyPDF2.errors.PdfReadError:
            st.error(
                "Could not read this PDF. Please upload a valid PDF file."
            )

        except UnicodeDecodeError:
            st.error(
                "Could not read this text file. "
                "Please save it as UTF-8 and try again."
            )

        except Exception as e:
            st.error(
                f"Analysis failed: {type(e).__name__}: {e}"
            )
