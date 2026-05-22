from fastapi import APIRouter, HTTPException
from models.schemas import CoverLetterRequest, CoverLetterResponse
from services.cover_letter import generate_cover_letter

router = APIRouter()


@router.post("/cover-letter", response_model=CoverLetterResponse)
async def create_cover_letter(request: CoverLetterRequest):
    """
    Generate a tailored cover letter.

    Uses Claude with temperature=0.7 for natural prose.
    Grounds all content in the provided resume — never fabricates.
    """
    try:
        result = generate_cover_letter(
            job_description=request.job_description,
            resume_text=request.resume_text,
            company_name=request.company_name,
            tone=request.tone.value,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")
