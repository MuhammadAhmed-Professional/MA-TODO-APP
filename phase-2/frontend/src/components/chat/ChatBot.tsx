/**
 * ChatBot Component - Enhanced with Vercel AI SDK v6.0
 *
 * Full-featured chat interface for AI-powered todo management.
 * Uses Vercel AI SDK's useChat hook with custom transport.
 * Integrates Web Speech API for voice input and output.
 */

"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  Plus,
  Loader2,
  Bot,
  User,
  AlertCircle,
  Settings,
  Volume2,
  VolumeX,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useChat } from "@ai-sdk/react";
import { createFastApiChatTransport } from "@/lib/chat-transport";
import { VoiceInput } from "./VoiceInput";
import { VoiceSettings } from "./VoiceSettings";
import { useSpeechSynthesis } from "@/hooks/useSpeechSynthesis";
import type { UIMessage } from "ai";

interface ChatBotProps {
  userId: string | undefined;
  translations?: any;
}

export function ChatBot({ userId, translations: t }: ChatBotProps) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [inputValue, setInputValue] = useState("");

  // Create custom transport for FastAPI backend
  const transport = useRef(
    createFastApiChatTransport(`${API_URL}/api/chat`, userId)
  );

  // Use Vercel AI SDK's useChat hook with new API v6.0
  const { messages, status, error, setMessages, sendMessage, stop } = useChat({
    transport: transport.current,
  });

  // Voice settings state
  const [voiceSettingsOpen, setVoiceSettingsOpen] = useState(false);
  const [recognitionLanguage, setRecognitionLanguage] = useState("en-US");
  const [synthesisEnabled, setSynthesisEnabled] = useState(false);
  const [synthesisLanguage, setSynthesisLanguage] = useState("en-US");
  const [voiceGender, setVoiceGender] = useState<"male" | "female" | "any">("any");

  // Speech synthesis
  const { speak, isSpeaking } = useSpeechSynthesis({
    language: synthesisLanguage,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLFormElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-speak AI responses when enabled
  useEffect(() => {
    if (synthesisEnabled && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === "assistant") {
        const content = getTextFromMessage(lastMessage);
        if (content) {
          speak(content);
        }
      }
    }
  }, [messages, synthesisEnabled, speak]);

  // Get text content from a message's parts
  const getTextFromMessage = (message: UIMessage): string => {
    return message.parts
      .filter((part): part is { type: "text"; text: string } => part.type === "text")
      .map((part) => part.text)
      .join("");
  };

  // Handle voice transcript
  const handleVoiceTranscript = (transcript: string) => {
    setInputValue(transcript);
  };

  // Handle new conversation
  const handleNewConversation = () => {
    setMessages([]);
    transport.current.setConversationId(null);
    // Clear localStorage
    if (typeof window !== "undefined") {
      try {
        localStorage.removeItem("chat_conversation_id");
      } catch {
        // Ignore localStorage errors
      }
    }
  };

  // Handle form submit
  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Stop any ongoing speech when user sends new message
    if (isSpeaking) {
      speak(""); // Cancel via the cancel call in useSpeechSynthesis
    }

    if (!inputValue.trim() || status === "streaming") return;

    // Send message using the new AI SDK API v6.0
    // sendMessage accepts an object with text property
    await sendMessage({ text: inputValue });
    setInputValue("");
  };

  const isLoading = status === "streaming" || status === "submitted";
  const hasError = status === "error";

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-200 dark:border-neutral-800">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
            <Bot className="h-4 w-4 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
              TaskFlow AI Assistant
            </h2>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              Manage your tasks with natural language
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Voice Settings Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setVoiceSettingsOpen(true)}
            className={cn(
              "gap-1.5 relative",
              synthesisEnabled &&
                "bg-purple-50 dark:bg-purple-950/30 border-purple-200 dark:border-purple-800"
            )}
            title="Voice settings"
          >
            {synthesisEnabled ? (
              <Volume2 className="h-3.5 w-3.5 text-purple-600 dark:text-purple-400" />
            ) : (
              <VolumeX className="h-3.5 w-3.5" />
            )}
            <Settings className="h-3.5 w-3.5" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleNewConversation}
            className="gap-1"
          >
            <Plus className="h-3.5 w-3.5" />
            New Chat
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 ? (
          <WelcomeMessage />
        ) : (
          messages.map((message, idx) => (
            <MessageBubble key={message.id || idx} message={message} />
          ))
        )}

        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="rounded-2xl rounded-tl-sm bg-neutral-100 dark:bg-neutral-800 px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-neutral-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        {hasError && error && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 text-sm">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error.message || "Failed to send message"}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-neutral-200 dark:border-neutral-800 px-4 py-3">
        <form onSubmit={onSubmit} className="flex items-end gap-2" ref={formRef}>
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type a message or use voice input... (e.g., 'Add a task to buy groceries')"
            className={cn(
              "flex-1 resize-none rounded-xl border border-neutral-300 dark:border-neutral-700",
              "bg-white dark:bg-neutral-900 px-4 py-2.5 text-sm",
              "placeholder:text-neutral-400 dark:placeholder:text-neutral-500",
              "focus:outline-none focus:ring-2 focus:ring-blue-500/50",
              "min-h-[42px] max-h-[120px]"
            )}
            disabled={isLoading || !userId}
          />

          {/* Voice Input */}
          <VoiceInput
            onTranscript={handleVoiceTranscript}
            language={recognitionLanguage}
            onLanguageChange={setRecognitionLanguage}
            disabled={isLoading || !userId}
          />

          <Button
            type="submit"
            disabled={!inputValue.trim() || isLoading || !userId}
            className="h-[42px] w-[42px] shrink-0 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md hover:shadow-lg"
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
        <p className="mt-1.5 text-xs text-neutral-400 dark:text-neutral-500 flex items-center justify-between">
          <span>Press Enter to send</span>
          {synthesisEnabled && (
            <span className="flex items-center gap-1 text-purple-600 dark:text-purple-400">
              <Volume2 className="h-3 w-3" />
              Voice enabled
            </span>
          )}
        </p>
      </div>

      {/* Voice Settings Dialog */}
      <VoiceSettings
        open={voiceSettingsOpen}
        onOpenChange={setVoiceSettingsOpen}
        recognitionLanguage={recognitionLanguage}
        onRecognitionLanguageChange={setRecognitionLanguage}
        synthesisEnabled={synthesisEnabled}
        onSynthesisEnabledChange={setSynthesisEnabled}
        synthesisLanguage={synthesisLanguage}
        onSynthesisLanguageChange={setSynthesisLanguage}
        voiceGender={voiceGender}
        onVoiceGenderChange={setVoiceGender}
      />
    </div>
  );
}

function WelcomeMessage() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 mb-4">
        <Bot className="h-8 w-8 text-white" />
      </div>
      <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
        TaskFlow AI Assistant
      </h3>
      <p className="text-sm text-neutral-500 dark:text-neutral-400 max-w-md mb-6">
        I can help you manage your tasks using natural language. Try saying:
      </p>
      <div className="grid gap-2 max-w-sm w-full">
        {[
          "Add a task to buy groceries",
          "Show me all my pending tasks",
          "Mark task 1 as complete",
          "What have I completed so far?",
        ].map((suggestion) => (
          <div
            key={suggestion}
            className="text-left text-sm px-4 py-2.5 rounded-lg bg-neutral-50 dark:bg-neutral-800/50 text-neutral-600 dark:text-neutral-400 border border-neutral-200 dark:border-neutral-700"
          >
            "{suggestion}"
          </div>
        ))}
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: UIMessage }) {
  const isUser = message.role === "user";

  // Extract text content from message parts
  const contentText = message.parts
    .filter((part): part is { type: "text"; text: string } => part.type === "text")
    .map((part) => part.text)
    .join("");

  return (
    <div className={cn("flex items-start gap-3", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg",
          isUser
            ? "bg-neutral-200 dark:bg-neutral-700"
            : "bg-gradient-to-br from-blue-500 to-purple-600"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-neutral-600 dark:text-neutral-300" />
        ) : (
          <Bot className="h-4 w-4 text-white" />
        )}
      </div>
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
          isUser
            ? "rounded-tr-sm bg-gradient-to-r from-blue-500 to-purple-600 text-white"
            : "rounded-tl-sm bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100"
        )}
      >
        <p className="whitespace-pre-wrap">{contentText}</p>
      </div>
    </div>
  );
}
