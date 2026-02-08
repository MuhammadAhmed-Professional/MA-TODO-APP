"use client";

import { useTranslations } from 'next-intl';
import dynamic from "next/dynamic";

const SignupPageContent = dynamic(() => import("@/components/pages/SignupPageContent").then(m => ({ default: m.SignupPageContent })), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  ),
});

export default function SignupPage() {
  const t = useTranslations('auth');

  return <SignupPageContent translations={t} />;
}
