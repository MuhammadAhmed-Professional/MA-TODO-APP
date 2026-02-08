# Frontend Development Guidelines (Next.js 16+ / React 19+)

**Project**: Phase II Full-Stack Todo Application - Frontend
**Framework**: Next.js 16+ with App Router, React 19+, TypeScript 5+ (strict mode)
**Styling**: Tailwind CSS 4+, shadcn/ui component library
**Authentication**: Better Auth client integration

---

## Directory Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router (routes + layouts)
│   │   ├── layout.tsx          # Root layout (providers, auth)
│   │   ├── page.tsx            # Landing page
│   │   ├── (auth)/             # Auth route group (public)
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   └── (dashboard)/        # Dashboard route group (protected)
│   │       ├── layout.tsx      # Dashboard layout (sidebar)
│   │       ├── dashboard/page.tsx
│   │       └── tasks/
│   │           ├── page.tsx    # Task list
│   │           └── [id]/page.tsx # Task detail
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn/ui components (Button, Input, etc.)
│   │   ├── auth/               # Auth-related components
│   │   ├── tasks/              # Task components
│   │   └── layout/             # Layout components (Header, Sidebar)
│   ├── lib/                    # Utilities and API clients
│   │   ├── api.ts              # Fetch wrapper with auth headers
│   │   ├── auth.ts             # Client-side auth utilities
│   │   └── utils.ts            # General utilities
│   └── types/                  # TypeScript type definitions
│       ├── user.ts             # User types (match backend)
│       ├── task.ts             # Task types (match backend)
│       └── api.ts              # API response types
├── public/                     # Static assets
├── tests/                      # Frontend tests
│   ├── unit/                   # Component unit tests (vitest)
│   └── e2e/                    # Playwright E2E tests
├── package.json                # pnpm dependencies
├── tsconfig.json               # TypeScript config (strict mode)
├── tailwind.config.ts          # Tailwind configuration
├── next.config.js              # Next.js configuration
└── .env.local.example          # Example environment variables
```

---

## Core Principles (Enforced by Constitution v2.0.0)

### 1. React Server Components (RSC) Default

**Use Server Components by default** for data fetching and static content:

```typescript
// ✅ GOOD: Server Component (default, no "use client")
export default async function TasksPage() {
  const tasks = await fetchTasks(); // Server-side fetch
  return <TaskList tasks={tasks} />;
}
```

**Use Client Components only for interactivity** (forms, buttons, modals):

```typescript
// ✅ GOOD: Client Component (for user interaction)
"use client";

export function TaskForm() {
  const [title, setTitle] = useState("");
  const handleSubmit = async (e: FormEvent) => {
    // ... form handling
  };
  return <form onSubmit={handleSubmit}>...</form>;
}
```

**❌ BAD: Using Client Component for data fetching**

```typescript
// ❌ BAD: Unnecessary client-side data fetching
"use client";
import { useEffect, useState } from "react";

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  useEffect(() => {
    fetch("/api/tasks").then((res) => setTasks(res.json()));
  }, []);
  return <TaskList tasks={tasks} />;
}
```

### 2. TypeScript Strict Mode

**Always use strict TypeScript** with proper type definitions:

```typescript
// ✅ GOOD: Proper typing
interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: string) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

export function TaskCard({ task, onToggleComplete, onDelete }: TaskCardProps) {
  // ...
}
```

**❌ BAD: Using `any` or loose typing**

```typescript
// ❌ BAD: Avoid `any`
export function TaskCard({ task, onToggleComplete }: any) {
  // ...
}
```

### 3. File and Component Naming

**Follow Next.js conventions**:

- **Pages**: `page.tsx` (lowercase)
- **Layouts**: `layout.tsx` (lowercase)
- **Components**: `PascalCase.tsx` (e.g., `TaskCard.tsx`, `LoginForm.tsx`)
- **Utilities**: `camelCase.ts` (e.g., `api.ts`, `utils.ts`)
- **Types**: `camelCase.ts` (e.g., `task.ts`, `user.ts`)

### 4. Component Size Limit

**Maximum 200 lines per component file**. If a component exceeds this:

1. Extract sub-components into separate files
2. Move complex logic to utility functions in `lib/`
3. Consider using composition over large monolithic components

---

## API Integration Patterns

### Fetch Wrapper with Authentication

**Always use the centralized API client** from `lib/api.ts`:

```typescript
// lib/api.ts
export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    credentials: "include", // Include HttpOnly cookies
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "API request failed");
  }

  return response.json();
}
```

**Usage in components**:

```typescript
// ✅ GOOD: Using centralized API client
import { fetchAPI } from "@/lib/api";

export async function getTasks(): Promise<Task[]> {
  const response = await fetchAPI<TaskListResponse>("/api/tasks");
  return response.tasks;
}
```

**❌ BAD: Direct fetch without error handling**

```typescript
// ❌ BAD: Direct fetch, no error handling
const tasks = await fetch("/api/tasks").then((r) => r.json());
```

### Type Safety Between Frontend and Backend

**Match backend types exactly** to prevent runtime errors:

```typescript
// types/task.ts (MUST match backend TaskResponse)
export interface Task {
  id: string; // UUID
  title: string;
  description: string | null;
  is_complete: boolean;
  user_id: string; // UUID
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

// types/user.ts (MUST match backend UserResponse)
export interface User {
  id: string; // UUID
  email: string;
  name: string;
  created_at: string; // ISO 8601
}
```

---

## Authentication Patterns

### Better Auth Client Setup

**Configure Better Auth** in `lib/auth.ts`:

```typescript
// lib/auth.ts
import { createAuth } from "better-auth/react";

export const auth = createAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  cookiePrefix: "tda_", // Todo App prefix
});

export const { useSession, signIn, signOut, signUp } = auth;
```

### Protected Route Pattern

**Use middleware for route protection**:

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const authToken = request.cookies.get("auth_token");

  // Redirect unauthenticated users from protected routes
  if (!authToken && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirect authenticated users from auth pages
  if (authToken && request.nextUrl.pathname.startsWith("/login")) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/signup"],
};
```

### Session Management in Components

**Access user session** with Better Auth hooks:

```typescript
// ✅ GOOD: Using Better Auth session
"use client";

import { useSession } from "@/lib/auth";

export function Header() {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return <div>Loading...</div>;
  }

  if (!session) {
    return <LoginButton />;
  }

  return (
    <div>
      <p>Welcome, {session.user.name}</p>
      <LogoutButton />
    </div>
  );
}
```

---

## Form Handling with React Hook Form + Zod

**Use React Hook Form + Zod for all forms**:

```typescript
// ✅ GOOD: Form with validation
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title too long"),
  description: z.string().max(2000, "Description too long").optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

export function TaskForm({ onSubmit }: { onSubmit: (data: TaskFormData) => Promise<void> }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("title")} placeholder="Task title" />
      {errors.title && <span className="text-red-500">{errors.title.message}</span>}

      <textarea {...register("description")} placeholder="Description (optional)" />
      {errors.description && <span className="text-red-500">{errors.description.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : "Save Task"}
      </button>
    </form>
  );
}
```

---

## Styling Guidelines (Tailwind CSS + shadcn/ui)

### Use shadcn/ui Components

**Prefer shadcn/ui** for common UI elements (buttons, inputs, cards, dialogs):

```typescript
// ✅ GOOD: Using shadcn/ui components
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export function TaskCard({ task }: { task: Task }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{task.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{task.description}</p>
        <Button onClick={() => handleToggle(task.id)}>
          {task.is_complete ? "Undo" : "Complete"}
        </Button>
      </CardContent>
    </Card>
  );
}
```

### Tailwind Class Organization

**Order Tailwind classes** logically:

1. Layout (display, position)
2. Spacing (margin, padding)
3. Sizing (width, height)
4. Typography (font, text)
5. Visual (color, background, border)
6. Interactions (hover, focus)

```typescript
// ✅ GOOD: Organized classes
<div className="flex flex-col gap-4 p-6 w-full max-w-2xl text-lg font-medium text-gray-900 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
```

### Responsive Design

**Use mobile-first approach** with Tailwind breakpoints:

```typescript
// ✅ GOOD: Mobile-first responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Cards adapt to screen size */}
</div>
```

---

## Performance Optimization

### Image Optimization

**Always use Next.js Image component**:

```typescript
// ✅ GOOD: Optimized images
import Image from "next/image";

<Image
  src="/logo.png"
  alt="Todo App Logo"
  width={200}
  height={50}
  priority // For above-the-fold images
/>
```

### Dynamic Imports for Heavy Components

**Lazy load non-critical components**:

```typescript
// ✅ GOOD: Dynamic import for modal
import dynamic from "next/dynamic";

const TaskDetailModal = dynamic(() => import("@/components/tasks/TaskDetailModal"), {
  loading: () => <div>Loading modal...</div>,
  ssr: false, // Client-side only
});
```

### Route Prefetching

**Leverage Next.js Link prefetching** (automatic):

```typescript
// ✅ GOOD: Automatic prefetching with Link
import Link from "next/link";

<Link href="/dashboard/tasks">
  View All Tasks
</Link>
```

---

## Error Handling

### Error Boundaries

**Use error.tsx for route-level error handling**:

```typescript
// app/(dashboard)/error.tsx
"use client";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold text-red-600">Something went wrong!</h2>
      <p className="text-gray-600 mt-2">{error.message}</p>
      <button
        onClick={reset}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Try Again
      </button>
    </div>
  );
}
```

### API Error Handling

**Handle API errors gracefully**:

```typescript
// ✅ GOOD: Proper error handling
"use client";

import { useState } from "react";
import { toast } from "@/components/ui/use-toast";

export function DeleteTaskButton({ taskId }: { taskId: string }) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await fetchAPI(`/api/tasks/${taskId}`, { method: "DELETE" });
      toast({ title: "Task deleted successfully" });
      // Trigger revalidation or redirect
    } catch (error) {
      toast({
        title: "Failed to delete task",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <button onClick={handleDelete} disabled={isDeleting}>
      {isDeleting ? "Deleting..." : "Delete"}
    </button>
  );
}
```

---

## Testing Guidelines

### Component Unit Tests (Vitest + React Testing Library)

**Test user interactions, not implementation details**:

```typescript
// tests/unit/TaskCard.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TaskCard } from "@/components/tasks/TaskCard";

test("marks task as complete when complete button is clicked", async () => {
  const mockTask = { id: "1", title: "Test Task", is_complete: false };
  const mockOnToggle = vi.fn();

  render(<TaskCard task={mockTask} onToggleComplete={mockOnToggle} />);

  const completeButton = screen.getByRole("button", { name: /complete/i });
  await userEvent.click(completeButton);

  expect(mockOnToggle).toHaveBeenCalledWith("1");
});
```

### E2E Tests (Playwright)

**Test critical user flows end-to-end**:

```typescript
// tests/e2e/tasks.spec.ts
import { test, expect } from "@playwright/test";

test("user can create and complete a task", async ({ page }) => {
  await page.goto("/login");
  await page.fill("[name=email]", "test@example.com");
  await page.fill("[name=password]", "password123");
  await page.click("button[type=submit]");

  await page.waitForURL("/dashboard");

  // Create task
  await page.click("text=Add Task");
  await page.fill("[name=title]", "New Task");
  await page.click("button:has-text('Save')");
  await expect(page.locator("text=New Task")).toBeVisible();

  // Complete task
  await page.click("[aria-label='Mark complete']");
  await expect(page.locator("text=New Task")).toHaveClass(/line-through/);
});
```

---

## Environment Variables

**Required environment variables** (`.env.local`):

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-different-secret-here

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

**NEVER commit** `.env.local` to version control. Use `.env.local.example` for documentation.

---

## Common Pitfalls to Avoid

### ❌ Don't Use "use client" Unnecessarily

```typescript
// ❌ BAD: Unnecessary "use client" for static content
"use client";

export default function AboutPage() {
  return <div>About us...</div>; // No interactivity!
}
```

### ❌ Don't Fetch Data in Client Components

```typescript
// ❌ BAD: Client-side data fetching in useEffect
"use client";

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  useEffect(() => {
    fetch("/api/tasks").then((r) => r.json()).then(setTasks);
  }, []);
  // ... causes waterfalls, poor UX
}
```

### ❌ Don't Hardcode API URLs

```typescript
// ❌ BAD: Hardcoded URLs
const response = await fetch("http://localhost:8000/api/tasks");

// ✅ GOOD: Use environment variable
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks`);
```

### ❌ Don't Mix Backend and Frontend Code

```typescript
// ❌ BAD: Importing backend code in frontend
import { User } from "@/../backend/src/models/user"; // NEVER do this

// ✅ GOOD: Define frontend types separately
import { User } from "@/types/user";
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Start dev server** | `pnpm dev` |
| **Build for production** | `pnpm build` |
| **Run unit tests** | `pnpm test` |
| **Run E2E tests** | `pnpm test:e2e` |
| **Lint code** | `pnpm lint` |
| **Format code** | `pnpm format` |
| **Type check** | `pnpm type-check` |

---

## Additional Resources

- **Next.js Docs**: https://nextjs.org/docs
- **React Docs**: https://react.dev
- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **shadcn/ui Docs**: https://ui.shadcn.com
- **Better Auth Docs**: https://better-auth.com
- **React Hook Form Docs**: https://react-hook-form.com
- **Zod Docs**: https://zod.dev
- **Playwright Docs**: https://playwright.dev

For project-specific architecture, see:
- [Specification](../specs/004-phase-2-web-app/spec.md)
- [Implementation Plan](../specs/004-phase-2-web-app/plan.md)
- [API Contracts](../specs/004-phase-2-web-app/contracts/)
