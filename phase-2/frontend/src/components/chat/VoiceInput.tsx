/**
 * VoiceInput Component
 *
 * Microphone button for speech recognition with visual feedback.
 * Integrates with useSpeechRecognition hook for voice-to-text conversion.
 *
 * @module VoiceInput
 */

"use client";

import { useState } from "react";
import { Mic, MicOff, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { useSpeechRecognition, SPEECH_RECOGNITION_LANGUAGES } from "@/hooks/useSpeechRecognition";
import { cn } from "@/lib/utils";

export interface VoiceInputProps {
  onTranscript: (transcript: string) => void;
  language?: string;
  onLanguageChange?: (language: string) => void;
  disabled?: boolean;
  className?: string;
}

export function VoiceInput({
  onTranscript,
  language = "en-US",
  onLanguageChange,
  disabled = false,
  className,
}: VoiceInputProps) {
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);

  const {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition({
    language: selectedLanguage,
    continuous: false,
    interimResults: true,
  });

  // Handle transcript changes
  const handleTranscriptChange = (text: string) => {
    if (text && text.trim()) {
      onTranscript(text.trim());
      resetTranscript();
    }
  };

  // Toggle listening state
  const toggleListening = () => {
    if (isListening) {
      stopListening();
      if (transcript) {
        handleTranscriptChange(transcript);
      }
    } else {
      startListening();
    }
  };

  // Handle language selection
  const handleLanguageSelect = (langCode: string) => {
    setSelectedLanguage(langCode);
    onLanguageChange?.(langCode);

    // Restart listening if active
    if (isListening) {
      stopListening();
      setTimeout(() => startListening(), 100);
    }
  };

  // Get display text for current language
  const currentLanguage = SPEECH_RECOGNITION_LANGUAGES.find(
    (lang) => lang.code === selectedLanguage
  );

  if (!isSupported) {
    return (
      <Button
        variant="outline"
        size="icon"
        disabled
        className={cn("h-[42px] w-[42px] shrink-0 rounded-xl", className)}
        title="Speech recognition not supported in this browser"
      >
        <MicOff className="h-4 w-4 text-neutral-400" />
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-1">
      {/* Language Selector */}
      <DropdownMenu onOpenChange={setShowLanguageMenu}>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-[42px] w-[42px] shrink-0 rounded-xl text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200"
            disabled={isListening || disabled}
            title={`Current language: ${currentLanguage?.name || "English (US)"}`}
          >
            <span className="text-xs font-semibold">
              {selectedLanguage.split("-")[1]?.toUpperCase() || "EN"}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <DropdownMenuLabel>Select Language</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {SPEECH_RECOGNITION_LANGUAGES.map((lang) => (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => handleLanguageSelect(lang.code)}
              className={cn(
                "cursor-pointer",
                selectedLanguage === lang.code && "bg-neutral-100 dark:bg-neutral-800"
              )}
            >
              <span className="flex-1">{lang.name}</span>
              {selectedLanguage === lang.code && (
                <span className="text-xs text-neutral-500">✓</span>
              )}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Microphone Button */}
      <div className="relative">
        <Button
          variant="outline"
          size="icon"
          onClick={toggleListening}
          disabled={disabled}
          className={cn(
            "h-[42px] w-[42px] shrink-0 rounded-xl transition-all duration-200",
            isListening && "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800",
            !isListening && "hover:bg-neutral-50 dark:hover:bg-neutral-800",
            className
          )}
          title={
            isListening
              ? "Click to stop recording"
              : "Click to start voice input"
          }
        >
          {isListening ? (
            <>
              <Mic className="h-4 w-4 text-red-600 dark:text-red-400 animate-pulse" />
              {/* Recording indicator ring */}
              <span className="absolute inset-0 rounded-xl border-2 border-red-500 animate-ping opacity-20" />
            </>
          ) : (
            <Mic className="h-4 w-4" />
          )}
        </Button>

        {/* Listening indicator badge */}
        {isListening && (
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
          </span>
        )}
      </div>

      {/* Error display */}
      {error && (
        <div className="absolute bottom-full left-0 right-0 mb-2 p-2 rounded-lg bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 text-xs flex items-start gap-1">
          <AlertCircle className="h-3 w-3 shrink-0 mt-0.5" />
          <span>{error.message}</span>
        </div>
      )}

      {/* Interim transcript preview */}
      {isListening && interimTranscript && (
        <div className="absolute bottom-full left-0 right-0 mb-2 p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 text-xs italic">
          "{interimTranscript}"
        </div>
      )}
    </div>
  );
}

/**
 * Compact version of VoiceInput for smaller spaces
 */
export function VoiceInputCompact({
  onTranscript,
  language = "en-US",
  disabled = false,
}: Pick<VoiceInputProps, "onTranscript" | "language" | "disabled">) {
  const { isListening, transcript, isSupported, startListening, stopListening } =
    useSpeechRecognition({ language });

  const handleClick = () => {
    if (isListening) {
      stopListening();
      if (transcript) {
        onTranscript(transcript);
      }
    } else {
      startListening();
    }
  };

  if (!isSupported) {
    return null;
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleClick}
      disabled={disabled}
      className={cn(
        "h-8 w-8 rounded-lg",
        isListening && "bg-red-50 dark:bg-red-950/30"
      )}
      title="Voice input"
    >
      {isListening ? (
        <Mic className="h-3.5 w-3.5 text-red-600 dark:text-red-400 animate-pulse" />
      ) : (
        <Mic className="h-3.5 w-3.5" />
      )}
    </Button>
  );
}

export default VoiceInput;
