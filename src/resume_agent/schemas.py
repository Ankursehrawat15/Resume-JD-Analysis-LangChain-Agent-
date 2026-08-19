form enum import Enum 
from pydanctic import BaseModel, field



class verdict(str, Enum):
    strong = "strong"
    borderline = "borderline"
    weak = "weak"

class JobRequirement(BaseModel):

    role: str = Field(description="Job title / role name")
    seniority: str = Field(description="eg. junior, mid, senior,staff")
    must_have_skills: list[str] = Field(
        default_factory=list,
        description="Required skills explicitly stated in the JD",
    )
    nice_to_have_skills: list[str] = Field(
        default_factory=list,
        description="Optional / preferred skills from the JD",
    )
    notes: str = Field(
        default="",
        description="Other Important requirements not captured as skills"
    )

    # what is default facotry for ? diff between default and default facotry 
    # what does None does in python ?

    class ResumeDocument(BaseModel):
        # raw text from resume
        raw_text: str = Field(description="Full extracted resume text")
        source_path: str = Field(description="Path to the source file")
        page_count: int | None = Field(
            default = None,
            description="PDF page count if know; None for .txt",
        )
    
    class MatchAnalysis(BaseModel):

        match_score: int = Field(
            ge=0,
            le=100,
            description="Overall match score from 0 to 100",
        )

        matched_skills: list[str] = Field(default_factory=list)
        missing_skills: list[str] = Field(default_factory=list)
        strenths: list[str] = Field(default_factory=list)
        gaps: list[str] = Field(default_factory=list)
        verdict: Verdict = Field(description="strong | borderline | weak")
        evidence: list[str] = Field(
            default_factory=list,
            description="Short quotes from the resume that supports the analysis"
            
        )