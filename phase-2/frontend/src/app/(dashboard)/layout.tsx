/**
 * Dashboard Layout
 *
 * Wraps all dashboard routes with:
 * - Background gradient
 * - Main content container
 */

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-neutral-950 dark:via-neutral-900 dark:to-neutral-950">
      {children}
    </div>
  );
}
