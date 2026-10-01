# Possible Improvements

> **Important:** none of the items below have been applied. The code in [`src/`](../src/) is intentionally preserved as the original May 2025 implementation. This list documents observations made during the 2026 review, for learning and for any future, separate iteration of the project.

Severity is a rough judgment for a production context: 🔴 high · 🟠 medium · 🟡 low. "Observed" means it is visible in the code; "Possible" means it is likely but was not reproduced.

[← Back to README](../README.md)

---

## 1. Correctness and robustness

| # | Observation | Where | Sev. |
|---|-------------|-------|------|
| 1.1 | `create_all` never alters existing tables. The six analysis columns added in `db48f12` would be missing from any database created before that commit, so inserts would fail. Schema migrations (e.g. Alembic) would solve it. | `main.py`, `models.py` | 🔴 Observed |
| 1.2 | `resumenes.video_id` has no unique constraint, and `POST /resumen` and `POST /{id}/auto-resumen` don't check for an existing summary. Duplicates are possible, and `get_resumen_by_video` returns an arbitrary first one. | `models.py`, `main.py` | 🟠 Observed |
| 1.3 | `outtmpl` is a fixed name ending in `.mp3` (with no `%(ext)s`) combined with `FFmpegExtractAudio`. This is a plausible cause of the "file not found after download" problem that the last two commits were diagnosing. | `transcriber.py` | 🟠 Possible |
| 1.4 | If transcription fails, the temporary MP3 is never deleted (`os.remove` only runs on success). | `transcriber.py` | 🟡 Observed |
| 1.5 | `force_generic_extractor=True` while listing a YouTube channel bypasses the YouTube extractor and may return unexpected entries. Also, `entries[0]` is assumed to be the latest video, which may be a live stream or a short. | `transcriber.py` | 🟠 Possible |
| 1.6 | A `None` `DATABASE_URL` crashes the app at import time with an unclear error. | `database.py` | 🟡 Observed |
| 1.7 | `POST /api/videos` with a duplicate `youtube_id` raises an unhandled `IntegrityError` → generic 500. | `crud.py` | 🟡 Observed |

## 2. ML quality

| # | Observation | Sev. |
|---|-------------|------|
| 2.1 | `google/flan-t5-base` is mainly trained on English instructions, so Spanish prompts and outputs may be poor or answered in English. A multilingual model (mT5/mBART-based summarizers) or an LLM API would fit Spanish better. | 🟠 Possible |
| 2.2 | Only the first 1,000–4,000 characters of a transcript spanning hours are analyzed, so most of the content is ignored. Chunking with map-reduce summarization would cover the whole text. | 🔴 Observed |
| 2.3 | `max_length=10` for single-word labels and free-text categories gives unconstrained outputs. Zero-shot classification with a fixed label set would be more consistent. | 🟡 Observed |
| 2.4 | Whisper `base` has limited accuracy on long, noisy Spanish audio. Larger models or `faster-whisper` trade accuracy against cost. | 🟡 Possible |

## 3. Performance and scalability

| # | Observation | Sev. |
|---|-------------|------|
| 3.1 | The full download + transcription + analysis runs inside the HTTP request. It will exceed typical proxy timeouts for long videos. A background job (queue/worker) plus a status endpoint would avoid that. | 🔴 Observed |
| 3.2 | The Whisper model is reloaded on every request; it could be loaded once and reused. | 🟠 Observed |
| 3.3 | FLAN-T5 loads at import time, which slows startup and makes health checks fail until it is ready. | 🟡 Observed |
| 3.4 | `GET /api/videos` has no pagination. | 🟡 Observed |
| 3.5 | Installing full CUDA-enabled `torch` in a CPU container makes the image unnecessarily large. A CPU-only wheel would be much smaller. | 🟡 Possible |

## 4. Security and operations

| # | Observation | Sev. |
|---|-------------|------|
| 4.1 | Expensive endpoints (`auto-resumen`) are unauthenticated: anyone can trigger heavy compute. | 🔴 Observed |
| 4.2 | Raw exception text, including `yt-dlp` logs, is returned to clients. | 🟠 Observed |
| 4.3 | `Procfile` and `Dockerfile` hard-code port 8000 instead of using the platform-provided `$PORT`. | 🟡 Observed |
| 4.4 | Logging is done with `print`; no structured logs or request IDs. | 🟡 Observed |
| 4.5 | YouTube downloads from data-center IPs are frequently blocked or throttled. This is an operational risk with no mitigation in the code. | 🟠 Possible |

## 5. Maintainability

| # | Observation | Sev. |
|---|-------------|------|
| 5.1 | Dependencies are mostly unpinned, and Whisper is installed from the Git HEAD, so builds are not reproducible. A lock file would fix that. | 🟠 Observed |
| 5.2 | `python-dotenv` and `ffmpeg-python` are declared but unused. | 🟡 Observed |
| 5.3 | Pydantic 1 (`orm_mode`, `.dict()`) and `sqlalchemy.ext.declarative` are legacy APIs. | 🟡 Observed |
| 5.4 | `datetime.utcnow` is deprecated in newer Python versions and produces naive datetimes. | 🟡 Observed |
| 5.5 | Configuration such as the channel URL and model names is hard-coded; it could come from environment variables. | 🟡 Observed |
| 5.6 | There are no automated tests. The acceptance checks in [`spec.md` §8](spec.md#8-acceptance-checks-derived) are a natural starting point. | 🟠 Observed |
| 5.7 | The data access pattern is mixed: some queries are inline in `main.py`, others live in `crud.py`. | 🟡 Observed |
