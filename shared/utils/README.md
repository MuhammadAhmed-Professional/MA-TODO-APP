# Shared Utilities

This directory is reserved for shared utility functions and helpers that are used across multiple phases.

## Purpose

- **TypeScript utilities**: Helper functions, formatters, validators used by frontend components
- **Python utilities**: Common helper functions, decorators, or utilities used by backend services

## Usage

When a utility function is needed in multiple phases, place it here instead of duplicating it in each phase directory.

## Current Status

This directory is currently empty. Utilities will be added here as they become shared across phases.

## Example Structure (Future)

```
shared/utils/
├── validation.ts    # Shared validation functions
├── formatting.ts    # Date/time formatting utilities
├── api-helpers.ts   # API client helpers
└── constants.py     # Shared constants (Python)
```

