"""
Unit tests for the resume scorer service.

Tests XML parsing logic in isolation — no API calls made.
"""
import pytest
from services.resume_scorer import _parse_scoring_response


SAMPLE_SCORING_XML = """
<scoring>
  <overall_score>78</overall_score>
  
  <dimensions>
    <keyword_match>
      <score>85</score>
      <rationale>Strong match on TypeScript, Python, REST APIs, and CI/CD.</rationale>
    </keyword_match>
    <transferable_skills>
      <score>72</score>
      <rationale>Backend architecture maps well but lacks React-specific experience.</rationale>
    </transferable_skills>
    <experience_depth>
      <score>70</score>
      <rationale>3 years total but role requires 5 years React specifically.</rationale>
    </experience_depth>
    <red_flags>
      <score>90</score>
      <rationale>No significant red flags. Location mismatch is minor.</rationale>
    </red_flags>
  </dimensions>

  <matched_keywords>
    <keyword>TypeScript</keyword>
    <keyword>Python</keyword>
    <keyword>REST APIs</keyword>
    <keyword>CI/CD</keyword>
    <keyword>PostgreSQL</keyword>
  </matched_keywords>

  <missing_keywords>
    <keyword>
      <term>React</term>
      <severity>critical</severity>
      <reframe_suggestion>Surface component architecture work from Sharecase as React-aligned patterns.</reframe_suggestion>
    </keyword>
    <keyword>
      <term>GraphQL</term>
      <severity>important</severity>
      <reframe_suggestion>Add GraphQL to skills if any API integration work involved it.</reframe_suggestion>
    </keyword>
  </missing_keywords>

  <strengths>
    <strength>Strong Python and TypeScript fundamentals across multiple roles.</strength>
    <strength>Live production experience at Sharecase demonstrates real shipping capability.</strength>
  </strengths>

  <weaknesses>
    <weakness>React not explicitly named in any role — critical gap for front-end roles.</weakness>
  </weaknesses>

  <ats_risk_factors>
    <risk>Year count for React may fail ATS threshold filters.</risk>
    <risk>Location in Savannah, GA vs. remote/Chicago roles.</risk>
  </ats_risk_factors>
</scoring>
"""


def test_parse_overall_score():
    result = _parse_scoring_response(SAMPLE_SCORING_XML)
    assert result.overall_score == 78


def test_parse_dimensions():
    result = _parse_scoring_response(SAMPLE_SCORING_XML)
    assert result.dimensions.keyword_match.score == 85
    assert result.dimensions.transferable_skills.score == 72
    assert result.dimensions.experience_depth.score == 70
    assert result.dimensions.red_flags.score == 90


def test_parse_matched_keywords():
    result = _parse_scoring_response(SAMPLE_SCORING_XML)
    assert "TypeScript" in result.matched_keywords
    assert "Python" in result.matched_keywords
    assert len(result.matched_keywords) == 5


def test_parse_missing_keywords():
    result = _parse_scoring_response(SAMPLE_SCORING_XML)
    assert len(result.missing_keywords) == 2
    react_gap = next(k for k in result.missing_keywords if k.term == "React")
    assert react_gap.severity == "critical"
    assert "Sharecase" in react_gap.reframe_suggestion


def test_parse_strengths_and_weaknesses():
    result = _parse_scoring_response(SAMPLE_SCORING_XML)
    assert len(result.strengths) == 2
    assert len(result.weaknesses) == 1


def test_parse_ats_risk_factors():
    result = _parse_scoring_response(SAMPLE_SCORING_XML)
    assert len(result.ats_risk_factors) == 2


def test_malformed_xml_raises():
    with pytest.raises((ValueError, Exception)):
        _parse_scoring_response("This is not XML and has no scoring tags")
