/**
 * Unit Tests for SignupForm Component (T038)
 *
 * Tests form validation, user interactions, and submission behavior.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SignupForm } from '@/components/auth/SignupForm';

// Mock next/navigation
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock API module
vi.mock('@/lib/api', () => ({
  api: {
    post: vi.fn(),
  },
}));

import { api } from '@/lib/api';

describe('SignupForm - Validation Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display error when name is empty', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const nameInput = screen.getByLabelText(/name/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    // Focus and blur without entering text
    await user.click(nameInput);
    await user.tab();

    // Try to submit
    await user.click(submitButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
    });
  });

  it('should display error when name exceeds 100 characters', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const nameInput = screen.getByLabelText(/name/i);
    const longName = 'a'.repeat(101);

    await user.type(nameInput, longName);
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText(/name must be 100 characters or less/i)).toBeInTheDocument();
    });
  });

  it('should accept valid name (1-100 characters)', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const nameInput = screen.getByLabelText(/name/i);
    await user.type(nameInput, 'Alice Smith');
    await user.tab();

    // Should not show error
    await waitFor(() => {
      expect(screen.queryByText(/name is required/i)).not.toBeInTheDocument();
    });
  });

  it('should display error when email is empty', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    await user.click(emailInput);
    await user.tab();
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });
  });

  it('should display error for invalid email format', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, 'not-an-email');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });
  });

  it('should accept valid email address', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, 'alice@example.com');
    await user.tab();

    await waitFor(() => {
      expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument();
    });
  });

  it('should display error when password is less than 8 characters', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const passwordInput = screen.getByLabelText(/^password$/i);
    await user.type(passwordInput, 'short');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it('should accept password with 8 or more characters', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const passwordInput = screen.getByLabelText(/^password$/i);
    await user.type(passwordInput, 'SecurePass123!');
    await user.tab();

    await waitFor(() => {
      expect(screen.queryByText(/password must be at least 8 characters/i)).not.toBeInTheDocument();
    });
  });

  it('should display error when confirm password does not match', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    await user.type(passwordInput, 'SecurePass123!');
    await user.type(confirmPasswordInput, 'DifferentPass456!');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it('should not display error when passwords match', async () => {
    const user = userEvent.setup();
    render(<SignupForm />);

    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

    await user.type(passwordInput, 'SecurePass123!');
    await user.type(confirmPasswordInput, 'SecurePass123!');
    await user.tab();

    await waitFor(() => {
      expect(screen.queryByText(/passwords do not match/i)).not.toBeInTheDocument();
    });
  });
});

describe('SignupForm - Submission Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should submit form with valid data and redirect to dashboard', async () => {
    const user = userEvent.setup();

    // Mock successful API response
    const mockResponse = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      email: 'alice@example.com',
      name: 'Alice Smith',
      created_at: '2025-12-07T12:00:00Z',
      updated_at: '2025-12-07T12:00:00Z',
    };
    vi.mocked(api.post).mockResolvedValue(mockResponse);

    render(<SignupForm />);

    // Fill in form
    await user.type(screen.getByLabelText(/name/i), 'Alice Smith');
    await user.type(screen.getByLabelText(/email/i), 'alice@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'SecurePass123!');
    await user.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    await user.click(submitButton);

    // Should call API with correct data
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/auth/signup', {
        name: 'Alice Smith',
        email: 'alice@example.com',
        password: 'SecurePass123!',
      });
    });

    // Should redirect to dashboard
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should display error message when API call fails', async () => {
    const user = userEvent.setup();

    // Mock API error
    const mockError = new Error('Email already registered. Please login or use a different email.');
    vi.mocked(api.post).mockRejectedValue(mockError);

    render(<SignupForm />);

    // Fill in form
    await user.type(screen.getByLabelText(/name/i), 'Bob Smith');
    await user.type(screen.getByLabelText(/email/i), 'existing@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'SecurePass123!');
    await user.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!');

    // Submit form
    await user.click(screen.getByRole('button', { name: /sign up/i }));

    // Should display error message
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        /email already registered/i
      );
    });

    // Should NOT redirect
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should disable submit button while submitting', async () => {
    const user = userEvent.setup();

    // Mock slow API call
    vi.mocked(api.post).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<SignupForm />);

    // Fill in form
    await user.type(screen.getByLabelText(/name/i), 'Charlie');
    await user.type(screen.getByLabelText(/email/i), 'charlie@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'SecurePass123!');
    await user.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    await user.click(submitButton);

    // Button should be disabled and show loading state
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent(/creating account/i);
    });
  });

  it('should clear error when user starts typing after error', async () => {
    const user = userEvent.setup();

    // Mock API error
    vi.mocked(api.post).mockRejectedValue(new Error('Signup failed'));

    render(<SignupForm />);

    // Submit form with errors
    await user.type(screen.getByLabelText(/name/i), 'Test User');
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign up/i }));

    // Error should appear
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    // Re-submit should clear error before making new request
    vi.mocked(api.post).mockResolvedValue({
      id: '123',
      email: 'test@example.com',
      name: 'Test User',
      created_at: '2025-12-07T12:00:00Z',
      updated_at: '2025-12-07T12:00:00Z',
    });

    await user.click(screen.getByRole('button', { name: /sign up/i }));

    // Error should be cleared
    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });
});
