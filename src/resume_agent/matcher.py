from langchain_core.prompts import ChatPromptTemplate

from resume_agent.llm_connection import get_llm
from resume_agent.schemas import MatchAnalysis

ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a hiring match analyst. Compare structured job requirements against a resume (unstructured text) and return a structured MatchAnalysis.
Rules:
- Base every claim ONLY on the provided job requirements JSON and resume text.
- Do NOT invent skills, employers, or experience that are not supported by the resume.
- Treat must_have_skills as critical. nice_to_have_skills matter less.
- A skill counts as matched if the resume shows clear evidence (same tool/skill or a clear equivalent).
- Put unmatched must-have skills in missing_skills.
- matched_skills should mostly come from must_have_skills (and relevant nice-to-haves if clearly present).
- strengths: short bullet points of what fits well for this role.
- gaps: short bullet points of important weaknesses or missing must-haves.
- evidence: 3-6 SHORT quotes copied from the resume text (prefer exact phrases that appear in the resume).
- Resume text may be messy from PDF extraction (wrong order, broken lines). Still judge on content, not formatting.
Scoring guidance (match_score 0-100):
- Start from must-have coverage:
  - all must-haves matched → roughly 75-90 before adjustments
  - most must-haves matched → roughly 55-75
  - about half matched → roughly 35-55
  - few/none matched → roughly 0-35
- Add up to +10 if many nice-to-haves are present.
- Subtract if seniority/role fit in the JD is clearly mismatched with the resume.
- Keep score as an integer.
Verdict:
- strong: generally 75+ and most must-haves matched
- borderline: generally 45-74, mixed must-have coverage
- weak: generally under 45, or many critical must-haves missing
Be concise and specific.""",
        ),
    (
        "human",
        """Compare this candidate resume to the job requirements.
           Job requirements (JSON):
           {job_requirements}
           Resume text:
          {resume_text}
        """,
    ),
    ]
)

def MatchAnalysis_llm(resume_text:str,jd_structured_ouput:str) -> MatchAnalysis:
         llm = get_llm()
         structured_llm = llm.with_structured_output(MatchAnalysis)
         chain = ANALYSIS_PROMPT | structured_llm
         return chain.invoke({"job_requirements": jd_structured_ouput, "resume_text": resume_text})