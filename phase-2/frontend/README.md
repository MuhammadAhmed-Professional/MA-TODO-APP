# Phase II Frontend - Next.js 16

**Status**: ✅ Deployed
**Live**: [https://talal-s-tda.vercel.app](https://talal-s-tda.vercel.app)
**Stack**: Next.js 16.0.10, React 19, TypeScript 5, Tailwind CSS, shadcn/ui

---

## Features

- App Router with dynamic routes and layouts
- Better Auth client integration (JWT + HttpOnly cookies)
- Task CRUD with priority, due dates, tags, search, filter, sort
- AI Chatbot with Vercel AI SDK
- Voice input (Web Speech API) + Voice output (Speech Synthesis)
- Multi-language (English + Urdu with RTL support)
- Dark/light mode (next-themes)
- Responsive design with Tailwind CSS + shadcn/ui
- Standalone Docker output for containerized deployment

---

## Quick Start

```bash
pnpm install
cp .env.local.example .env.local
pnpm dev  # http://localhost:3000
```

## Build

```bash
pnpm build  # Standalone output
pnpm start   # Production server
```

## Testing

```bash
pnpm test       # Unit tests (Vitest)
pnpm test:e2e   # E2E tests (Playwright)
pnpm lint       # ESLint
```

---

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3001
```

See `CLAUDE.md` for development guidelines.
