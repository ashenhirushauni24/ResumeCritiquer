from __future__ import annotations

import io
import os

import PyPDF2
import streamlit as st
from dotenv import load_dotenv

from resumecritiquer.ai_analyzer import analyze_resume

MAX_FILE_SIZE = 5*1024*1024 #5MB

load_dotenv()

st.set_page_config(
    page_title="Resume Studio | AI Resume Critiquer",
    page_icon=":material/description:",
    layout="centered",
)


def validate_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return False, "Please upload a resume."

    if uploaded_file.size == 0:
        return False, "The uploaded file is empty."

    if uploaded_file.size > MAX_FILE_SIZE:
        return False, "File size must not exceed 5 MB."

    filename = uploaded_file.name.lower()

    if not filename.endswith((".pdf", ".txt")):
        return False, "Only PDF and TXT files are supported."

    return True, ""


def extract_text_from_pdf(pdf_file: io.BytesIO) -> str:
    """Read selectable text from every page in an uploaded PDF."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    if pdf_reader.is_encrypted:
        raise ValueError("Password-protected PDFs are not supported.")

    text = "\n".join(
        page.extract_text() or ""
        for page in pdf_reader.pages
    )

    if not text.strip():
        raise ValueError(
            "No readable text found. If this is a scanned PDF, "
            "try a text-based copy."
        )

    return text


def extract_text_from_file(uploaded_file) -> str:
    """Extract text from PDF or UTF-8 TXT files."""
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(io.BytesIO(file_bytes))

    if filename.endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(
                "Save your text file using UTF-8 encoding."
            ) from exc

        if not text.strip():
            raise ValueError("The text file contains no readable text.")

        return text

    raise ValueError("Only PDF and TXT files are supported.")



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
        max_upload_size=5,
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
    is_valid, error_message = validate_uploaded_file(uploaded_file)

    if not is_valid:
        st.warning(
            error_message,
            icon=":material/upload_file:",
        )
    elif not os.getenv("GOOGLE_API_KEY"):
        st.error(
            "Gemini is not configured yet. Add GOOGLE_API_KEY to your local environment settings.",
            icon=":material/key_off:",
        )
    else:
        try:
            resume_text = extract_text_from_file(uploaded_file)

            with st.spinner("Reviewing your resume…"):
                feedback = analyze_resume(
                    resume_text,
                    job_role,
                    job_description,
                )

                required_fields = {
                    "match_score",
                    "ats_readiness_score",
                    "summary",
                    "matched_skills",
                    "missing_skills",
                    "ats_issues",
                    "bullet_improvements",
                    "priority_actions",
                }

                if (
                    isinstance(feedback, dict)
                    and required_fields.issubset(feedback.keys())
                    and type(feedback["match_score"]) is int
                    and 0 <= feedback["match_score"] <= 100
                    and type(feedback["ats_readiness_score"]) is int
                    and 0 <= feedback["ats_readiness_score"] <= 100
                ):
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
        except ValueError as error:
            st.warning(str(error))

        except PyPDF2.errors.PdfReadError:
            st.error(
                "This PDF could not be read. Please upload a valid PDF."
            )

        except Exception:
            st.error(
                "Analysis failed. Please try again later."
            )
