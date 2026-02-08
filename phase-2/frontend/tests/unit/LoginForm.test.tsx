/**
 * Unit Tests for LoginForm Component (T039)
 *
 * Tests form validation, user interactions, and submission behavior.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { LoginForm } from '@/components/auth/LoginForm';

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

describe('LoginForm - Email Validation Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display error when email is empty', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    // Click and blur email input without entering text
    await user.click(emailInput);
    await user.tab();

    // Try to submit
    await user.click(submitButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });
  });

  it('should display error for invalid email format', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);

    await user.type(emailInput, 'not-an-email');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });
  });

  it('should accept valid email address', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, 'user@example.com');
    await user.tab();

    await waitFor(() => {
      expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument();
    });
  });

  it('should validate various email formats', async () => {
    const user = userEvent.setup();

    const validEmails = [
      'simple@example.com',
      'user.name@example.com',
      'user+tag@example.co.uk',
      'user123@subdomain.example.com',
    ];

    for (const email of validEmails) {
      const { unmount } = render(<LoginForm />);
      const emailInput = screen.getByLabelText(/email/i);

      await user.clear(emailInput);
      await user.type(emailInput, email);
      await user.tab();

      await waitFor(() => {
        expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument();
      });

      unmount();
    }
  });
});

describe('LoginForm - Password Validation Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should display error when password is empty', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /log in/i });

    // Click and blur without entering text
    await user.click(passwordInput);
    await user.tab();

    // Try to submit
    await user.click(submitButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it('should accept any non-empty password', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const passwordInput = screen.getByLabelText(/password/i);

    // Login form only checks if password is provided (no min length on login)
    await user.type(passwordInput, 'anypassword');
    await user.tab();

    await waitFor(() => {
      expect(screen.queryByText(/password is required/i)).not.toBeInTheDocument();
    });
  });
});

describe('LoginForm - Form Submission Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should submit form with valid credentials and redirect to dashboard', async () => {
    const user = userEvent.setup();

    // Mock successful API response
    const mockResponse = {
      id: '123e4567-e89b-12d3-a456-426614174000',
      email: 'user@example.com',
      name: 'Test User',
      created_at: '2025-12-07T12:00:00Z',
      updated_at: '2025-12-07T12:00:00Z',
    };
    vi.mocked(api.post).mockResolvedValue(mockResponse);

    render(<LoginForm />);

    // Fill in form
    await user.type(screen.getByLabelText(/email/i), 'user@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /log in/i });
    await user.click(submitButton);

    // Should call API with correct data
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/auth/login', {
        email: 'user@example.com',
        password: 'password123',
      });
    });

    // Should redirect to dashboard
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should display error message when credentials are invalid', async () => {
    const user = userEvent.setup();

    // Mock API error (401 Unauthorized)
    const mockError = new Error('Invalid email or password');
    vi.mocked(api.post).mockRejectedValue(mockError);

    render(<LoginForm />);

    // Fill in form with invalid credentials
    await user.type(screen.getByLabelText(/email/i), 'wrong@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword');

    // Submit form
    await user.click(screen.getByRole('button', { name: /log in/i }));

    // Should display error message
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/invalid email or password/i);
    });

    // Should NOT redirect
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should display generic error message when API call fails', async () => {
    const user = userEvent.setup();

    // Mock network error
    const mockError = new Error('Network error');
    vi.mocked(api.post).mockRejectedValue(mockError);

    render(<LoginForm />);

    // Fill in form
    await user.type(screen.getByLabelText(/email/i), 'user@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    // Submit form
    await user.click(screen.getByRole('button', { name: /log in/i }));

    // Should display error message
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/network error/i);
    });
  });

  it('should disable submit button while logging in', async () => {
    const user = userEvent.setup();

    // Mock slow API call
    vi.mocked(api.post).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(<LoginForm />);

    // Fill in form
    await user.type(screen.getByLabelText(/email/i), 'user@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /log in/i });
    await user.click(submitButton);

    // Button should be disabled and show loading state
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent(/logging in/i);
    });
  });

  it('should clear previous error on new submission', async () => {
    const user = userEvent.setup();

    // First attempt: API error
    vi.mocked(api.post).mockRejectedValue(new Error('Login failed'));

    render(<LoginForm />);

    await user.type(screen.getByLabelText(/email/i), 'user@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpass');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    // Error should appear
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    // Second attempt: successful login
    vi.mocked(api.post).mockResolvedValue({
      id: '123',
      email: 'user@example.com',
      name: 'Test User',
      created_at: '2025-12-07T12:00:00Z',
      updated_at: '2025-12-07T12:00:00Z',
    });

    // Clear password and retry
    await user.clear(screen.getByLabelText(/password/i));
    await user.type(screen.getByLabelText(/password/i), 'correctpass');
    await user.click(screen.getByRole('button', { name: /log in/i }));

    // Error should be cleared
    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });

  it('should not submit form with validation errors', async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const submitButton = screen.getByRole('button', { name: /log in/i });

    // Try to submit without filling anything
    await user.click(submitButton);

    // API should not be called
    expect(api.post).not.toHaveBeenCalled();

    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });
});

describe('LoginForm - Accessibility Tests', () => {
  it('should have proper form labels', () => {
    render(<LoginForm />);

    // All inputs should have associated labels
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('should have proper input types', () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    expect(emailInput).toHaveAttribute('type', 'email');
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('should have autocomplete attributes', () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    expect(emailInput).toHaveAttribute('autocomplete', 'email');
    expect(passwordInput).toHaveAttribute('autocomplete', 'current-password');
  });

  it('should have submit button with proper role', () => {
    render(<LoginForm />);

    const submitButton = screen.getByRole('button', { name: /log in/i });
    expect(submitButton).toHaveAttribute('type', 'submit');
  });
});
