/**
 * Custom Chat Transport for Vercel AI SDK v6.0
 *
 * Simplified implementation that works with the FastAPI backend.
 * Since the backend doesn't support streaming, we convert the response
 * into a simulated stream.
 *
 * @module chat-transport
 */

import type {
  ChatTransport,
  ChatRequestOptions,
  UIMessage,
  UIMessageChunk,
} from "ai";
import { getAuthToken } from "@/lib/token-storage";
import { fetchWithRetry } from "@/lib/api";

interface FastApiChatTransportOptions {
  api: string;
  userId?: string;
  credentials?: RequestCredentials;
  headers?: Record<string, string>;
}

interface SendMessageBody {
  content: string;
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

interface ToolCall {
  id: string;
  name: string;
  result: Record<string, unknown>;
}

/**
 * Custom transport that bridges useChat with FastAPI backend
 */
export class FastApiChatTransport implements ChatTransport<UIMessage> {
  private api: string;
  private userId?: string;
  private credentials?: RequestCredentials;
  private headers?: Record<string, string>;
  private conversationId: string | null = null;

  constructor(options: FastApiChatTransportOptions) {
    this.api = options.api;
    this.userId = options.userId;
    this.credentials = options.credentials;
    this.headers = options.headers;
  }

  /**
   * Build headers with auth token from localStorage
   */
  private getRequestHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...this.headers,
    };
    const token = getAuthToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  /**
   * Create a new conversation
   * Uses retry logic to handle Railway cold starts
   */
  private async createConversation(title?: string): Promise<string> {
    const response = await fetchWithRetry(
      `${this.api}/conversations`,
      {
        method: "POST",
        headers: this.getRequestHeaders(),
        credentials: this.credentials || "include",
        body: JSON.stringify({ title: title || null }),
      },
      3, // Max retries
      2000 // Base delay
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to create conversation");
    }

    const data = await response.json();
    return data.id;
  }

  /**
   * Extract text content from UIMessage parts
   */
  private getTextFromMessage(message: UIMessage): string {
    return message.parts
      .filter((part): part is { type: "text"; text: string } => part.type === "text")
      .map((part) => part.text)
      .join(" ");
  }

  /**
   * Send messages to the backend and get the AI response
   * This implements the ChatTransport interface for AI SDK v6.0
   */
  async sendMessages(
    options: {
      messages: UIMessage[];
      trigger: "submit-message" | "regenerate-message";
      chatId: string;
      messageId?: string;
      abortSignal?: AbortSignal;
    } & ChatRequestOptions
  ): Promise<ReadableStream<UIMessageChunk>> {
    const { messages, abortSignal } = options;
    const lastMessage = messages[messages.length - 1];

    if (!lastMessage || lastMessage.role !== "user") {
      throw new Error("Last message must be from user");
    }

    // Extract text content from the user message
    const userContent = this.getTextFromMessage(lastMessage);

    try {
      // Create conversation if none exists
      if (!this.conversationId) {
        this.conversationId = await this.createConversation(userContent.slice(0, 50));
        // Store in localStorage for persistence
        if (typeof window !== "undefined") {
          try {
            localStorage.setItem("chat_conversation_id", this.conversationId);
          } catch {
            // Ignore localStorage errors
          }
        }
      }

      // Send message to the conversation (with retry for cold starts)
      const response = await fetchWithRetry(
        `${this.api}/conversations/${this.conversationId}/messages`,
        {
          method: "POST",
          headers: this.getRequestHeaders(),
          credentials: this.credentials || "include",
          body: JSON.stringify({ content: userContent } as SendMessageBody),
          signal: abortSignal,
        },
        3, // Max retries
        2000 // Base delay
      );

      if (!response.ok) {
        const error = await response.json();
        // If conversation not found, clear it and retry
        if (response.status === 404) {
          this.conversationId = null;
          if (typeof window !== "undefined") {
            try {
              localStorage.removeItem("chat_conversation_id");
            } catch {
              // Ignore
            }
          }
          // Retry with new conversation
          return this.sendMessages(options);
        }
        throw new Error(error.detail || "Failed to send message");
      }

      const data = (await response.json()) as SendMessageResponse;

      // Create a readable stream for the assistant response only
      // User message is already shown in the UI when sent, don't duplicate it
      const stream = new ReadableStream<UIMessageChunk>({
        async start(controller) {
          try {
            const assistantId = data.assistant_message.id;

            // Send assistant message text in chunks for streaming effect
            controller.enqueue({
              type: "text-start",
              id: assistantId,
            });

            const content = data.assistant_message.content;
            const chunkSize = 20; // Send 20 chars at a time for effect
            for (let i = 0; i < content.length; i += chunkSize) {
              const chunk = content.slice(i, i + chunkSize);
              controller.enqueue({
                type: "text-delta",
                delta: chunk,
                id: assistantId,
              });
            }

            controller.enqueue({
              type: "text-end",
              id: assistantId,
            });

            controller.close();
          } catch (error) {
            controller.error(error);
          }
        },
      });

      return stream;
    } catch (error) {
      console.error("Chat transport error:", error);
      throw error;
    }
  }

  /**
   * Reconnect to an existing stream (not implemented for this backend)
   */
  async reconnectToStream(): Promise<ReadableStream<UIMessageChunk> | null> {
    // Our backend doesn't support reconnection to streams
    return null;
  }

  setConversationId(id: string | null) {
    this.conversationId = id;
  }

  getConversationId(): string | null {
    return this.conversationId;
  }
}

/**
 * Factory function to create a FastAPI chat transport
 */
export function createFastApiChatTransport(
  apiUrl: string,
  userId?: string
): FastApiChatTransport {
  return new FastApiChatTransport({
    api: apiUrl,
    userId,
    credentials: "include",
  });
}
