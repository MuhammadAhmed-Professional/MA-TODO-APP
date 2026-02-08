/**
 * Root Layout - Pass-through to locale layouts
 *
 * This layout is required by Next.js but all rendering
 * is handled by [locale]/layout.tsx which provides
 * the <html> and <body> tags.
 *
 * The next-intl middleware handles redirecting / to /en.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
