# Shared Types

This directory is reserved for shared TypeScript/Python type definitions that are used across multiple phases.

## Purpose

- **TypeScript types**: Common interfaces, types, and enums used by frontend components across phases
- **Python types**: Common Pydantic models or type hints shared between backend services

## Usage

When a type definition is needed in multiple phases, place it here instead of duplicating it in each phase directory.

## Current Status

This directory is currently empty. Types will be added here as they become shared across phases.

## Example Structure (Future)

```
shared/types/
├── task.ts          # Task type definition (used in Phase 2+)
├── user.ts          # User type definition (used in Phase 2+)
└── api.ts           # API response types (used across all phases)
```

