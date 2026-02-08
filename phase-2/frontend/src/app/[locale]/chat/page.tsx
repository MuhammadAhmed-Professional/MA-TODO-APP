"use client";

import { useTranslations } from 'next-intl';
import dynamic from "next/dynamic";

const ChatPageContent = dynamic(() => import("@/components/pages/ChatPageContent").then(m => ({ default: m.ChatPageContent })), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
    </div>
  ),
});

export default function ChatPage() {
  const t = useTranslations('chat');

  return <ChatPageContent translations={t} />;
}
