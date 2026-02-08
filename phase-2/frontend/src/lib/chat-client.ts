/**
 * Chat client for AI-powered conversational todo management.
 *
 * Manages chat conversations with the AI assistant via the backend API:
 * - POST /api/chat/conversations - create new conversation
 * - POST /api/chat/conversations/{id}/messages - send message & get response
 * - GET /api/chat/conversations/{id}/messages - load history
 * - GET /api/chat/conversations - list conversations
 *
 * @module chat-client
 */

"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { fetchAPI, APIError } from "./api";

/** Message structure for chat conversations. */
export interface ChatMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  tool_calls?: ToolCall[] | null;
  created_at?: string;
}

interface ToolCall {
  id: string;
  name: string;
  result: Record<string, unknown>;
}

interface ConversationResponse {
  id: string;
  user_id: string;
  title: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

interface SendMessageResponse {
  success: boolean;
  conversation_id: string;
  user_message: {
    id: string;
    role: string;
    content: string;
    created_at: string;
  };
  assistant_message: {
    id: string;
    role: string;
    content: string;
    tool_calls: ToolCall[];
    created_at: string;
  };
}

interface MessageResponse {
  id: string;
  conversation_id: string;
  user_id: string;
  role: string;
  content: string;
  tool_calls: Record<string, unknown> | null;
  created_at: string;
}

const CONVERSATION_ID_KEY = "chat_conversation_id";

export function getStoredConversationId(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(CONVERSATION_ID_KEY);
  } catch {
    return null;
  }
}

export function storeConversationId(id: string): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(CONVERSATION_ID_KEY, id);
  } catch {}
}

export function clearStoredConversationId(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(CONVERSATION_ID_KEY);
  } catch {}
}

/** Create a new conversation via the backend API. */
async function createConversation(title?: string): Promise<ConversationResponse> {
  return fetchAPI<ConversationResponse>("/api/chat/conversations", {
    method: "POST",
    body: JSON.stringify({ title: title || null }),
  });
}

/** Send a message to an existing conversation and get the AI response. */
async function sendMessageToConversation(
  conversationId: string,
  content: string
): Promise<SendMessageResponse> {
  return fetchAPI<SendMessageResponse>(
    `/api/chat/conversations/${conversationId}/messages`,
    {
      method: "POST",
      body: JSON.stringify({ content }),
    }
  );
}

/** Load message history for a conversation. */
async function loadConversationMessages(
  conversationId: string
): Promise<MessageResponse[]> {
  return fetchAPI<MessageResponse[]>(
    `/api/chat/conversations/${conversationId}/messages`
  );
}

/**
 * Custom hook for managing chat state and API calls.
 *
 * @param userId - Current user's ID (from auth session)
 * @returns Chat interface with messages, send, and new conversation controls
 */
export function useChatClient(userId: string | undefined) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const initialized = useRef(false);

  // Restore conversation from localStorage on mount
  useEffect(() => {
    if (initialized.current || !userId) return;
    initialized.current = true;

    const storedId = getStoredConversationId();
    if (storedId) {
      setConversationId(storedId);
      setIsLoadingHistory(true);
      loadConversationMessages(storedId)
        .then((msgs) => {
          setMessages(
            msgs.map((m) => ({
              id: m.id,
              role: m.role as "user" | "assistant",
              content: m.content,
              created_at: m.created_at,
            }))
          );
        })
        .catch(() => {
          // Conversation may no longer exist; start fresh
          clearStoredConversationId();
          setConversationId(null);
        })
        .finally(() => setIsLoadingHistory(false));
    }
  }, [userId]);

  const sendMessage = useCallback(
    async (message: string) => {
      if (!userId) {
        setError("You must be logged in to chat.");
        return;
      }

      setError(null);
      setIsLoading(true);

      // Optimistically add user message
      const userMsg: ChatMessage = { role: "user", content: message };
      setMessages((prev) => [...prev, userMsg]);

      try {
        let activeConvId = conversationId;

        // Create conversation if none exists
        if (!activeConvId) {
          const conv = await createConversation(message.slice(0, 50));
          activeConvId = conv.id;
          setConversationId(activeConvId);
          storeConversationId(activeConvId);
        }

        // Send message and get AI response
        const response = await sendMessageToConversation(activeConvId, message);

        const assistantMsg: ChatMessage = {
          id: response.assistant_message.id,
          role: "assistant",
          content: response.assistant_message.content,
          tool_calls: response.assistant_message.tool_calls,
          created_at: response.assistant_message.created_at,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        // Remove optimistic user message
        setMessages((prev) => prev.slice(0, -1));

        if (err instanceof APIError) {
          if (err.status === 401) {
            setError("Session expired. Please log in again.");
          } else if (err.status === 429) {
            setError("Too many messages. Please wait a moment.");
          } else {
            setError(err.message);
          }
        } else {
          setError("Failed to send message. Please try again.");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [userId, conversationId]
  );

  const startNewConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    clearStoredConversationId();
    setError(null);
  }, []);

  return {
    messages,
    conversationId,
    isLoading,
    isLoadingHistory,
    error,
    sendMessage,
    startNewConversation,
  };
}
