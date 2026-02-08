/**
 * useSpeechRecognition Hook
 *
 * Provides speech recognition functionality using the Web Speech API.
 * Supports multiple languages (English, Urdu) with error handling.
 *
 * @module useSpeechRecognition
 */

"use client";

import { useState, useCallback, useRef, useEffect } from "react";

export interface SpeechRecognitionOptions {
  language?: string;
  continuous?: boolean;
  interimResults?: boolean;
  maxAlternatives?: number;
}

export interface SpeechRecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
}

export interface SpeechRecognitionError {
  error: string;
  message: string;
}

type SpeechRecognitionEventType =
  | "start"
  | "end"
  | "result"
  | "error"
  | "speechstart"
  | "speechend"
  | "audiostart"
  | "audioend";

// Extend Window interface for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

// Check browser support
export function supportsSpeechRecognition(): boolean {
  if (typeof window === "undefined") return false;
  return (
    "SpeechRecognition" in window ||
    "webkitSpeechRecognition" in window
  );
}

// Speech Recognition API (with webkit prefix for Chrome/Edge)
const SpeechRecognitionAPI =
  typeof window !== "undefined"
    ? (window.SpeechRecognition || window.webkitSpeechRecognition || null)
    : null;

class SpeechRecognition extends EventTarget {
  continuous = false;
  interimResults = false;
  lang = "en-US";
  maxAlternatives = 1;

  private recognition: any;

  constructor() {
    super();
    if (!SpeechRecognitionAPI) {
      throw new Error("Speech recognition not supported in this browser");
    }
    this.recognition = new SpeechRecognitionAPI();
    this.setupEventForwarding();
  }

  private setupEventForwarding() {
    const events: SpeechRecognitionEventType[] = [
      "start",
      "end",
      "result",
      "error",
      "speechstart",
      "speechend",
      "audiostart",
      "audioend",
    ];

    events.forEach((event) => {
      this.recognition.addEventListener(event, (e: any) => {
        this.dispatchEvent(new CustomEvent(event, { detail: e }));
      });
    });
  }

  start() {
    this.recognition.continuous = this.continuous;
    this.recognition.interimResults = this.interimResults;
    this.recognition.lang = this.lang;
    this.recognition.maxAlternatives = this.maxAlternatives;
    this.recognition.start();
  }

  stop() {
    this.recognition.stop();
  }

  abort() {
    this.recognition.abort();
  }
}

export function useSpeechRecognition(options: SpeechRecognitionOptions = {}) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState<SpeechRecognitionError | null>(null);
  const [isSupported, setIsSupported] = useState(false);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const finalTranscriptRef = useRef("");

  // Check support on mount
  useEffect(() => {
    setIsSupported(supportsSpeechRecognition());
  }, []);

  const startListening = useCallback(() => {
    if (!isSupported) {
      setError({
        error: "not-allowed",
        message: "Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.",
      });
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = options.continuous ?? false;
      recognition.interimResults = options.interimResults ?? false;
      recognition.lang = options.language ?? "en-US";
      recognition.maxAlternatives = options.maxAlternatives ?? 1;

      recognition.addEventListener("start", () => {
        setIsListening(true);
        setError(null);
        setTranscript("");
        setInterimTranscript("");
        finalTranscriptRef.current = "";
      });

      recognition.addEventListener("result", (event: any) => {
        // Access the native event from CustomEvent.detail
        const nativeEvent = event.detail || event;
        const results = nativeEvent.results;
        const resultIndex = nativeEvent.resultIndex ?? 0;

        // Guard against undefined results
        if (!results || typeof results.length === "undefined") {
          return;
        }

        let interimText = "";
        let finalText = finalTranscriptRef.current;

        for (let i = resultIndex; i < results.length; i++) {
          const result = results[i];
          if (!result || !result[0]) continue;

          const transcript = result[0].transcript;

          if (result.isFinal) {
            finalText += transcript + " ";
            setConfidence(result[0].confidence ?? 0);
          } else {
            interimText += transcript;
          }
        }

        if (finalText) {
          finalTranscriptRef.current = finalText;
          setTranscript(finalText.trim());
        }
        setInterimTranscript(interimText);
      });

      recognition.addEventListener("end", () => {
        setIsListening(false);
        // If we have a final transcript but no more speech, we're done
        if (finalTranscriptRef.current) {
          setTranscript(finalTranscriptRef.current.trim());
        }
      });

      recognition.addEventListener("error", (event: any) => {
        setIsListening(false);
        // Access the native event from CustomEvent.detail
        const nativeEvent = event.detail || event;
        const errorCode = nativeEvent.error || "unknown";

        const errorMessages: Record<string, string> = {
          "no-speech": "No speech detected. Please try again.",
          "audio-capture": "No microphone found. Please ensure a microphone is connected.",
          "not-allowed": "Microphone permission denied. Please allow microphone access.",
          "network": "Network error. Please check your connection.",
          "aborted": "Speech recognition was aborted.",
        };
        const errorMessage = errorMessages[errorCode] || errorCode;

        setError({
          error: errorCode,
          message: errorMessage,
        });
      });

      recognition.start();
      recognitionRef.current = recognition;
    } catch (err) {
      setIsListening(false);
      setError({
        error: "init-failed",
        message: err instanceof Error ? err.message : "Failed to initialize speech recognition",
      });
    }
  }, [isSupported, options]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript("");
    setInterimTranscript("");
    setConfidence(0);
    setError(null);
    finalTranscriptRef.current = "";
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  return {
    isListening,
    transcript,
    interimTranscript,
    confidence,
    error,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  };
}

// Language options for speech recognition
export const SPEECH_RECOGNITION_LANGUAGES = [
  { code: "en-US", name: "English (US)" },
  { code: "en-GB", name: "English (UK)" },
  { code: "ur-PK", name: "Urdu (Pakistan)" },
  { code: "ur-IN", name: "Urdu (India)" },
  { code: "hi-IN", name: "Hindi (India)" },
  { code: "es-ES", name: "Spanish (Spain)" },
  { code: "fr-FR", name: "French (France)" },
  { code: "ar-SA", name: "Arabic (Saudi Arabia)" },
] as const;

export type SpeechRecognitionLanguage = typeof SPEECH_RECOGNITION_LANGUAGES[number]["code"];
