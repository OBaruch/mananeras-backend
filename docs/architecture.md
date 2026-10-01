# Architecture

A deliberately simple, single-process monolith: one FastAPI application, one PostgreSQL database and in-process ML models. This page describes only what exists in [`src/`](../src/).

[← Back to README](../README.md)

---

## 1. Components

```mermaid
flowchart TB
    subgraph Container["Container (python:3.10-slim, port 8000)"]
        direction TB
        M["main.py<br/>FastAPI routes + get_db()"]
        CR["crud.py<br/>query/insert helpers"]
        SC["schemas.py<br/>Pydantic v1 I/O models"]
        MO["models.py<br/>SQLAlchemy ORM"]
        DB["database.py<br/>engine · SessionLocal · Base"]
        T["utils/transcriber.py<br/>yt-dlp · Whisper · FLAN-T5"]
        FS[("/tmp/audio_files<br/>temporary MP3")]
        M --> CR & SC & MO & T
        CR --> MO & SC
        MO --> DB
        T --> FS
    end
    DB -->|DATABASE_URL| PG[(PostgreSQL)]
    T -->|HTTPS| YT[(YouTube)]
    T -.first use: model download.-> HF[(Hugging Face Hub /<br/>Whisper model CDN)]
```

| Component | Responsibility |
|-----------|----------------|
| `main.py` | HTTP layer and orchestration. It creates tables at import time, defines the per-request DB session dependency, and implements the two auto-summary flows inline. |
| `crud.py` | Thin data-access helpers for `Video` and `Resumen`. |
| `schemas.py` | Request and response contracts (Pydantic 1, `orm_mode`). |
| `models.py` | Table definitions and the `Video` ↔ `Resumen` relationship. |
| `database.py` | Builds the SQLAlchemy engine from `DATABASE_URL`. |
| `utils/transcriber.py` | All external I/O besides the DB: YouTube listing and download, Whisper speech-to-text, FLAN-T5 analysis. |

Some endpoints in `main.py` query the database directly (`db.query(models.Video)…`) instead of going through `crud.py`, so the layering is informal.

## 2. Request flow — `POST /api/auto-resumen/latest`

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as main.py
    participant T as transcriber.py
    participant Y as YouTube
    participant D as PostgreSQL
    C->>A: POST /api/auto-resumen/latest
    A->>T: get_latest_video_id_from_channel(@ClaudiaSheinbaumP)
    T->>Y: list channel (flat)
    Y-->>T: entries[0] → id, title
    A->>D: SELECT video WHERE youtube_id
    alt video not stored
        A->>D: INSERT video (date = utcnow)
    end
    A->>D: SELECT resumen WHERE video_id
    alt summary exists
        A-->>C: 200 existing Resumen
    else
        A->>T: download_audio(youtube_id)
        T->>Y: download bestaudio → ffmpeg → MP3
        A->>T: transcribe_audio(path)
        Note over T: load Whisper base, transcribe (es), delete MP3
        A->>T: analizar_texto(texto)
        Note over T: 6 FLAN-T5 prompts on truncated text
        A->>D: INSERT resumen
        A-->>C: 200 new Resumen
    end
    Note over A,C: any exception → 500 "Error en auto resumen: …"
```

`POST /api/videos/{video_id}/auto-resumen` follows the same pipeline for an already registered video. It does **not** check for an existing summary first.

## 3. Lifecycle notes

- **Import time:** `database.py` creates the engine, `main.py` runs `create_all`, and importing `utils/transcriber.py` loads the FLAN-T5 pipeline (downloading the weights on first run). The app is not ready until all of this finishes.
- **Per request:** a new DB session; for auto-summary requests, the Whisper model is loaded again on every call.
- **Concurrency:** handlers are plain `def` functions, so FastAPI runs them in its threadpool. Long transcriptions occupy a worker thread for their whole duration.

## 4. Deployment view

```mermaid
flowchart LR
    Repo["GitHub repo<br/>(src/ = build context)"] --> Build["Docker build<br/>apt: ffmpeg git gcc<br/>pip -r requirements.txt"]
    Build --> Run["uvicorn main:app<br/>0.0.0.0:8000"]
    Run --- PG[(Managed PostgreSQL<br/>via DATABASE_URL)]
```

The commit history shows this was deployed on Railway (see [`project-context.md`](project-context.md#5-deployment-history)). After the 2026 reorganization, the build context and working directory are `src/`.

## 5. What is *not* part of the architecture

There are no queues, workers, caches, schedulers, separate ML services, authentication layers or migrations. Any of these would be a new design, not a description of this project. See [`possible-improvements.md`](possible-improvements.md).
