# Skill: Create Frontend Tests

## Description
Generate comprehensive Vitest + React Testing Library tests for React components with proper rendering, interaction, and state testing patterns.

## Inputs
- `component_file`: Path to the React component (e.g., `frontend/src/components/tasks/TaskCard.tsx`)
- `test_scenarios`: List of scenarios to test (e.g., "toggle complete", "delete button", "form validation")

## Process

### 1. Analyze Component
- Read the component file to understand props, state, and user interactions
- Identify event handlers (onClick, onChange, onSubmit)
- Identify conditional rendering and state transitions
- Identify form fields and validation rules

### 2. Generate Component Tests
Create `frontend/tests/unit/<ComponentName>.test.tsx`:
- Test initial render (component mounts without errors)
- Test prop variations (different prop values render correctly)
- Test user interactions (clicks, typing, form submission)
- Test validation errors (invalid inputs show error messages)
- Test loading/error states
- Mock external dependencies (API calls, context values)

**Pattern**:
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TaskCard from '@/components/tasks/TaskCard';

describe('TaskCard', () => {
  it('renders task title and description', () => {
    const task = { id: '1', title: 'Test Task', description: 'Test Description' };
    render(<TaskCard task={task} />);
    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('calls onToggle when checkbox is clicked', async () => {
    const onToggle = vi.fn();
    render(<TaskCard task={...} onToggle={onToggle} />);
    fireEvent.click(screen.getByRole('checkbox'));
    await waitFor(() => expect(onToggle).toHaveBeenCalledWith('1'));
  });
});
```

### 3. Test Accessibility
- Test keyboard navigation (Tab, Enter, Space)
- Test ARIA labels (screen reader text)
- Test focus management (focus traps in modals)

### 4. Test Forms
For form components, test:
- Valid submission (success flow)
- Invalid submission (validation errors displayed)
- Field-level validation (email format, min/max length)
- Disabled state during submission
- Error messages from API (401, 400, 500)

**Pattern**:
```typescript
it('shows validation error for empty title', async () => {
  render(<TaskForm />);
  fireEvent.submit(screen.getByRole('button', { name: /submit/i }));
  await waitFor(() => {
    expect(screen.getByText(/title is required/i)).toBeInTheDocument();
  });
});
```

## Example Usage

**Scenario**: Generate tests for TaskCard and TaskForm components

```bash
# Context: Tasks T063 and T064 from tasks.md
# T063: Write frontend unit tests in frontend/tests/unit/TaskCard.test.tsx
# T064: Write frontend unit tests in frontend/tests/unit/TaskForm.test.tsx
```

**Agent invocation**:
```
Create frontend tests for:
1. TaskCard component (frontend/src/components/tasks/TaskCard.tsx)
   - Test scenarios: render task, toggle complete checkbox, delete button click

2. TaskForm component (frontend/src/components/tasks/TaskForm.tsx)
   - Test scenarios: valid submission, title required validation, description max length, API error handling
```

## Constitution Compliance
- **Principle III**: TDD - Component tests validate behavior and user interactions
- **Principle V**: Multi-interface - Tests ensure accessibility (keyboard, screen reader)
- **Principle II**: Clean code - Tests follow testing-library best practices (queries by role/label)

## Output
- `frontend/tests/unit/<ComponentName>.test.tsx` (component tests)
- Coverage report showing >70% coverage for tested components
