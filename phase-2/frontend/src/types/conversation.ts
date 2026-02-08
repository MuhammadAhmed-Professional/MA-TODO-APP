/**
 * Conversation and Message types for Phase III AI Chatbot.
 * Matches backend models in src/models/conversation.py
 */

export interface Conversation {
  id: string;
  user_id: string;
  title: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  user_id: string;
  role: "user" | "assistant";
  content: string;
  tool_calls: ToolCallRecord | null;
  created_at: string;
}

export interface ToolCallRecord {
  tool_calls: Array<{
    id: string;
    type: string;
    function: {
      name: string;
      result: string;
    };
  }>;
}

export interface ConversationCreate {
  title?: string | null;
}

export interface MessageCreate {
  content: string;
}
