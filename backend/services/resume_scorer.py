import xml.etree.ElementTree as ET
from services.claude_client import claude
from models.prompts import RESUME_SCORER_SYSTEM, RESUME_SCORE_PROMPT
from models.schemas import (
    AnalyzeResponse, ScoringDimension, ScoringDimensions, KeywordGap, SeverityEnum
)


def score_resume(job_description: str, resume_text: str) -> AnalyzeResponse:
    """
    Score a resume against a job description using Claude.

    Uses temperature=0.1 for consistency — scoring should be deterministic.
    Parses structured XML response into typed Pydantic models.
    """
    prompt = RESUME_SCORE_PROMPT.format(
        job_description=job_description,
        resume_text=resume_text,
    )

    raw_response = claude.complete(
        user_message=prompt,
        system_prompt=RESUME_SCORER_SYSTEM,
        temperature=0.1,
    )

    return _parse_scoring_response(raw_response)


def _parse_scoring_response(raw: str) -> AnalyzeResponse:
    """
    Parse Claude's XML scoring response into an AnalyzeResponse.

    Wraps the response in a root tag before parsing to handle
    cases where Claude omits a top-level wrapper.
    """
    # Extract content within <scoring> tags
    start = raw.find("<scoring>")
    end = raw.find("</scoring>") + len("</scoring>")
    if start == -1 or end == -1:
        raise ValueError(f"Could not find <scoring> tags in response: {raw[:200]}")

    xml_str = raw[start:end]
    root = ET.fromstring(xml_str)

    def text(node, path, default=""):
        el = node.find(path)
        return el.text.strip() if el is not None and el.text else default

    def int_text(node, path, default=0):
        val = text(node, path, str(default))
        try:
            return int(val)
        except ValueError:
            return default

    def list_text(node, path):
        return [el.text.strip() for el in node.findall(path) if el.text]

    dims_node = root.find("dimensions")

    def parse_dim(tag: str) -> ScoringDimension:
        node = dims_node.find(tag)
        return ScoringDimension(
            score=int_text(node, "score", 50),
            rationale=text(node, "rationale", "No rationale provided."),
        )

    dimensions = ScoringDimensions(
        keyword_match=parse_dim("keyword_match"),
        transferable_skills=parse_dim("transferable_skills"),
        experience_depth=parse_dim("experience_depth"),
        red_flags=parse_dim("red_flags"),
    )

    missing_keywords = []
    for kw in root.findall("missing_keywords/keyword"):
        term = text(kw, "term")
        severity_raw = text(kw, "severity", "nice-to-have")
        try:
            severity = SeverityEnum(severity_raw)
        except ValueError:
            severity = SeverityEnum.nice_to_have
        reframe = text(kw, "reframe_suggestion", "No reframe available.")
        if term:
            missing_keywords.append(KeywordGap(
                term=term,
                severity=severity,
                reframe_suggestion=reframe,
            ))

    return AnalyzeResponse(
        overall_score=int_text(root, "overall_score", 50),
        dimensions=dimensions,
        matched_keywords=list_text(root, "matched_keywords/keyword"),
        missing_keywords=missing_keywords,
        strengths=list_text(root, "strengths/strength"),
        weaknesses=list_text(root, "weaknesses/weakness"),
        ats_risk_factors=list_text(root, "ats_risk_factors/risk"),
    )
