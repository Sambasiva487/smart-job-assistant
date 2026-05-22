# Prompt Engineering Notes

## Design philosophy

All prompts in this project follow three principles:

1. **Structured XML output** — Claude is instructed to respond in XML. This makes responses parseable without regex heuristics and fails loudly when the model deviates.

2. **Role priming** — System prompts establish a specific expert persona. "Senior technical recruiter with 15 years of experience" produces different (better) output than a generic assistant instruction.

3. **Temperature by task type** — Scoring uses `temperature=0.1` for consistency. Cover letter generation uses `temperature=0.7` for natural prose variation.

---

## Scoring prompt

### Why chain-of-thought before scoring?

The scoring prompt asks Claude to "reason through each dimension carefully" before outputting scores. This produces more accurate scores because it forces the model to surface evidence before committing to a number.

Without CoT:
> `<score>72</score>` — no reasoning, potentially arbitrary

With CoT:
> Claude identifies specific matched terms, counts years, notes gaps, then arrives at a score grounded in evidence.

### XML dimension structure

Each scoring dimension (keyword_match, transferable_skills, experience_depth, red_flags) gets its own score and rationale. This makes the output actionable — a low `keyword_match` score tells the user to update their skills section; a low `experience_depth` score is a different problem with a different solution.

---

## Cover letter prompt

### Why "do NOT open with I am excited to apply"?

Negative constraints work better than positive ones for stylistic instructions. Telling Claude what NOT to do eliminates the most common failure mode without over-constraining the output.

### Temperature 0.7 rationale

Cover letters need to sound like a real person. Temperature 0.0-0.2 produces technically correct but noticeably robotic prose. Temperature 0.7-0.8 produces natural variation while still following structural instructions.

### Grounding in resume text

The cover letter prompt includes the full resume text and explicitly instructs Claude to base all claims on it. This prevents hallucination of experience — a critical requirement given the professional and legal implications of resume fraud.

---

## Bullet improvement prompt

### The truthfulness constraint

The bullet improvement prompt includes three explicit constraints:
- "Keep all facts true"
- "Do not add experience that is not there"
- "Do not invent numbers"

And requires a `<truthfulness_note>` in the output confirming compliance. This creates a self-auditing loop — Claude must explicitly state that the improved bullet preserves accuracy.

---

## Parsing strategy

All XML parsing uses Python's `xml.etree.ElementTree`. Key decisions:

- **Wrap before parsing** — responses are extracted between known tags before being parsed, handling cases where Claude adds preamble text
- **Graceful defaults** — missing fields fall back to empty strings or defaults rather than raising exceptions
- **Fail loudly on structure** — if `<scoring>` tags are absent entirely, a `ValueError` is raised and surfaced to the API caller

---

## Known failure modes

| Failure | Cause | Mitigation |
|---|---|---|
| Malformed XML | Claude adds markdown fences around XML | Strip ` ```xml ``` ` before parsing |
| Score out of range | Model ignores 0-100 constraint | Clamp values in parser |
| Missing dimensions | Model omits a low-confidence dimension | Default to score=50 |
| Cover letter ignores tone | Tone instruction too weak | Add one-shot example for each tone |
