# Skill: Add Accessibility

## Description
Add WCAG 2.1 AA accessibility features to React components including ARIA labels, focus indicators, keyboard navigation, and screen reader support.

## Inputs
- `component_file`: Path to the React component (e.g., `frontend/src/components/tasks/TaskCard.tsx`)
- `accessibility_requirements`: Specific a11y features needed (e.g., "keyboard navigation", "screen reader labels", "focus indicators")

## Process

### 1. Analyze Component Interactions
- Read the component file
- Identify interactive elements (buttons, inputs, links, custom controls)
- Identify visual-only information (icons without text, color-only states)
- Identify focus management needs (modals, dropdowns, menus)

### 2. Add ARIA Labels

#### Icon Buttons (no visible text)
```typescript
// Before
<button onClick={onDelete}>
  <TrashIcon />
</button>

// After
<button onClick={onDelete} aria-label="Delete task">
  <TrashIcon aria-hidden="true" />
</button>
```

#### Form Fields
```typescript
// Before
<input type="text" placeholder="Task title" />

// After
<label htmlFor="task-title" className="sr-only">Task Title</label>
<input
  id="task-title"
  type="text"
  placeholder="Task title"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby={hasError ? "title-error" : undefined}
/>
{hasError && <span id="title-error" className="text-red-600">Title is required</span>}
```

#### Live Regions (dynamic content)
```typescript
// Announce task creation success
<div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
  {successMessage}
</div>
```

### 3. Add Focus Indicators
Use Tailwind's focus utilities:
```typescript
// Buttons
className="... focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"

// Inputs
className="... focus:border-blue-500 focus:ring-2 focus:ring-blue-200"

// Custom focus styles
className="... focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
```

### 4. Add Keyboard Navigation

#### Custom Dropdowns/Menus
```typescript
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Escape') {
    closeMenu();
  } else if (e.key === 'ArrowDown') {
    focusNextItem();
  } else if (e.key === 'ArrowUp') {
    focusPreviousItem();
  } else if (e.key === 'Enter' || e.key === ' ') {
    selectCurrentItem();
  }
};

<div role="menu" onKeyDown={handleKeyDown}>
  <button role="menuitem" tabIndex={0}>Option 1</button>
  <button role="menuitem" tabIndex={-1}>Option 2</button>
</div>
```

#### Modal Focus Traps
```typescript
import { useEffect, useRef } from 'react';

function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  );
}
```

### 5. Add Alt Text for Images
```typescript
// Decorative images (purely visual)
<img src="/decorative-pattern.svg" alt="" />

// Functional images (convey information)
<img src="/empty-state.svg" alt="No tasks found. Create your first task to get started." />

// Logo
<img src="/logo.svg" alt="TaskMaster - Todo Application" />
```

### 6. Ensure Color Contrast
Use Tailwind colors that meet WCAG 2.1 AA standards:
- Text (4.5:1): `text-gray-900` on `bg-white`, `text-white` on `bg-blue-600`
- UI components (3:1): `border-gray-300`, `bg-gray-100`
- Avoid: `text-gray-400` on `bg-white` (fails contrast)

### 7. Test with Tools
- **Chrome DevTools**: Lighthouse accessibility audit (score ≥90)
- **axe DevTools**: Automated a11y testing extension
- **Screen reader**: Test with NVDA (Windows) or VoiceOver (Mac)
- **Keyboard only**: Disconnect mouse, navigate with Tab/Enter/Space/Escape

## Example Usage

**Scenario**: Add accessibility to TaskCard component

```bash
# Context: Task T081 from tasks.md
# T081: Add ARIA labels to all icon buttons in TaskCard (aria-label="Mark complete", "Edit task", "Delete task")
```

**Agent invocation**:
```
Add accessibility to TaskCard:
- Component: frontend/src/components/tasks/TaskCard.tsx
- Requirements:
  - Add aria-label to toggle complete button ("Mark task as complete" / "Mark task as incomplete")
  - Add aria-label to edit button ("Edit task")
  - Add aria-label to delete button ("Delete task")
  - Add focus indicators (ring-2 ring-blue-500)
  - Ensure keyboard navigation (Enter and Space trigger buttons)
```

**Scenario**: Add accessibility to forms

```bash
# Context: Task T079 from tasks.md
# T079: Update SignupForm and LoginForm to be responsive and accessible
```

**Agent invocation**:
```
Add accessibility to SignupForm and LoginForm:
- Components: frontend/src/components/auth/SignupForm.tsx, LoginForm.tsx
- Requirements:
  - Associate labels with inputs (htmlFor + id)
  - Add aria-required="true" to required fields
  - Add aria-invalid and aria-describedby for validation errors
  - Add focus indicators to inputs
  - Announce form errors to screen readers (role="alert")
```

## Constitution Compliance
- **Principle V**: Multi-interface - Accessibility ensures usability for all users
- **Principle XII**: Security - Proper ARIA prevents UI spoofing/phishing
- **Principle II**: Clean code - Follow semantic HTML and ARIA best practices

## Output
- Updated component file with accessibility features
- Lighthouse accessibility score ≥90
- Manual keyboard navigation test passing
