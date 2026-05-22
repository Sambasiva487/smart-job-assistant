from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ToneEnum(str, Enum):
    professional = "professional"
    conversational = "conversational"
    confident = "confident"


class SeverityEnum(str, Enum):
    critical = "critical"
    important = "important"
    nice_to_have = "nice-to-have"


# ─── Request Models ───────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    job_description: str = Field(..., min_length=100, description="Full job description text")
    resume_text: str = Field(..., min_length=100, description="Full resume text")
    target_role: Optional[str] = Field(None, description="Optional role title override")


class CoverLetterRequest(BaseModel):
    job_description: str = Field(..., min_length=100)
    resume_text: str = Field(..., min_length=100)
    company_name: str = Field(..., min_length=1)
    tone: ToneEnum = Field(ToneEnum.professional)


class BulletImprovementRequest(BaseModel):
    bullet: str = Field(..., description="Original resume bullet point")
    jd_excerpt: str = Field(..., description="Relevant excerpt from job description")


# ─── Response Models ──────────────────────────────────────────────────────────

class ScoringDimension(BaseModel):
    score: int = Field(..., ge=0, le=100)
    rationale: str


class ScoringDimensions(BaseModel):
    keyword_match: ScoringDimension
    transferable_skills: ScoringDimension
    experience_depth: ScoringDimension
    red_flags: ScoringDimension


class KeywordGap(BaseModel):
    term: str
    severity: SeverityEnum
    reframe_suggestion: str


class AnalyzeResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    dimensions: ScoringDimensions
    matched_keywords: list[str]
    missing_keywords: list[KeywordGap]
    strengths: list[str]
    weaknesses: list[str]
    ats_risk_factors: list[str]


class CoverLetterResponse(BaseModel):
    cover_letter: str
    key_points_used: list[str]
    gaps_addressed: list[str]
    word_count: int


class BulletImprovementResponse(BaseModel):
    original: str
    improved: str
    changes_made: str
    truthfulness_note: str
