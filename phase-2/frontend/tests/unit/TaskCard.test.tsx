/**
 * Unit Tests for TaskCard Component (T063)
 *
 * Tests rendering, completion status, and user interactions (edit, delete, toggle).
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TaskCard } from '@/components/tasks/TaskCard';
import { Task } from '@/types/task';

// Mock window.confirm
const mockConfirm = vi.spyOn(window, 'confirm');

describe('TaskCard - Rendering Tests', () => {
  const mockTask: Task = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    title: 'Test Task Title',
    description: 'Test task description',
    is_complete: false,
    user_id: '123e4567-e89b-12d3-a456-426614174001',
    created_at: '2025-01-01T10:00:00Z',
    updated_at: '2025-01-01T10:00:00Z',
  };

  const mockOnToggleComplete = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockConfirm.mockImplementation(() => true);
  });

  it('renders task title and description', () => {
    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Test Task Title')).toBeInTheDocument();
    expect(screen.getByText('Test task description')).toBeInTheDocument();
  });

  it('renders task without description', () => {
    const taskWithoutDescription: Task = {
      ...mockTask,
      description: null,
    };

    render(
      <TaskCard
        task={taskWithoutDescription}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Test Task Title')).toBeInTheDocument();
    expect(screen.queryByText('Test task description')).not.toBeInTheDocument();
  });

  it('renders created and updated dates', () => {
    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText(/Created:/)).toBeInTheDocument();
    expect(screen.getByText(/Jan 1, 2025/)).toBeInTheDocument();
  });

  it('shows updated date when different from created date', () => {
    const updatedTask: Task = {
      ...mockTask,
      updated_at: '2025-01-02T15:30:00Z',
    };

    render(
      <TaskCard
        task={updatedTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText(/Updated:/)).toBeInTheDocument();
    expect(screen.getByText(/Jan 2, 2025/)).toBeInTheDocument();
  });
});

describe('TaskCard - Completion Status Tests', () => {
  const mockOnToggleComplete = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders incomplete task without checkmark', () => {
    const incompleteTask: Task = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      title: 'Incomplete Task',
      description: 'Not done yet',
      is_complete: false,
      user_id: '123e4567-e89b-12d3-a456-426614174001',
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    };

    render(
      <TaskCard
        task={incompleteTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const checkbox = screen.getByRole('button', { name: /mark as complete/i });
    expect(checkbox).toBeInTheDocument();
    expect(screen.getByText('Incomplete Task')).not.toHaveClass('line-through');
  });

  it('renders complete task with checkmark and strikethrough', () => {
    const completeTask: Task = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      title: 'Complete Task',
      description: 'All done!',
      is_complete: true,
      user_id: '123e4567-e89b-12d3-a456-426614174001',
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    };

    render(
      <TaskCard
        task={completeTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const checkbox = screen.getByRole('button', { name: /mark as incomplete/i });
    expect(checkbox).toBeInTheDocument();
    expect(screen.getByText('Complete Task')).toHaveClass('line-through');
  });

  it('applies correct styling to complete task', () => {
    const completeTask: Task = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      title: 'Complete Task',
      description: 'All done!',
      is_complete: true,
      user_id: '123e4567-e89b-12d3-a456-426614174001',
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    };

    render(
      <TaskCard
        task={completeTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    // Title should have line-through and gray color
    const title = screen.getByText('Complete Task');
    expect(title).toHaveClass('text-gray-500');
    expect(title).toHaveClass('line-through');

    // Description should have gray color
    const description = screen.getByText('All done!');
    expect(description).toHaveClass('text-gray-400');
  });
});

describe('TaskCard - Toggle Complete Interaction', () => {
  const mockTask: Task = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    title: 'Test Task',
    description: 'Test description',
    is_complete: false,
    user_id: '123e4567-e89b-12d3-a456-426614174001',
    created_at: '2025-01-01T10:00:00Z',
    updated_at: '2025-01-01T10:00:00Z',
  };

  const mockOnToggleComplete = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnToggleComplete.mockResolvedValue(undefined);
  });

  it('calls onToggleComplete when checkbox clicked (mark as complete)', async () => {
    const user = userEvent.setup();

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const checkbox = screen.getByRole('button', { name: /mark as complete/i });
    await user.click(checkbox);

    await waitFor(() => {
      expect(mockOnToggleComplete).toHaveBeenCalledWith('123e4567-e89b-12d3-a456-426614174000', true);
      expect(mockOnToggleComplete).toHaveBeenCalledTimes(1);
    });
  });

  it('calls onToggleComplete when checkbox clicked (mark as incomplete)', async () => {
    const user = userEvent.setup();
    const completeTask: Task = { ...mockTask, is_complete: true };

    render(
      <TaskCard
        task={completeTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const checkbox = screen.getByRole('button', { name: /mark as incomplete/i });
    await user.click(checkbox);

    await waitFor(() => {
      expect(mockOnToggleComplete).toHaveBeenCalledWith('123e4567-e89b-12d3-a456-426614174000', false);
      expect(mockOnToggleComplete).toHaveBeenCalledTimes(1);
    });
  });

  it('disables checkbox during toggle operation', async () => {
    const user = userEvent.setup();
    let resolveToggle: () => void;
    const togglePromise = new Promise<void>((resolve) => {
      resolveToggle = resolve;
    });
    mockOnToggleComplete.mockReturnValue(togglePromise);

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const checkbox = screen.getByRole('button', { name: /mark as complete/i });
    await user.click(checkbox);

    // Checkbox should be disabled during operation
    expect(checkbox).toBeDisabled();

    // Resolve the promise
    resolveToggle!();
    await waitFor(() => {
      expect(checkbox).not.toBeDisabled();
    });
  });
});

describe('TaskCard - Edit Button Interaction', () => {
  const mockTask: Task = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    title: 'Test Task',
    description: 'Test description',
    is_complete: false,
    user_id: '123e4567-e89b-12d3-a456-426614174001',
    created_at: '2025-01-01T10:00:00Z',
    updated_at: '2025-01-01T10:00:00Z',
  };

  const mockOnToggleComplete = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls onEdit when edit button clicked', async () => {
    const user = userEvent.setup();

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const editButton = screen.getByRole('button', { name: /edit task/i });
    await user.click(editButton);

    expect(mockOnEdit).toHaveBeenCalledWith(mockTask);
    expect(mockOnEdit).toHaveBeenCalledTimes(1);
  });

  it('passes entire task object to onEdit', async () => {
    const user = userEvent.setup();

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const editButton = screen.getByRole('button', { name: /edit task/i });
    await user.click(editButton);

    expect(mockOnEdit).toHaveBeenCalledWith(
      expect.objectContaining({
        id: '123e4567-e89b-12d3-a456-426614174000',
        title: 'Test Task',
        description: 'Test description',
      })
    );
  });
});

describe('TaskCard - Delete Button Interaction', () => {
  const mockTask: Task = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    title: 'Test Task',
    description: 'Test description',
    is_complete: false,
    user_id: '123e4567-e89b-12d3-a456-426614174001',
    created_at: '2025-01-01T10:00:00Z',
    updated_at: '2025-01-01T10:00:00Z',
  };

  const mockOnToggleComplete = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockOnDelete.mockResolvedValue(undefined);
    mockConfirm.mockImplementation(() => true);
  });

  it('shows confirmation dialog before delete', async () => {
    const user = userEvent.setup();

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByRole('button', { name: /delete task/i });
    await user.click(deleteButton);

    expect(mockConfirm).toHaveBeenCalledWith(
      'Are you sure you want to delete "Test Task"? This action cannot be undone.'
    );
  });

  it('calls onDelete when confirmation accepted', async () => {
    const user = userEvent.setup();
    mockConfirm.mockReturnValue(true);

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByRole('button', { name: /delete task/i });
    await user.click(deleteButton);

    await waitFor(() => {
      expect(mockOnDelete).toHaveBeenCalledWith('123e4567-e89b-12d3-a456-426614174000');
      expect(mockOnDelete).toHaveBeenCalledTimes(1);
    });
  });

  it('does not call onDelete when confirmation cancelled', async () => {
    const user = userEvent.setup();
    mockConfirm.mockReturnValue(false);

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByRole('button', { name: /delete task/i });
    await user.click(deleteButton);

    expect(mockOnDelete).not.toHaveBeenCalled();
  });

  it('shows loading spinner during delete operation', async () => {
    const user = userEvent.setup();
    let resolveDelete: () => void;
    const deletePromise = new Promise<void>((resolve) => {
      resolveDelete = resolve;
    });
    mockOnDelete.mockReturnValue(deletePromise);
    mockConfirm.mockReturnValue(true);

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByRole('button', { name: /delete task/i });
    await user.click(deleteButton);

    // Should show loading state
    await waitFor(() => {
      expect(deleteButton).toBeDisabled();
    });

    // Resolve the promise
    resolveDelete!();
    await waitFor(() => {
      expect(deleteButton).not.toBeDisabled();
    });
  });

  it('disables all buttons during delete operation', async () => {
    const user = userEvent.setup();
    let resolveDelete: () => void;
    const deletePromise = new Promise<void>((resolve) => {
      resolveDelete = resolve;
    });
    mockOnDelete.mockReturnValue(deletePromise);
    mockConfirm.mockReturnValue(true);

    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const deleteButton = screen.getByRole('button', { name: /delete task/i });
    await user.click(deleteButton);

    await waitFor(() => {
      const editButton = screen.getByRole('button', { name: /edit task/i });
      const checkbox = screen.getByRole('button', { name: /mark as complete/i });

      expect(deleteButton).toBeDisabled();
      expect(editButton).toBeDisabled();
      expect(checkbox).toBeDisabled();
    });

    // Resolve the promise
    resolveDelete!();
    await waitFor(() => {
      expect(deleteButton).not.toBeDisabled();
    });
  });
});

describe('TaskCard - Accessibility Tests', () => {
  const mockTask: Task = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    title: 'Test Task',
    description: 'Test description',
    is_complete: false,
    user_id: '123e4567-e89b-12d3-a456-426614174001',
    created_at: '2025-01-01T10:00:00Z',
    updated_at: '2025-01-01T10:00:00Z',
  };

  const mockOnToggleComplete = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('has accessible button labels for incomplete task', () => {
    render(
      <TaskCard
        task={mockTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByRole('button', { name: /mark as complete/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /edit task/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /delete task/i })).toBeInTheDocument();
  });

  it('has accessible button labels for complete task', () => {
    const completeTask: Task = { ...mockTask, is_complete: true };

    render(
      <TaskCard
        task={completeTask}
        onToggleComplete={mockOnToggleComplete}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByRole('button', { name: /mark as incomplete/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /edit task/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /delete task/i })).toBeInTheDocument();
  });
});
