/**
 * useSpeechSynthesis Hook
 *
 * Provides text-to-speech functionality using the Web Speech Synthesis API.
 * Supports voice selection, playback controls, and language filtering.
 *
 * @module useSpeechSynthesis
 */

"use client";

import { useState, useCallback, useEffect, useRef } from "react";

export interface SpeechSynthesisOptions {
  voice?: SpeechSynthesisVoice;
  volume?: number;
  rate?: number;
  pitch?: number;
  language?: string;
}

export interface SpeechSynthesisState {
  isSpeaking: boolean;
  isPaused: boolean;
  isSupported: boolean;
  currentText: string | null;
  voices: SpeechSynthesisVoice[];
}

export interface VoicePreference {
  lang: string;
  gender: "male" | "female" | "any";
}

// Check browser support
export function supportsSpeechSynthesis(): boolean {
  if (typeof window === "undefined") return false;
  return "speechSynthesis" in window;
}

export function useSpeechSynthesis(options: SpeechSynthesisOptions = {}) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentText, setCurrentText] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [filteredVoices, setFilteredVoices] = useState<SpeechSynthesisVoice[]>([]);

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const optionsRef = useRef(options);

  // Update options ref
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  // Check support and load voices on mount
  useEffect(() => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setIsSupported(false);
      return;
    }

    setIsSupported(true);

    // Load voices
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
    };

    // Voices load asynchronously in some browsers
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, []);

  // Filter voices based on language and options
  useEffect(() => {
    if (voices.length === 0) {
      setFilteredVoices([]);
      return;
    }

    let filtered = voices;

    // Filter by language if specified
    if (options.language) {
      filtered = filtered.filter((voice) =>
        voice.lang.toLowerCase().startsWith(options.language!.toLowerCase())
      );
    }

    // Filter by gender if voice is specified
    if (options.voice) {
      filtered = filtered.filter((v) => v.name === options.voice!.name);
    }

    setFilteredVoices(filtered);
  }, [voices, options.language, options.voice]);

  const speak = useCallback(
    (text: string, overrideOptions?: SpeechSynthesisOptions) => {
      if (!isSupported || !text) return;

      // Cancel any ongoing speech
      cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      const opts = { ...optionsRef.current, ...overrideOptions };

      // Set utterance properties
      utterance.volume = opts.volume ?? 1;
      utterance.rate = opts.rate ?? 1;
      utterance.pitch = opts.pitch ?? 1;

      // Set voice
      if (opts.voice) {
        utterance.voice = opts.voice;
      } else if (filteredVoices.length > 0) {
        // Use first available voice matching the language
        utterance.voice = filteredVoices[0];
      } else if (voices.length > 0) {
        // Fallback to first available voice
        utterance.voice = voices[0];
      }

      // Event handlers
      utterance.onstart = () => {
        setIsSpeaking(true);
        setIsPaused(false);
        setCurrentText(text);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
        setIsPaused(false);
        setCurrentText(null);
        utteranceRef.current = null;
      };

      utterance.onerror = (event) => {
        console.error("Speech synthesis error:", event.error);
        setIsSpeaking(false);
        setIsPaused(false);
        setCurrentText(null);
        utteranceRef.current = null;
      };

      utterance.onpause = () => {
        setIsPaused(true);
      };

      utterance.onresume = () => {
        setIsPaused(false);
      };

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    },
    [isSupported, filteredVoices, voices]
  );

  const cancel = useCallback(() => {
    if (!isSupported) return;

    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
    setCurrentText(null);
    utteranceRef.current = null;
  }, [isSupported]);

  const pause = useCallback(() => {
    if (!isSupported || !isSpeaking) return;

    window.speechSynthesis.pause();
    setIsPaused(true);
  }, [isSupported, isSpeaking]);

  const resume = useCallback(() => {
    if (!isSupported || !isPaused) return;

    window.speechSynthesis.resume();
    setIsPaused(false);
  }, [isSupported, isPaused]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isSpeaking) {
        cancel();
      }
    };
  }, [isSpeaking, cancel]);

  return {
    isSpeaking,
    isPaused,
    isSupported,
    currentText,
    voices,
    filteredVoices,
    speak,
    cancel,
    pause,
    resume,
  };
}

/**
 * Get a voice matching specific preferences (language, gender)
 */
export function findVoiceByPreference(
  voices: SpeechSynthesisVoice[],
  preference: VoicePreference
): SpeechSynthesisVoice | null {
  const { lang, gender } = preference;

  // Filter by language
  let matching = voices.filter((voice) =>
    voice.lang.toLowerCase().startsWith(lang.toLowerCase())
  );

  if (matching.length === 0) {
    // No voice for this language, return first available
    return voices[0] || null;
  }

  // Filter by gender if specified and not "any"
  if (gender !== "any") {
    const genderMatches = matching.filter((voice) => {
      const name = voice.name.toLowerCase();
      // Common patterns for gender-specific voices
      if (gender === "female") {
        return (
          name.includes("female") ||
          name.includes("woman") ||
          name.includes("zira") ||
          name.includes("samantha") ||
          name.includes("karen") ||
          name.includes("moira") ||
          name.includes("tessa") ||
          name.includes("fiona")
        );
      } else {
        return (
          name.includes("male") ||
          name.includes("david") ||
          name.includes("daniel") ||
          name.includes("james") ||
          name.includes("richard") ||
          name.includes("google us english")
        );
      }
    });

    if (genderMatches.length > 0) {
      matching = genderMatches;
    }
  }

  // Prefer local service voices (faster, more reliable)
  const localVoices = matching.filter((v) => v.localService);
  if (localVoices.length > 0) {
    return localVoices[0];
  }

  return matching[0];
}

// Helper to get all available languages from voices
export function getAvailableLanguages(voices: SpeechSynthesisVoice[]): string[] {
  const langs = new Set<string>();
  voices.forEach((voice) => {
    langs.add(voice.lang.split("-")[0]);
  });
  return Array.from(langs).sort();
}

// Helper to get voices by language
export function getVoicesByLanguage(
  voices: SpeechSynthesisVoice[],
  languageCode: string
): SpeechSynthesisVoice[] {
  return voices.filter((voice) =>
    voice.lang.toLowerCase().startsWith(languageCode.toLowerCase())
  );
}

// Helper to get male voices
export function getMaleVoices(voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice[] {
  const maleKeywords = [
    "male",
    "david",
    "daniel",
    "james",
    "richard",
    "google us english",
    "microsoft david",
    "microsoft mark",
  ];

  return voices.filter((voice) =>
    maleKeywords.some((keyword) =>
      voice.name.toLowerCase().includes(keyword)
    )
  );
}

// Helper to get female voices
export function getFemaleVoices(voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice[] {
  const femaleKeywords = [
    "female",
    "zira",
    "samantha",
    "karen",
    "moira",
    "tessa",
    "fiona",
    "microsoft zira",
    "microsoft aria",
  ];

  return voices.filter((voice) =>
    femaleKeywords.some((keyword) =>
      voice.name.toLowerCase().includes(keyword)
    )
  );
}

export default useSpeechSynthesis;
