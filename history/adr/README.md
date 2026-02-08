# Architecture Decision Records (ADRs)

This directory contains architectural decisions for the MA-TODO-APP project across all phases.

## Active ADRs

| ID | Title | Status | Date | Phase |
|----|-------|--------|------|-------|
| [0001](0001-in-memory-storage-for-phase-i-cli.md) | In-Memory Storage for Phase I CLI | Accepted | 2025-12-11 | Phase I |
| [0002](0002-uv-package-manager-for-python-dependencies.md) | UV Package Manager for Python Dependencies | Draft | 2025-12-11 | All |
| [0003](0003-next-js-16-app-router-for-frontend.md) | Next.js 16 App Router for Frontend | Draft | 2025-12-11 | Phase II |
| [0004](0004-fastapi-and-sqlmodel-backend-stack.md) | FastAPI and SQLModel Backend Stack | Draft | 2025-12-11 | Phase II |
| [0005](0005-neon-serverless-postgresql-database.md) | Neon Serverless PostgreSQL Database | Draft | 2025-12-11 | Phase II |
| [0006](0006-jwt-authentication-with-httponly-cookies.md) | JWT Authentication with HttpOnly Cookies | Draft | 2025-12-11 | Phase II |
| [0007](0007-monorepo-with-phase-wise-organization.md) | Monorepo with Phase-Wise Organization | Accepted | 2025-12-11 | All |

## Decision Categories

### Phase I (CLI)
- **0001**: In-Memory Storage - Fast prototyping, no persistence (superseded by 0005 in Phase II)

### Phase II (Web App)
- **0003**: Next.js 16 - Modern React framework with App Router
- **0004**: FastAPI + SQLModel - Type-safe Python backend
- **0005**: Neon PostgreSQL - Serverless database for production
- **0006**: JWT + HttpOnly Cookies - Secure authentication strategy

### Cross-Phase
- **0002**: UV Package Manager - Python dependency management (all phases)
- **0007**: Phase-Wise Monorepo - Project structure (all phases)

## Status Definitions

- **Accepted**: Decision implemented and validated
- **Draft**: ADR created, needs detailed content
- **Proposed**: Under review
- **Rejected**: Decision not adopted
- **Superseded**: Replaced by newer ADR

## Next Steps

ADRs marked as **Draft** need detailed content:
1. Fill **Context** section with problem statement
2. Document **Alternatives Considered** (at least 2)
3. List **Consequences** (positive and negative)
4. Add **References** to specs, code, related ADRs

Use `.specify/templates/adr-template.md` as guide.

---

*ADRs follow [Michael Nygard's format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)*
