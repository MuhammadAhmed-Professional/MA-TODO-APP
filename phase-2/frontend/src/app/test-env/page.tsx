import { redirect } from 'next/navigation';

/**
 * Test Env Page - Redirects to localized version
 */
export default function TestEnvPage() {
  redirect('/en/test-env');
}
