from langchain_core.prompts import ChatPromptTemplate

from resume_agent.llm_connection import get_llm
from resume_agent.schemas import JobRequirements


JD_EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    
    (
        "system",
        """You Analyize and extract structured job requirements from a job description. 

        Rules:
        - Extract only information explicitly stated in the Job Description.
        - Do Not invent skills, tools or requirements.
        - Put required/mandatory skills in must have skills.
        - Put preferred/optional/nice-to-have skills in nice_to_have_skills.
        - Use short skill names (eg: "Playwright", "Docker", "JIRA").
        - If seniority is unclear, set seniority to "unspecified".
        - Put years of experience, education, employement type, and responsibilities in notes if they are not skills.""",

    ),
    (
        "human",
        "Extract requirement from this job description:\n\n{jd_text}",
    ),

])

def extract_jd(jd_text:str) -> JobRequirements:
    llm = get_llm()
    structured_llm = llm.with_structured_output(JobRequirements)
    chain = JD_EXTRACT_PROMPT | structured_llm
    return chain.invoke({"jd_text": jd_text})