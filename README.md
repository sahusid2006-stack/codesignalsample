# Prompt Engineering Assessment Simulator (Web App)

A lightweight CodeSignal-style **web app** for prompt engineering drills.
You edit only prompt text files, then click buttons to run visible tests and full grading.

## What this is
- A local web app with exercise navigation (Level 1 → Level 4 style).
- Uses the Claude API (default model: Haiku) with deterministic settings (`temperature=0`, `top_p=1`).
- Includes visible and hidden pytest grading.
- Includes a cache to speed up repeated runs.

## What you can edit
Only files under:
- `src/prompts/system_prompt.txt`
- `src/prompts/task1_prompt.txt`
- `src/prompts/task2_prompt.txt`
- `src/prompts/task3_prompt.txt`

Everything else is grader/app infrastructure.

## Requirements
- Python 3.11+

Install:

```bash
python -m pip install -r requirements.txt
```

## Environment variables
- `ANTHROPIC_API_KEY` (required)
- `MODEL` (optional, default: `claude-3-5-haiku-latest`)
- `CACHE` (optional, default: `1`; set `0` to disable)
- `PORT` (optional, default: `8000`)

## Run as a local app (recommended)

```bash
python app.py
```

Open:
- `http://localhost:8000`

You will get:
- Home page with levels/exercises
- Exercise page with prompt editor
- Buttons for:
  - Save Prompt
  - Run This Exercise
  - Run Visible Tests
  - Submit / Full Grade

## Terminal fallback commands

Visible tests:

```bash
pytest -q
```

Full grade (guard + visible + hidden):

```bash
python scripts/grade.py
```

Timer helper:

```bash
python scripts/timed_run.py --minutes 75
```

## Notes on exercises
The included exercises are **Anthropic-style practice exercises** inspired by common prompt-assessment patterns (not official Anthropic exam content).

## Determinism and cache
- LLM calls run with deterministic parameters.
- Responses are cached at `.cache/responses.json`.
