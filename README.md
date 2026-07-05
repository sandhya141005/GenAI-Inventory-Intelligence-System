# Inventory Intelligence Platform — Frontend

Frontend-only implementation of the GenAI Inventory Copilot experience.
**No backend, database, auth, or AI model calls are wired up** — all data
lives in `lib/mock-data.ts` and the Copilot's replies are mocked in
`components/layout/CopilotPanel.tsx`. This keeps the project ready for a
teammate to drop in real APIs without touching UI code.

## Tech stack (as specified)

- Next.js 15 (App Router)
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui-style primitives (`components/ui`)
- Lucide Icons
- Framer Motion (installed, used sparingly — see note below)
- Apache ECharts (`echarts-for-react`) — Analytics page
- TanStack Table — Inventory page

## Getting started

```bash
npm install
npm run dev
```

Then open http://localhost:3000.

## Project structure

```
app/                    Route segments (App Router)
  layout.tsx            Root layout, wraps everything in <AppShell>
  page.tsx              Overview / landing page
  inventory/page.tsx     Inventory table
  recommendations/page.tsx
  reports/page.tsx
  analytics/page.tsx      ECharts-powered supporting analytics
  transfers/page.tsx
  aging/page.tsx
  notices/page.tsx
  settings/page.tsx
  copilot/page.tsx        Full-screen Copilot route used only on mobile
  globals.css             Theme tokens, base styles

components/
  layout/                 Sidebar, AppShell, CopilotPanel (pinned), MobileNav
  copilot/                ChatMessage, InsightCard, SuggestedPrompts
  dashboard/              KPICard, RecommendationCard
  inventory/              InventoryTable (TanStack Table)
  ui/                     button.tsx, card.tsx, badge.tsx (shadcn-style primitives)

lib/
  types.ts                Shared TypeScript interfaces
  mock-data.ts            All mock data — swap for real API calls here
  utils.ts                cn() class helper, currency formatter
```

## Where to plug in a real backend

1. **`lib/mock-data.ts`** — replace exported arrays with `fetch`/API calls
   (ideally via server components or a data-fetching hook).
2. **`components/layout/CopilotPanel.tsx`** — replace `buildAssistantResponse`
   with a real call to your inventory-reasoning/LLM endpoint. The chat state
   shape (`ChatMessage`, `ChatInsight`) is already designed to carry
   structured AI responses (metrics, reasoning, confidence, savings).
3. Add an `app/api/*` route (or a separate service) once auth/database
   requirements are defined — nothing here assumes a particular backend.

## Design notes

- Theme tokens (colors, radius, shadows) are defined once in
  `tailwind.config.ts` and mirror the brief exactly (`#0057B8` primary,
  `#F7F9FC` background, 12px radius, soft shadows only).
- The AI Copilot is a **persistent right-hand panel** on desktop (always
  visible per the brief), collapses to a toggle on smaller desktop widths,
  and becomes a dedicated full-screen route (`/copilot`) with bottom
  navigation on mobile.
- Motion is intentionally minimal: fade-in on new chat messages/cards and a
  typing indicator. Framer Motion is included in `package.json` for anything
  further (e.g. page transitions) but the current build leans on Tailwind's
  `animate-fade-in` utility to keep the bundle light — swap in
  `motion.div` where you want more orchestrated movement.

## Known limitations (by design, per the brief)

- No backend, auth, database, or real AI model — everything is mock data.
- No persistence between reloads (Copilot conversation resets on refresh).
- Charts/tables use representative, not live, figures.
## Backend / AI integration

The Member 2 backend lives in `backend/` as a separate FastAPI service. It includes PostgreSQL models and Alembic migrations, JWT auth, chat memory, LangGraph orchestration, Groq/OpenAI LLM integration, mock seed data, and Docker Compose.

See `backend/README.md` for setup and run instructions.
