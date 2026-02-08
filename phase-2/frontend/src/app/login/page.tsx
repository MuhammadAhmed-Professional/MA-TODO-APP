import { redirect } from 'next/navigation';

/**
 * Login Page - Redirects to localized version
 */
export default function LoginPage() {
  redirect('/en/login');
}
