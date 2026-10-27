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



def score_card(title, score):
    if score >= 80:
        bg_color = "#163E31"
        text_color = "#A8F0C3"
        status = "Excellent"
    elif score >= 60:
        bg_color = "#4D3717"
        text_color = "#FFE0A0"
        status = "Good"
    else:
        bg_color = "#512B35"
        text_color = "#FFB5C0"
        status = "Needs improvement"

    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            min-height: 150px;
        ">
            <p style="color: {text_color}; margin: 0; font-size: 14px;">
                {title}
            </p>
            <h1 style="color: white; margin: 12px 0; font-size: 50px;">
                {score}%
            </h1>
            <p style="color: {text_color}; margin: 0; font-size: 13px;">
                {status}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )



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

    job_description = st.text_area(
        "Paste the job description",
        placeholder= "Paste the job requirements, responsibilities, and qualifications here...",
        height=180,
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
                    feedback = analyze_resume(resume_text, job_role, job_description)

                if isinstance(feedback, dict) and feedback:
                    st.success("Your review is ready", icon=":material/check_circle:")
                    st.header("Resume feedback", icon=":material/rate_review:")
                    st.caption(
                        "Scores are AI-generated estimates, not official ATS results."
                    )

                    col1, col2 = st.columns(2)

                    with col1 :
                        score_card(
                            "Estimated Job Match",
                            feedback["match_score"],
                        )

                    with col2:
                        score_card(
                            "Estimated ATS Readiness",
                            feedback["ats_readiness_score"],
                        )

                    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

                    with st.container(border=True):
                        
                        st.subheader("Overall Summary")
                        st.write(feedback["summary"])

                        st.subheader("Matched Skills")
                        for skill in feedback["matched_skills"]:
                            st.write(f"✅ {skill}")

                        st.subheader("Skills Not Evident in Resume")
                        for skill in feedback["missing_skills"]:
                            st.write(f"⚠️ {skill}")

                        st.subheader("ATS Readiness Issues")
                        for issue in feedback["ats_issues"]:
                            st.write(f"• {issue}")

                        st.subheader("Suggested Bullet Improvements")
                        for suggestion in feedback["bullet_improvements"]:
                            st.write(f"• {suggestion}")

                        st.subheader("Top Priority Actions")
                        for index, action in enumerate(
                            feedback["priority_actions"], start=1
                        ):
                            st.write(f"{index}. {action}")
                    
                else:
                    st.warning("The analysis returned no feedback. Please try again.")
        except PyPDF2.errors.PdfReadError:
            st.error("This PDF could not be opened. Please choose a valid PDF file.")
        except UnicodeDecodeError:
            st.error("This text file could not be read. Save it as UTF-8 and try again.")
        except Exception as e:
            # Avoid putting provider diagnostics or request data in the page. e:
            st.error(f"Analysis failed: {type(e).__name__}: {e}")
