# RACE Frontend Architecture

This folder contains the frontend workspace for the **RACE (Revenue Adaptive Control Engine)** Merchant Operations Console.

---

## Current Architecture: Zero-Dependency Embedded Console

To enable single-command, zero-configuration local execution and evaluation, the live interactive frontend is served directly by the FastAPI application in [`backend/api/app.py`](../backend/api/app.py).

### Endpoints:
* **`/`** — Operational Console (Real-time telemetry, Scenario selector, Organic Neural Loader, 5-stage lifecycle rail, ERV Decision Centerpiece, Deterministic Policy Gate, Outcome Settlement, and Recovery Queue).
* **`/benchmarks`** — Scientific Validation & Benchmark Matrix (200 held-out cases, Baselines A/B/C, Ablation study, Live re-test trigger).
* **`/about`** — Technical System Specification (Mathematical foundations, 9-stage architecture, 4 core equations).

### Tech Stack:
* **Framework**: Native HTML5 + Vanilla JS + HTML5 Canvas (Organic Neural Network Loader)
* **Styling**: Tailwind CSS (with Light & Dark theme support and `localStorage` persistence)
* **Typography**: Plus Jakarta Sans (UI) + JetBrains Mono (Data & Formulas)

---

## Future Standalone Expansion

The `public/` and `src/` subdirectories are structured to support future standalone Next.js / Vite / React dashboard deployments if decoupled micro-frontend routing is desired.
