import xml.etree.ElementTree as ET
from services.claude_client import claude
from models.prompts import COVER_LETTER_SYSTEM, COVER_LETTER_PROMPT
from models.schemas import CoverLetterResponse


def generate_cover_letter(
    job_description: str,
    resume_text: str,
    company_name: str,
    tone: str = "professional",
) -> CoverLetterResponse:
    """
    Generate a tailored cover letter using Claude.

    Uses temperature=0.7 for natural, non-template-sounding prose.
    """
    prompt = COVER_LETTER_PROMPT.format(
        job_description=job_description,
        resume_text=resume_text,
        company_name=company_name,
        tone=tone,
    )

    raw_response = claude.complete(
        user_message=prompt,
        system_prompt=COVER_LETTER_SYSTEM,
        temperature=0.7,
    )

    return _parse_cover_letter_response(raw_response)


def _parse_cover_letter_response(raw: str) -> CoverLetterResponse:
    """Parse Claude's XML cover letter response."""
    def extract_tag(tag: str) -> str:
        start = raw.find(f"<{tag}>")
        end = raw.find(f"</{tag}>")
        if start == -1 or end == -1:
            return ""
        return raw[start + len(f"<{tag}>"):end].strip()

    def extract_list(tag: str, item_tag: str) -> list[str]:
        block = extract_tag(tag)
        if not block:
            return []
        items = []
        search = f"<{item_tag}>"
        close = f"</{item_tag}>"
        pos = 0
        while True:
            start = block.find(search, pos)
            if start == -1:
                break
            end = block.find(close, start)
            if end == -1:
                break
            items.append(block[start + len(search):end].strip())
            pos = end + len(close)
        return items

    cover_letter = extract_tag("cover_letter")
    key_points = extract_list("key_points_used", "point")
    gaps = extract_list("gaps_addressed", "gap")
    word_count = len(cover_letter.split()) if cover_letter else 0

    return CoverLetterResponse(
        cover_letter=cover_letter,
        key_points_used=key_points,
        gaps_addressed=gaps,
        word_count=word_count,
    )
