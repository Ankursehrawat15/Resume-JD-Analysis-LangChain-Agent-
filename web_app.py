"""Web UI for the existing resume-agent workflow.

Run with: streamlit run web_app.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from resume_agent.jd_extractor import extract_jd
from resume_agent.config import LLM_MODEL
from resume_agent.loaders import InputError, load_resume
from resume_agent.matcher import MatchAnalysis_llm


st.set_page_config(
    page_title="Resume Match Workbench",
    page_icon="⌁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink:#17201d; --muted:#68736e; --paper:#f5f6f1; --line:#d8ded8; --accent:#d7ff62; }
    .stApp { background:var(--paper); color:var(--ink); }
    .block-container { max-width:1180px; padding:3.5rem 2rem 5rem; }
    h1,h2,h3,p,label,button { font-family:Manrope,sans-serif; }
    h1 { font-size:clamp(2.7rem,6vw,5.8rem)!important; line-height:.96!important; letter-spacing:-.07em; max-width:760px; }
    h2 { letter-spacing:-.04em; }
    .kicker { color:#54705b; font:500 .75rem 'DM Mono',monospace; letter-spacing:.12em; text-transform:uppercase; }
    .intro { color:var(--muted); font-size:1.06rem; max-width:540px; line-height:1.65; }
    .section-label { border-top:1px solid var(--line); padding-top:1.2rem; margin-top:2.2rem; font:500 .76rem 'DM Mono',monospace; letter-spacing:.1em; text-transform:uppercase; }
    [data-testid="stFileUploader"] section { border:1px dashed #9ba99f; background:#eef1ea; border-radius:12px; padding:.7rem; }
    [data-testid="stFileUploader"] button { background:#d7ff62!important; color:#17201d!important; border:0!important; font-weight:700!important; }
    [data-testid="stFileUploader"] button span { color:#17201d!important; }
    [data-testid="stFileUploader"] button:hover { background:#c7ef4d!important; color:#17201d!important; }
    [data-testid="stTextArea"] textarea { background:#ffffff!important; color:#17201d!important; caret-color:#17201d!important; border:1px solid #aeb9b0!important; }
    [data-testid="stTextArea"] textarea::placeholder { color:#68736e!important; opacity:1!important; }
    [data-testid="stTextArea"] label, [data-testid="stFileUploader"] label { color:#17201d!important; }
    [data-testid="stFileUploader"] small { color:#17201d!important; }
    .result-card { background:#17201d; color:#f5f6f1; border-radius:16px; padding:1.6rem; }
    .score { color:var(--accent); font-size:4.6rem; font-weight:800; letter-spacing:-.08em; line-height:1; }
    .pill { display:inline-block; border:1px solid #58655f; border-radius:99px; color:#d7ff62; padding:.35rem .7rem; font:500 .72rem 'DM Mono',monospace; text-transform:uppercase; }
    .hint { color:#68736e; font-size:.82rem; }
    .model-chip { display:inline-flex; align-items:center; gap:.5rem; border:1px solid #c3ccc4; border-radius:99px; padding:.45rem .7rem; color:#415249; background:#eef1ea; font:500 .75rem 'DM Mono',monospace; }
    .model-dot { width:.45rem; height:.45rem; border-radius:50%; background:#4e9b66; box-shadow:0 0 0 4px #d6e9d9; }
    .metric-strip { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem; margin-top:.8rem; }
    .metric { background:#eef1ea; border:1px solid #d8ded8; border-radius:12px; padding:.8rem 1rem; }
    .metric-label { color:#68736e; font:500 .68rem 'DM Mono',monospace; text-transform:uppercase; letter-spacing:.08em; }
    .metric-value { color:#17201d; font-size:1.2rem; font-weight:800; margin-top:.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="kicker">Resume agent / local analysis</div>', unsafe_allow_html=True)
st.title("See how the role fits the resume.")
st.markdown(
    '<p class="intro">Paste a job description, upload a PDF resume, and run the same local LangChain analysis from a focused web workbench.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="model-chip"><span class="model-dot"></span> ANALYSIS MODEL&nbsp;&nbsp; {LLM_MODEL}</div>',
    unsafe_allow_html=True,
)

def estimate_tokens(text: str) -> int:
    """Provider-neutral estimate; the exact count depends on the local model tokenizer."""
    return max(1, round(len(text) / 4))


def read_uploaded_resume(uploaded_file) -> object:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = Path(temp_file.name)
        return load_resume(temp_path)
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


input_jd, input_resume = st.columns(2, gap="large")
with input_jd:
    st.markdown('<div class="section-label">01 — Job description</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "Job description",
        height=280,
        placeholder="Paste the complete job description here…",
        label_visibility="collapsed",
    )
    if jd_text.strip():
        st.markdown(
            f'<div class="metric-strip"><div class="metric"><div class="metric-label">Characters</div><div class="metric-value">{len(jd_text):,}</div></div><div class="metric"><div class="metric-label">Est. input tokens</div><div class="metric-value">~{estimate_tokens(jd_text):,}</div></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="hint">Estimated at roughly 4 characters per token. Exact counts vary by tokenizer.</div>', unsafe_allow_html=True)

with input_resume:
    st.markdown('<div class="section-label">02 — Resume PDF</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader(
        "Upload resume PDF",
        type=["pdf"],
        help="PDF resumes only. The existing PDF loader extracts the text for matching.",
    )
    resume_document = None
    if resume_file is not None:
        try:
            resume_document = read_uploaded_resume(resume_file)
            st.markdown(
                f'<div class="metric-strip"><div class="metric"><div class="metric-label">Extracted characters</div><div class="metric-value">{len(resume_document.raw_text):,}</div></div><div class="metric"><div class="metric-label">Est. input tokens</div><div class="metric-value">~{estimate_tokens(resume_document.raw_text):,}</div></div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div class="hint">{resume_document.page_count or "—"} page(s) extracted. Token estimate uses the extracted text.</div>', unsafe_allow_html=True)
        except InputError as exc:
            st.error(str(exc))

st.markdown('<div class="section-label">03 — Analysis</div>', unsafe_allow_html=True)
ready = bool(jd_text.strip()) and resume_file is not None and resume_document is not None
if not ready:
    st.markdown('<div class="hint">Add both inputs to enable analysis.</div>', unsafe_allow_html=True)

if st.button("Analyze match", type="primary", disabled=not ready, use_container_width=False):
    try:
        with st.status("Analysis in progress", expanded=True) as status:
            status.write(f"Using local model: `{LLM_MODEL}`")
            status.write("Reading the uploaded resume…")
            status.write(f"Resume context: ~{estimate_tokens(resume_document.raw_text):,} estimated tokens")
            status.write("Extracting structured requirements from the job description…")
            requirements = extract_jd(jd_text.strip())
            status.write("Comparing resume evidence against the extracted requirements…")
            analysis = MatchAnalysis_llm(
                resume_document.raw_text,
                requirements.model_dump_json(indent=2),
            )
            status.update(label="Analysis complete", state="complete", expanded=False)
        st.session_state["analysis"] = analysis.model_dump()
        st.session_state["requirements"] = requirements.model_dump()
    except InputError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")


if "analysis" in st.session_state:
    result = st.session_state["analysis"]
    requirements = st.session_state.get("requirements", {})
    st.markdown('<div class="section-label">Result</div>', unsafe_allow_html=True)
    st.subheader(f'{requirements.get("role", "Role")} — match signal')
    result_metrics = st.columns(4)
    with result_metrics[0]:
        st.metric("Match score", f'{result["match_score"]}/100')
    with result_metrics[1]:
        st.metric("Must-have skills", len(requirements.get("must_have_skills", [])))
    with result_metrics[2]:
        st.metric("Matched", len(result["matched_skills"]))
    with result_metrics[3]:
        st.metric("Missing", len(result["missing_skills"]))
    st.progress(result["match_score"] / 100, text=f'{result["match_score"]}% match confidence')
    left, right = st.columns([1, 2], gap="large")
    with left:
        st.markdown(
            f'<div class="result-card"><div class="kicker">Match score</div><div class="score">{result["match_score"]}</div><div class="pill">{result["verdict"]}</div><p style="color:#b9c2bc;margin-top:1rem">{requirements.get("role", "Role analysis")}</p></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.subheader("What the evidence says")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Matched skills**")
            st.write(" · ".join(result["matched_skills"]) or "No matched skills returned.")
            st.markdown("**Strengths**")
            for item in result["strengths"]:
                st.markdown(f"- {item}")
        with col_b:
            st.markdown("**Missing skills**")
            st.write(" · ".join(result["missing_skills"]) or "No missing must-have skills returned.")
            st.markdown("**Gaps**")
            for item in result["gaps"]:
                st.markdown(f"- {item}")
        with st.expander("Resume evidence"):
            for quote in result["evidence"]:
                st.markdown(f'> {quote}')
        st.download_button(
            "Download JSON",
            data=json.dumps({"requirements": requirements, "analysis": result}, indent=2),
            file_name="resume-match-result.json",
            mime="application/json",
        )
