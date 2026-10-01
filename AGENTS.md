# AGENTS.md

Working agreement for anyone (human contributors or AI coding agents) who changes this repository.

## What this repository is

A **historical** personal MVP from May 2025: a FastAPI backend that transcribes and summarizes YouTube videos of the Mexican presidential morning conferences. Start with [`README.md`](README.md), then read [`docs/intent.md`](docs/intent.md) → [`docs/spec.md`](docs/spec.md) → [`docs/plan.md`](docs/plan.md).

## Hard rules

1. **Do not modify anything under `src/`.** That includes logic, formatting, comments, names, imports, `requirements.txt`, `Procfile` and `Dockerfile`. They are the preserved original implementation. Do not "fix" bugs, upgrade dependencies or apply linters there.
2. **Do not delete historical material.** That covers `docs/original/` and git history references.
3. **Do not invent facts.** Tag statements in docs as *Confirmed*, *Inferred* or *Unknown*, and cite the file or commit.
4. **Improvements are documentation only.** Record them in [`docs/possible-improvements.md`](docs/possible-improvements.md). Do not implement them in this repository.
5. **No new infrastructure** (CI, Docker Compose, linters, test frameworks, package managers) unless the owner explicitly requests it.

## Spec-driven workflow for any future change

Any future change should follow intent → spec → plan → implement → verify:

1. Update [`docs/intent.md`](docs/intent.md) if the *why* changes.
2. Update [`docs/spec.md`](docs/spec.md) with requirement IDs (`FR-n`) for the *what*.
3. Add a phase to [`docs/plan.md`](docs/plan.md) with tasks, guardrails and verification.
4. Implement in small commits using Conventional Commits (`docs:`, `refactor(repo):`, `feat:` …).
5. Verify the guardrail: `git diff -M main --stat` must list every `src/` file as a pure rename with no line changes (unless the owner explicitly approved a code change).

## Useful facts

- Run from `src/` (flat imports): `uvicorn main:app --host 0.0.0.0 --port 8000`, with `DATABASE_URL` set.
- Docker build context: `src/`.
- There are no tests. The derived acceptance checks are in [`docs/spec.md` §8](docs/spec.md#8-acceptance-checks-derived).
