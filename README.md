# smart-job-assistant

An AI-powered job application tool built on the Anthropic Claude API. Paste a job description and your resume — get back a structured fit analysis, ATS keyword gap report, bullet-by-bullet improvement suggestions, and a tailored cover letter draft.

Built with Python (FastAPI backend), TypeScript (Next.js frontend), and Claude claude-sonnet-4-20250514.

---

## What it does

- **JD Parser** — Extracts required skills, preferred qualifications, seniority signals, and company culture cues from any job description using Claude
- **Resume Scorer** — Scores your resume against the JD across four dimensions: direct keyword match, transferable skills, experience depth, and red flags
- **ATS Gap Report** — Identifies missing keywords and suggests truthful reframings to close gaps
- **Cover Letter Generator** — Produces a tailored, role-specific cover letter draft grounded in your actual experience
- **Prompt Engineering Layer** — Structured multi-turn prompts with XML output formatting for reliable, parseable LLM responses

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude API (claude-sonnet-4-20250514) |
| Backend | Python 3.11+, FastAPI, Pydantic |
| Frontend | TypeScript, Next.js 14, Tailwind CSS |
| Database | PostgreSQL (via Supabase) |
| Auth | Supabase Auth |
| Deployment | Vercel (frontend), AWS Lambda (backend) |
| CI/CD | GitHub Actions |

---

## Project structure

```
smart-job-assistant/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── routers/
│   │   ├── analyze.py       # /analyze endpoint — JD + resume scoring
│   │   └── generate.py      # /generate endpoint — cover letter
│   ├── services/
│   │   ├── claude_client.py # Anthropic API wrapper
│   │   ├── jd_parser.py     # JD extraction logic
│   │   ├── resume_scorer.py # Scoring engine
│   │   └── cover_letter.py  # Cover letter generation
│   ├── models/
│   │   ├── schemas.py       # Pydantic request/response models
│   │   └── prompts.py       # Prompt templates
│   ├── db/
│   │   └── supabase.py      # Supabase client + queries
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx     # Landing / input page
│   │   │   ├── results/
│   │   │   │   └── page.tsx # Results dashboard
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── JobInput.tsx       # JD + resume paste form
│   │   │   ├── ScoreCard.tsx      # Fit score display
│   │   │   ├── GapReport.tsx      # ATS keyword gaps
│   │   │   └── CoverLetter.tsx    # Generated cover letter
│   │   ├── lib/
│   │   │   ├── api.ts       # Backend API calls
│   │   │   └── types.ts     # Shared TypeScript types
│   │   └── styles/
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
├── docs/
│   ├── architecture.md      # System design decisions
│   ├── prompts.md           # Prompt engineering notes
│   └── api.md               # API reference
└── README.md
```

---

## Quick start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key
- Supabase project (optional — falls back to in-memory for local dev)

### Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

uvicorn main:app --reload
# API running at http://localhost:8000
```

### Frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Add NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
# App running at http://localhost:3000
```

---

## API reference

### POST /analyze

Analyzes a job description against a resume.

**Request:**
```json
{
  "job_description": "string",
  "resume_text": "string",
  "target_role": "string (optional)"
}
```

**Response:**
```json
{
  "overall_score": 82,
  "dimensions": {
    "keyword_match": 88,
    "transferable_skills": 79,
    "experience_depth": 75,
    "red_flags": 0
  },
  "matched_keywords": ["TypeScript", "REST APIs", "CI/CD"],
  "missing_keywords": ["GraphQL", "Docker", "Kubernetes"],
  "gap_analysis": [
    {
      "keyword": "GraphQL",
      "severity": "medium",
      "reframe_suggestion": "Surface API integration experience..."
    }
  ],
  "strengths": ["string"],
  "weaknesses": ["string"]
}
```

### POST /generate/cover-letter

Generates a tailored cover letter.

**Request:**
```json
{
  "job_description": "string",
  "resume_text": "string",
  "company_name": "string",
  "tone": "professional | conversational | confident"
}
```

**Response:**
```json
{
  "cover_letter": "string",
  "key_points_used": ["string"],
  "gaps_addressed": ["string"],
  "word_count": 320
}
```

---

## Prompt engineering approach

This project uses structured XML prompting for reliable, parseable LLM output. See `docs/prompts.md` for the full prompt design rationale.

Key techniques used:
- **Role priming** — system prompt establishes Claude as a senior technical recruiter with ATS expertise
- **XML output formatting** — all responses use structured XML tags for deterministic parsing
- **Chain-of-thought extraction** — JD parsing uses step-by-step reasoning before scoring
- **Few-shot examples** — cover letter generation includes one-shot example for tone calibration
- **Temperature control** — scoring uses temp=0.1 for consistency; cover letter uses temp=0.7 for natural prose

---

## CI/CD pipeline

GitHub Actions runs on every push to `main` and `dev` branches:

- Python linting (ruff)
- Type checking (mypy)
- Unit tests (pytest)
- TypeScript type checking (tsc)
- Frontend build validation (next build)

See `.github/workflows/ci.yml` for full configuration.

---

## Database schema (Supabase / PostgreSQL)

```sql
-- Stores analysis sessions
CREATE TABLE analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  job_description TEXT NOT NULL,
  resume_text TEXT NOT NULL,
  overall_score INTEGER,
  result_json JSONB,
  user_id UUID REFERENCES auth.users(id)
);

-- Stores generated cover letters
CREATE TABLE cover_letters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID REFERENCES analyses(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  content TEXT NOT NULL,
  company_name TEXT,
  tone TEXT
);
```

---

## Contributing

PRs welcome. Open an issue first for significant changes.

---

## License

MIT
"# smart-job-assistant" 
