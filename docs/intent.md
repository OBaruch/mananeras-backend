# Intent — Mañaneras Backend

> **Artifact type:** Intent (the *why*). First of the three spec-driven artifacts: **intent → [spec](spec.md) → [plan](plan.md)**.
> **Status:** Reconstructed (retro-specified) in 2026 from the existing code and git history of May 2025. It was not written before implementation; it describes the intent the original code expresses.
> **Evidence tags:** **[C]** Confirmed · **[I]** Inferred · **[U]** Unknown.

[← Back to README](../README.md)

---

## 1. Problem

The President of Mexico's daily morning press conferences (*"mañaneras"*) are long, unscripted and published as YouTube videos **[I]**. Getting the substance of a single conference means watching or skimming hours of video. No structured, searchable record of what was said is produced automatically.

## 2. Intent statement

Provide a backend that, **with one API call**, takes the most recent conference video from the official YouTube channel and turns it into a stored, structured record: the full Spanish transcript plus an automatic summary and a light semantic analysis. A client application can then display or query that record **[I]**, based on the endpoints in `src/main.py` **[C]**.

## 3. Target users

| User | Need | Level |
|------|------|-------|
| The author, as builder of an MVP | Validate that the download → transcribe → analyze → store chain works end to end on a real deployment | [I] |
| A client application (frontend, bot, script) | Fetch videos and their summaries as JSON | [I] (implied by the REST API and the `-backend` name; no client exists in the repo) |
| End readers (citizens, journalists, analysts) | Read a short summary instead of watching the whole video | [U] (never stated) |

## 4. Goals

1. **G1 — Automate ingestion.** Detect the channel's latest video without manual input **[C]** (`get_latest_video_id_from_channel`).
2. **G2 — Transcribe in Spanish.** Produce a full transcript from the audio **[C]** (Whisper, `language="es"`).
3. **G3 — Summarize and characterize.** Derive a summary, key points, discourse type, topics, policy category and sentiment **[C]** (`analizar_texto`).
4. **G4 — Persist and serve.** Store videos and analyses in PostgreSQL and expose them over HTTP **[C]**.
5. **G5 — Idempotent "latest" flow.** Do not reprocess a video that already has a summary **[C]** (commit `58c88a1`, check in `/api/auto-resumen/latest`).
6. **G6 — Run in the cloud with minimal ops.** Deployable as a single container on a PaaS (Railway) **[C]** (Dockerfile, commit history).

## 5. Non-goals (as evidenced by what was *not* built)

- No user accounts, authentication or authorization **[C]**.
- No background job queue or scheduler; processing runs synchronously inside the HTTP request **[C]**.
- No search, filtering or pagination endpoints **[C]**.
- No frontend in this repository **[C]**.
- No fact-checking, speaker diarization or timestamps **[C]**.
- No evaluation of the quality of the summaries **[C]**.

## 6. Success signals

These are the signals the MVP could demonstrate; whether they were ever measured is **[U]**.

- `GET /` answers on the deployed instance with the "connected to PostgreSQL" message.
- `POST /api/auto-resumen/latest` returns a `Resumen` with non-empty `contenido` and `transcripcion_completa` for the latest video.
- Calling it again for the same video returns the stored record instead of reprocessing it.

## 7. Constraints and assumptions

- **Language:** all content is Spanish **[C]**.
- **Source:** a single hard-coded channel URL **[C]**.
- **Models:** small, free, self-hosted models (Whisper `base`, `flan-t5-base`) rather than paid APIs **[C]**. The motive (cost, simplicity, curiosity) is **[U]**.
- **Runtime:** Python 3.10, Pydantic 1 (pinned to fix build compatibility) **[C]**.
- **Infra:** one container, one PostgreSQL database provided through `DATABASE_URL` **[C]**.

## 8. Open questions (unanswerable from the repository)

- Was there a frontend or consumer, and where does it live?
- Was the "latest" endpoint triggered manually or by an external scheduler?
- Did audio download from the cloud host eventually succeed? The last two commits are download diagnostics.
- Was the output quality of FLAN-T5 on Spanish text considered acceptable?
