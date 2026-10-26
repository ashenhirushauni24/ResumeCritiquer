from __future__ import annotations

import io
import os

import PyPDF2
import streamlit as st
from dotenv import load_dotenv

from resumecritiquer.ai_analyzer import analyze_resume

load_dotenv()

st.set_page_config(
    page_title="Resume Studio | AI Resume Critiquer",
    page_icon=":material/description:",
    layout="centered",
)


def extract_text_from_pdf(pdf_file: io.BytesIO) -> str:
    """Read selectable text from every page in an uploaded PDF."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)


def extract_text_from_file(uploaded_file) -> str:
    """Extract text from the supported PDF or plain-text upload."""
    if uploaded_file.name.lower().endswith(".pdf"):
        return extract_text_from_pdf(io.BytesIO(uploaded_file.getvalue()))
    return uploaded_file.getvalue().decode("utf-8")


# A small brand header keeps the page welcoming without taking space from the task.
st.badge("AI-powered resume feedback", icon=":material/auto_awesome:", color="blue")
st.title("Make your resume work harder")
st.markdown(
    "Get clear, practical feedback tailored to the role you want. "
    "Upload a PDF or text resume to get started."
)

with st.container(border=True):
    st.subheader("Your resume", icon=":material/description:")
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=["pdf", "txt"],
        help="PDF and plain text files are supported.",
    )

    if uploaded_file:
        file_size_kb = max(1, round(uploaded_file.size / 1024))
        st.caption(f"Ready to review · {uploaded_file.name} · {file_size_kb} KB")

    job_role = st.text_input(
        "Target job role",
        placeholder="For example, product designer or data analyst",
        help="Optional. Adding a role makes the feedback more specific.",
    )

    submitted = st.button(
        "Analyze my resume",
        type="primary",
        icon=":material/auto_awesome:",
        width="stretch",
    )

st.caption("Your resume is used to generate feedback for this analysis.")

if submitted:
    if not uploaded_file:
        st.warning("Choose a PDF or TXT resume to continue.", icon=":material/upload_file:")
    elif not os.getenv("GOOGLE_API_KEY"):
        st.error(
            "Gemini is not configured yet. Add GOOGLE_API_KEY to your local environment settings.",
            icon=":material/key_off:",
        )
    else:
        try:
            resume_text = extract_text_from_file(uploaded_file)
            if not resume_text.strip():
                st.error(
                    "This file doesn't contain readable text. If it is a scanned PDF, try a text-based copy.",
                    icon=":material/text_snippet:",
                )
            else:
                with st.spinner("Reviewing your resume…"):
                    feedback = analyze_resume(resume_text, job_role)

                if feedback and feedback.strip():
                    st.success("Your review is ready", icon=":material/check_circle:")
                    st.header("Resume feedback", icon=":material/rate_review:")
                    with st.container(border=True):
                        st.markdown(feedback)
                else:
                    st.warning("The analysis returned no feedback. Please try again.")
        except PyPDF2.errors.PdfReadError:
            st.error("This PDF could not be opened. Please choose a valid PDF file.")
        except UnicodeDecodeError:
            st.error("This text file could not be read. Save it as UTF-8 and try again.")
        except Exception:
            # Avoid putting provider diagnostics or request data in the page.
            st.error("The analysis couldn't be completed. Please try again in a moment.")
