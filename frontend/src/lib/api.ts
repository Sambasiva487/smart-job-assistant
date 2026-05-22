import type {
  AnalyzeRequest,
  AnalyzeResponse,
  CoverLetterRequest,
  CoverLetterResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiRequest<T>(
  path: string,
  body: unknown
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail ?? `Request failed: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function analyzeResume(
  request: AnalyzeRequest
): Promise<AnalyzeResponse> {
  return apiRequest<AnalyzeResponse>("/analyze/", request);
}

export async function generateCoverLetter(
  request: CoverLetterRequest
): Promise<CoverLetterResponse> {
  return apiRequest<CoverLetterResponse>("/generate/cover-letter", request);
}
