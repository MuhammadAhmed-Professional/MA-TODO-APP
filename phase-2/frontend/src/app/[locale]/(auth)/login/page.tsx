"use client";

import { useTranslations } from 'next-intl';
import dynamic from "next/dynamic";

const LoginPageContent = dynamic(() => import("@/components/pages/LoginPageContent").then(m => ({ default: m.LoginPageContent })), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  ),
});

export default function LoginPage() {
  const t = useTranslations('auth');

  return <LoginPageContent translations={t} />;
}
