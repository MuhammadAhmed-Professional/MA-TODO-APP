/**
 * Unit Tests for TaskForm Component (T064)
 *
 * Tests form fields, validation, submission behavior, and error handling.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TaskForm } from '@/components/tasks/TaskForm';
import { Task, TaskCreate, TaskUpdate } from '@/types/task';

describe('TaskForm - Rendering Tests', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders form fields for creating new task', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText('Create New Task')).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save task/i })).toBeInTheDocument();
  });

  it('renders form fields for editing existing task', () => {
    const existingTask: Task = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      title: 'Existing Task',
      description: 'Existing description',
      is_complete: false,
      user_id: '123e4567-e89b-12d3-a456-426614174001',
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    };

    render(<TaskForm task={existingTask} onSubmit={mockOnSubmit} />);

    expect(screen.getByText('Edit Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Existing Task')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Existing description')).toBeInTheDocument();
  });

  it('shows cancel button when onCancel provided', () => {
    render(<TaskForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('does not show cancel button when onCancel not provided', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.queryByRole('button', { name: /cancel/i })).not.toBeInTheDocument();
  });

  it('uses custom submit label when provided', () => {
    render(<TaskForm onSubmit={mockOnSubmit} submitLabel="Update Task" />);

    expect(screen.getByRole('button', { name: /update task/i })).toBeInTheDocument();
  });

  it('shows helper text for field requirements', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText(/required, max 200 characters/i)).toBeInTheDocument();
    expect(screen.getByText(/optional, max 2000 characters/i)).toBeInTheDocument();
  });
});

describe('TaskForm - Title Validation Tests', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnSubmit.mockResolvedValue(undefined);
  });

  it('shows validation error for empty title', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('shows validation error when title is only whitespace', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, '   ');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('shows validation error for title exceeding 200 characters', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const longTitle = 'a'.repeat(201);
    await user.type(titleInput, longTitle);

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title must be 200 characters or less/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('accepts valid title with exactly 200 characters', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const validTitle = 'a'.repeat(200);
    await user.type(titleInput, validTitle);

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
    });

    expect(screen.queryByText(/title must be 200 characters or less/i)).not.toBeInTheDocument();
  });

  it('trims whitespace from title before validation', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, '  Valid Title  ');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Valid Title',
        })
      );
    });
  });

  it('clears validation error when valid title entered', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    // First submit with empty title to trigger error
    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    // Now enter valid title
    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Valid Task Title');

    await waitFor(() => {
      expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument();
    });
  });
});

describe('TaskForm - Description Validation Tests', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnSubmit.mockResolvedValue(undefined);
  });

  it('allows empty description', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Valid Title');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Valid Title',
          description: null,
        })
      );
    });
  });

  it('shows validation error for description exceeding 2000 characters', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Valid Title');

    const descriptionInput = screen.getByLabelText(/description/i);
    const longDescription = 'a'.repeat(2001);
    await user.type(descriptionInput, longDescription);

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/description must be 2000 characters or less/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('accepts valid description with exactly 2000 characters', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Valid Title');

    const descriptionInput = screen.getByLabelText(/description/i);
    const validDescription = 'a'.repeat(2000);
    await user.type(descriptionInput, validDescription);

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
    });

    expect(screen.queryByText(/description must be 2000 characters or less/i)).not.toBeInTheDocument();
  });

  it('trims whitespace from description before submission', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Valid Title');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, '  Valid description  ');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Valid description',
        })
      );
    });
  });

  it('converts empty string description to null', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Valid Title');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, '   '); // Only whitespace

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Valid Title',
          description: null,
        })
      );
    });
  });
});

describe('TaskForm - Form Submission Tests', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnSubmit.mockResolvedValue(undefined);
  });

  it('calls onSubmit with valid data', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, 'Task description');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'New Task Title',
        description: 'Task description',
      });
    });
  });

  it('calls onSubmit with title only (no description)', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'New Task Title',
        description: null,
      });
    });
  });

  it('submits form on Enter key in title field', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title{Enter}');

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'New Task Title',
        description: null,
      });
    });
  });

  it('resets form after successful submission for new task', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, 'Task description');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
    });

    // Form should be reset after successful submission
    await waitFor(() => {
      expect(titleInput).toHaveValue('');
      expect(descriptionInput).toHaveValue('');
    });
  });

  it('does not reset form after editing existing task', async () => {
    const user = userEvent.setup();
    const existingTask: Task = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      title: 'Existing Task',
      description: 'Existing description',
      is_complete: false,
      user_id: '123e4567-e89b-12d3-a456-426614174001',
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    };

    render(<TaskForm task={existingTask} onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.clear(titleInput);
    await user.type(titleInput, 'Updated Task Title');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled();
    });

    // Form should NOT be reset when editing
    await waitFor(() => {
      expect(titleInput).toHaveValue('Updated Task Title');
    });
  });
});

describe('TaskForm - Loading State Tests', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('disables submit button during submission', async () => {
    const user = userEvent.setup();
    let resolveSubmit: () => void;
    const submitPromise = new Promise<void>((resolve) => {
      resolveSubmit = resolve;
    });
    mockOnSubmit.mockReturnValue(submitPromise);

    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    // Button should be disabled during submission
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(screen.getByText(/saving\.\.\./i)).toBeInTheDocument();
    });

    // Resolve the promise
    resolveSubmit!();
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('disables input fields during submission', async () => {
    const user = userEvent.setup();
    let resolveSubmit: () => void;
    const submitPromise = new Promise<void>((resolve) => {
      resolveSubmit = resolve;
    });
    mockOnSubmit.mockReturnValue(submitPromise);

    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    // Inputs should be disabled during submission
    await waitFor(() => {
      expect(titleInput).toBeDisabled();
      expect(screen.getByLabelText(/description/i)).toBeDisabled();
    });

    // Resolve the promise
    resolveSubmit!();
    await waitFor(() => {
      expect(titleInput).not.toBeDisabled();
    });
  });

  it('disables cancel button during submission', async () => {
    const user = userEvent.setup();
    const mockOnCancel = vi.fn();
    let resolveSubmit: () => void;
    const submitPromise = new Promise<void>((resolve) => {
      resolveSubmit = resolve;
    });
    mockOnSubmit.mockReturnValue(submitPromise);

    render(<TaskForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    // Cancel button should be disabled during submission
    await waitFor(() => {
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      expect(cancelButton).toBeDisabled();
    });

    // Resolve the promise
    resolveSubmit!();
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('shows loading text on submit button during submission', async () => {
    const user = userEvent.setup();
    let resolveSubmit: () => void;
    const submitPromise = new Promise<void>((resolve) => {
      resolveSubmit = resolve;
    });
    mockOnSubmit.mockReturnValue(submitPromise);

    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'New Task Title');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/saving\.\.\./i)).toBeInTheDocument();
      expect(screen.queryByText(/save task/i)).not.toBeInTheDocument();
    });

    // Resolve the promise
    resolveSubmit!();
    await waitFor(() => {
      expect(screen.queryByText(/saving\.\.\./i)).not.toBeInTheDocument();
    });
  });
});

describe('TaskForm - Cancel Button Tests', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls onCancel when cancel button clicked', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('does not submit form when cancel button clicked', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Some Task');

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });
});

describe('TaskForm - Accessibility Tests', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('has proper form labels', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
  });

  it('marks required field with asterisk', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleLabel = screen.getByText(/title/i);
    expect(titleLabel.parentElement).toContainHTML('*');
  });

  it('marks optional field clearly', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText(/\(optional\)/i)).toBeInTheDocument();
  });

  it('error messages are associated with inputs', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      const titleInput = screen.getByLabelText(/title/i);
      const errorMessage = screen.getByText(/title is required/i);
      expect(errorMessage).toBeInTheDocument();
      // Error should be close to the input
      expect(titleInput.parentElement).toContainElement(errorMessage);
    });
  });
});

describe('TaskForm - Edge Cases', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnSubmit.mockResolvedValue(undefined);
  });

  it('handles special characters in title', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Task with special chars: @#$%^&*()');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Task with special chars: @#$%^&*()',
        })
      );
    });
  });

  it('handles unicode characters in description', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Task');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, 'Unicode: 你好 🎉 مرحبا');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Unicode: 你好 🎉 مرحبا',
        })
      );
    });
  });

  it('handles line breaks in description', async () => {
    const user = userEvent.setup();
    render(<TaskForm onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    await user.type(titleInput, 'Task');

    const descriptionInput = screen.getByLabelText(/description/i);
    await user.type(descriptionInput, 'Line 1{Enter}Line 2{Enter}Line 3');

    const submitButton = screen.getByRole('button', { name: /save task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          description: expect.stringContaining('Line 1'),
        })
      );
    });
  });
});
