// Shared TypeScript types matching backend Pydantic schemas

export type Severity = "critical" | "important" | "nice-to-have";
export type Tone = "professional" | "conversational" | "confident";

export interface ScoringDimension {
  score: number;
  rationale: string;
}

export interface ScoringDimensions {
  keyword_match: ScoringDimension;
  transferable_skills: ScoringDimension;
  experience_depth: ScoringDimension;
  red_flags: ScoringDimension;
}

export interface KeywordGap {
  term: string;
  severity: Severity;
  reframe_suggestion: string;
}

export interface AnalyzeResponse {
  overall_score: number;
  dimensions: ScoringDimensions;
  matched_keywords: string[];
  missing_keywords: KeywordGap[];
  strengths: string[];
  weaknesses: string[];
  ats_risk_factors: string[];
}

export interface CoverLetterResponse {
  cover_letter: string;
  key_points_used: string[];
  gaps_addressed: string[];
  word_count: number;
}

export interface AnalyzeRequest {
  job_description: string;
  resume_text: string;
  target_role?: string;
}

export interface CoverLetterRequest {
  job_description: string;
  resume_text: string;
  company_name: string;
  tone: Tone;
}
