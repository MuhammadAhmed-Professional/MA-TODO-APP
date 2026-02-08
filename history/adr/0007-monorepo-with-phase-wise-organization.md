# ADR-0007: Monorepo with Phase-Wise Organization

> **Scope**: Fundamental project structure decision affecting all 5 hackathon phases

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** Project Structure (All Phases)
- **Context:** Hackathon spans 5 phases (CLI, Web App, Chatbot, Kubernetes, Cloud). Initial flat structure with numbered specs became untenable. Constitution v2.0.0 requires type-based organization.

## Decision

Adopt **phase-wise monorepo** with type-based spec organization:
- `phase-1/` (CLI), `phase-2/` (Web App), `phase-3-5/` (future)
- `specs/{features,api,database,ui}/` (type-based, not numbered)
- `history/{prompts,adr}/` (shared learning)
- Independent per-phase dependencies and deployment

## Consequences

### Positive

- Clear phase boundaries and ownership
- Independent deployment/archival
- Type-based specs improve discoverability
- Constitution v2.0.0 compliant
- Scales to 5 phases without restructuring

### Negative

- Migration cost (10 hours, 176 files)
- Multiple test locations
- Learning curve for contributors

## Alternatives Considered

1. **Flat monorepo**: Cluttered, unclear boundaries, doesn't scale
2. **Separate repos**: Loses shared learning, more setup overhead
3. **npm workspaces**: JavaScript-only, doesn't fit multi-language project

**Why phase-wise won**: Balance of isolation and knowledge sharing, clear for hackathon progression

## References

- Migration: `.specify/scripts/bash/migrate-to-phase-structure.sh`
- Guide: `MIGRATION_GUIDE.md`
- Constitution: `.specify/memory/constitution.md` v2.0.0
- Related ADRs: 001 (Storage), 002 (UV), 003 (Next.js), 004 (FastAPI), 005 (Neon), 006 (JWT)
