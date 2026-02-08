import { redirect } from 'next/navigation';

/**
 * Signup Page - Redirects to localized version
 */
export default function SignupPage() {
  redirect('/en/signup');
}
