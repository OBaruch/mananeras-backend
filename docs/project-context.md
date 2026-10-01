# Project Context

This document reconstructs where `mananeras-backend` came from, using only evidence found in the repository and its git history. Each statement is tagged:

- **Confirmed**: directly supported by a file or commit.
- **Inferred**: a reasonable deduction from the available material.
- **Unknown**: not determinable from the repository.

[← Back to README](../README.md)

---

## 1. Classification

**Project origin: Personal Project — Proof of Concept / MVP** *(Inferred)*

| Evidence | Source | Level |
|----------|--------|-------|
| The service calls itself "MVP Mañaneras" | `src/main.py` (`home()` response), commit `6340cf8` "Primer commit del MVP Mañaneras" | Confirmed |
| Single author working in bursts late at night over three days | git history, 22–24 May 2025 | Confirmed |
| Deployed to a hobby-friendly PaaS (Railway) | commit messages `5064a8e`, `4f3b203`, `2012f5c`, `7c96ab6`; deleted `railway.toml` | Confirmed |
| No course name, university, rubric, assignment PDF/Word, or report exists | whole repository | Confirmed (absence) |
| Therefore not classified as Academic/Coursework | — | Inferred |

Because the repository contains no document that states the motivation, the *motivation* itself remains **Unknown**. What follows describes what the code does and the most reasonable reading of why.

## 2. Domain

- *"Mañaneras"* is the colloquial Mexican Spanish name for the daily morning press conferences held by the President of Mexico. *(General domain knowledge; the repository does not define the term.)*
- The code hard-codes the channel `https://www.youtube.com/@ClaudiaSheinbaumP/videos` as the source for the "latest video" flow (`src/main.py`). *(Confirmed)*
- Taken together, the project's target content is the President's daily conferences as published on that YouTube channel. *(Inferred)*
- All prompts, identifiers, error messages and the Whisper language (`language="es"`) are Spanish. *(Confirmed)*

## 3. Goal (as reconstructed)

Turn each long press-conference video into a compact, structured record: a transcript, a summary, bullet points, a discourse type, the main topics, a policy category and a sentiment. The record is then exposed through an API that another application could consume. See [`intent.md`](intent.md). *(Inferred from code.)*

The `-backend` suffix of the repository name suggests a separate client/frontend was planned or existed. No such code or reference exists here. *(Unknown)*

## 4. Timeline

All times are UTC-6 (the author's local time as recorded by git).

| Date / time | Commit | What happened |
|-------------|--------|---------------|
| 22 May 2025 22:30 | `57afbc8` | Repository created on GitHub (`LICENSE` Apache-2.0, Python `.gitignore`, README containing only `# mananeras-backend`) |
| 22:33 | `6340cf8` | First FastAPI app: `GET /` → "¡MVP Mañaneras está vivo!", `Procfile`, `requirements.txt` |
| 22:39 | `e61b7b5` | PostgreSQL connection and `Video` / `Resumen` models |
| 22:53 | `af22e79` | `POST`/`GET /api/videos`, `crud.py`, `schemas.py` |
| 23:00 | `0c0c948` | `POST`/`GET /api/videos/{id}/resumen` |
| 23:20 | `8e2aad3` | `utils/transcriber.py`: download, Whisper transcription, detection of the channel's latest video |
| 23:27–23:39 | `dd90513`, `5064a8e`, `4f3b203`, `2012f5c` | Dependencies for Whisper; Railway build fixes (Git-installed Whisper, Python 3.10, Pydantic 1, Nixpacks) |
| 23:56 | `2318cc6` | Missing `utils/__init__.py` added |
| 23 May 00:17–00:52 | `c3fed16`, `9c51b5d`, `7c96ab6` | More build fixes; `railway.toml` removed in favor of a `Dockerfile` on Python 3.10 |
| 01:15 | `58c88a1` | Avoid duplicate summaries for the latest video; better transcription error handling |
| 01:31 | `db48f12` | Semantic fields added (bullets, discourse type, topics, category, sentiment) via FLAN-T5 |
| 01:40 | `fa30b83` | `transformers` and `torch` added to requirements |
| 08:04 UTC | `940f9d7` | README rewritten by an automated documentation bot; merged by the author via PR #1 (`ed15c5a`) |
| 24 May 13:18 | `d4fefe2` | Audio written to an absolute path in `/tmp/audio_files` and existence check added |
| 21:55 | `17319a1` | Custom `YtdlLogger` that captures `yt-dlp` logs into error messages. **Last change to the code.** |

The last two commits focus entirely on diagnosing audio download failures. Whether the download then worked reliably in production is **Unknown**.

## 5. Deployment history

The repository shows three successive deployment approaches *(Confirmed)*:

1. **Procfile** (from the first commit): `web: uvicorn main:app --host 0.0.0.0 --port 8000`.
2. **`railway.toml` with Nixpacks** (commits `4f3b203` → `9c51b5d`, later deleted). Its last version was:

   ```toml
   [build]
   builder = "NIXPACKS"

   [variables]
   PYTHON_VERSION = "3.12"
   ```

   Earlier revisions pinned `PYTHON_VERSION = "3.10"`, and the first used `nixpacksPlan = true` under `[build]` and `[env]`.
3. **Dockerfile** on `python:3.10-slim` with `ffmpeg`, `git` and `gcc` (commit `7c96ab6`), which is the final state.

The deleted `railway.toml` is not restored as a file because it is no longer part of the working configuration. Its contents are preserved above and in git history.

## 6. Pre-existing documentation and contradictions

The README that existed before this reorganization is preserved at [`original/README.md`](original/README.md). It was **not written by the author**: it was generated by an automated documentation bot (commit `940f9d7`) and merged by the author. The original author-written README contained only the title `# mananeras-backend` (commit `57afbc8`).

Points where that README disagrees with the code:

| Previous README says | Code actually shows |
|----------------------|---------------------|
| Procfile is `uvicorn main:app --host 0.0.0.0 --port $PORT` | `src/Procfile` uses the fixed port `8000` |
| "Ensure you have FFmpeg installed on your system" | True for local runs, but the `Dockerfile` already installs `ffmpeg` |
| Deployment on Railway is "presumed" | Railway usage is confirmed by commit messages and the deleted `railway.toml` |
| Analysis uses FLAN-T5 for "Spanish" NLP | The prompts are Spanish, but `google/flan-t5-base` is primarily trained on English, so output quality in Spanish is uncertain (see [`possible-improvements.md`](possible-improvements.md)) |

## 7. What is not in the repository

- No PDFs, Word documents, slides, images, diagrams, datasets, notebooks or sample outputs. *(Confirmed)*
- No tests, migrations, CI configuration or `.env` example. *(Confirmed)*
- No record of which database instance was used or whether the service is still deployed. *(Unknown)*
