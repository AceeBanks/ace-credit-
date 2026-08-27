# Grant Platform Web (apps/web)

Chat-first client application per **G1 Appendix B — Client Interaction &
Frontend Contract**.

## Stack (Appendix B §20)

Next.js · React · TypeScript · Tailwind · shadcn-style accessible
primitives. Desktop-first, mobile usable. No hard runtime dependency on
inspiration/component websites.

## Run

```bash
# 1. API (repo root)
python -m uvicorn apps.api.main:app --port 8000

# 2. Web (this directory)
npm install
npm run dev        # http://localhost:3000
```

The Next dev server rewrites `/api/*` to the FastAPI backend
(`http://localhost:8000` by default; override with `API_URL`).

## Product Principles (Appendix B §12–§17)

- Primary experience is **CHAT + WORK PROGRESS + DELIVERABLES** — not a
  complex grant dashboard.
- User types what they need → system works → high-level progress → final
  deliverable appears in chat.
- Right-side **Work** panel exposes operational state (finding
  opportunities, checking eligibility, drafting sections, QA, packaging)
  — never private model reasoning or chain-of-thought.
- Deliverable cards offer DOCX/PDF downloads directly in chat.
- Model picker defaults to **Auto — Recommended** and lists only governed
  approved models; the backend retains final selection authority
  (Appendix A §8). The client never needs to understand model
  infrastructure (Appendix A §10).
- Advanced Hermes consoles (Personal/CEO) are reachable via the API
  (`/consoles`) for advanced/debug use only; workers are never exposed as
  user-facing chats.
- **Submission stays disabled** — the UI says "Ready for review"; there is
  no submit action anywhere.

## Verification

```bash
npm run typecheck
npm run build
```

Browser/API integration behavior is exercised end-to-end by
`tools/g1/pilot_simulation.py` (drives the real API; see G1 Pilot
checkpoint).
