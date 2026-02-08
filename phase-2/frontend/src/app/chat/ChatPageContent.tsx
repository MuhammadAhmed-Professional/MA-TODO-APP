/**
 * Chat Page - AI-Powered Todo Assistant
 *
 * Phase III: Conversational interface for managing tasks via natural language.
 * Uses OpenAI Agents SDK on the backend with MCP tools for task operations.
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChatBot } from "@/components/chat/ChatBot";
import { Header } from "@/components/layout/Header";
import { getAuthToken } from "@/lib/token-storage";
import { fetchAPI } from "@/lib/api";
import type { TranslationValues } from "next-intl";

interface ChatPageContentProps {
  translations: (key: string, values?: TranslationValues) => string;
}

export default function ChatPage({ translations: t }: ChatPageContentProps) {
  const router = useRouter();
  const [userId, setUserId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      try {
        // Use stored token + backend session validation (same as task API)
        const token = getAuthToken();
        if (!token) {
          router.push("/login");
          return;
        }
        const userData = await fetchAPI<{ id: string }>("/api/auth/get-session");
        if (userData?.id) {
          setUserId(userData.id);
        } else {
          router.push("/login");
        }
      } catch {
        router.push("/login");
      } finally {
        setIsLoading(false);
      }
    }
    checkAuth();
  }, [router]);

  if (isLoading) {
    return (
      <>
        <Header />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-neutral-300 border-t-blue-500" />
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <ChatBot userId={userId} translations={t} />
    </>
  );
}
