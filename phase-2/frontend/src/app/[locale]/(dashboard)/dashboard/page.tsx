"use client";

import { useTranslations } from 'next-intl';
import dynamic from "next/dynamic";

const DashboardContent = dynamic(() => import("@/components/pages/DashboardPageContent").then(m => ({ default: m.DashboardPageContent })), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  ),
});

export default function DashboardPage() {
  const t = useTranslations('tasks');

  return <DashboardContent translations={t} />;
}
