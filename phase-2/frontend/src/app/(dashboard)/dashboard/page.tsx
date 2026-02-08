import { redirect } from 'next/navigation';

/**
 * Dashboard Page - Redirects to localized version
 */
export default function DashboardPage() {
  redirect('/en/dashboard');
}
