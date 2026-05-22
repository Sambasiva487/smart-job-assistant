from fastapi import APIRouter, HTTPException
from models.schemas import AnalyzeRequest, AnalyzeResponse, BulletImprovementRequest, BulletImprovementResponse
from services.resume_scorer import score_resume
from services.claude_client import claude
from models.prompts import RESUME_SCORER_SYSTEM, BULLET_IMPROVEMENT_PROMPT
import xml.etree.ElementTree as ET

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    """
    Analyze a resume against a job description.

    Returns a structured fit score with keyword gaps, strengths,
    weaknesses, and ATS risk factors.
    """
    try:
        result = score_resume(
            job_description=request.job_description,
            resume_text=request.resume_text,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse LLM response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/improve-bullet", response_model=BulletImprovementResponse)
async def improve_bullet(request: BulletImprovementRequest):
    """
    Improve a single resume bullet point to better match a job description.
    Preserves factual accuracy — never fabricates experience.
    """
    prompt = BULLET_IMPROVEMENT_PROMPT.format(
        bullet=request.bullet,
        jd_excerpt=request.jd_excerpt,
    )

    try:
        raw = claude.complete(
            user_message=prompt,
            system_prompt=RESUME_SCORER_SYSTEM,
            temperature=0.2,
        )

        def extract(tag):
            start = raw.find(f"<{tag}>")
            end = raw.find(f"</{tag}>")
            if start == -1 or end == -1:
                return ""
            return raw[start + len(f"<{tag}>"):end].strip()

        return BulletImprovementResponse(
            original=request.bullet,
            improved=extract("improved_bullet"),
            changes_made=extract("changes_made"),
            truthfulness_note=extract("truthfulness_note"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bullet improvement failed: {str(e)}")
