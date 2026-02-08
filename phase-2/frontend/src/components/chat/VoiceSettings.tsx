/**
 * VoiceSettings Component
 *
 * Settings panel for voice recognition and synthesis preferences.
 * Provides language selection, voice gender selection, and speech synthesis toggle.
 *
 * @module VoiceSettings
 */

"use client";

import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Settings, Volume2, VolumeX, Play, Pause } from "lucide-react";
import { useSpeechSynthesis } from "@/hooks/useSpeechSynthesis";
import { cn } from "@/lib/utils";

export interface VoiceSettingsProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  recognitionLanguage: string;
  onRecognitionLanguageChange: (language: string) => void;
  synthesisEnabled: boolean;
  onSynthesisEnabledChange: (enabled: boolean) => void;
  synthesisLanguage: string;
  onSynthesisLanguageChange: (language: string) => void;
  voiceGender: "male" | "female" | "any";
  onVoiceGenderChange: (gender: "male" | "female" | "any") => void;
}

// Available languages
const LANGUAGES = [
  { code: "en-US", name: "English (US)" },
  { code: "en-GB", name: "English (UK)" },
  { code: "ur-PK", name: "Urdu (Pakistan)" },
  { code: "ur-IN", name: "Urdu (India)" },
  { code: "hi-IN", name: "Hindi (India)" },
  { code: "es-ES", name: "Spanish (Spain)" },
  { code: "fr-FR", name: "French (France)" },
  { code: "ar-SA", name: "Arabic (Saudi Arabia)" },
];

const GENDER_OPTIONS = [
  { value: "any", label: "Any Voice" },
  { value: "female", label: "Female Voice" },
  { value: "male", label: "Male Voice" },
] as const;

export function VoiceSettings({
  open,
  onOpenChange,
  recognitionLanguage,
  onRecognitionLanguageChange,
  synthesisEnabled,
  onSynthesisEnabledChange,
  synthesisLanguage,
  onSynthesisLanguageChange,
  voiceGender,
  onVoiceGenderChange,
}: VoiceSettingsProps) {
  const { isSpeaking, filteredVoices, speak, cancel } = useSpeechSynthesis({
    language: synthesisLanguage,
  });

  const [isPlayingPreview, setIsPlayingPreview] = useState(false);

  // Test speech synthesis
  const handleTestVoice = () => {
    if (isSpeaking) {
      cancel();
      setIsPlayingPreview(false);
    } else {
      const testText =
        synthesisLanguage.startsWith("ur")
          ? "آپ کی آواز کی تنظیم مکمل ہو گئی ہے"
          : "Your voice settings have been configured.";

      speak(testText);
      setIsPlayingPreview(true);

      // Reset preview state after speaking
      setTimeout(() => {
        setIsPlayingPreview(false);
      }, 3000);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Voice Settings
          </DialogTitle>
          <DialogDescription>
            Configure your voice recognition and speech synthesis preferences.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Speech Recognition Settings */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                <Volume2 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="text-sm font-semibold">Speech Recognition</h3>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Language for voice input
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="recognition-language">Recognition Language</Label>
              <select
                id="recognition-language"
                value={recognitionLanguage}
                onChange={(e) => onRecognitionLanguageChange(e.target.value)}
                className={cn(
                  "w-full rounded-lg border border-neutral-300 dark:border-neutral-700",
                  "bg-white dark:bg-neutral-900 px-3 py-2 text-sm",
                  "focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                )}
              >
                {LANGUAGES.map((lang) => (
                  <option key={`rec-${lang.code}`} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Speech Synthesis Settings */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30">
                {synthesisEnabled ? (
                  <Volume2 className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                ) : (
                  <VolumeX className="h-4 w-4 text-neutral-400" />
                )}
              </div>
              <div>
                <h3 className="text-sm font-semibold">Speech Synthesis</h3>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  AI response voice output
                </p>
              </div>
            </div>

            {/* Enable/Disable Toggle */}
            <div className="flex items-center justify-between">
              <Label htmlFor="synthesis-toggle" className="cursor-pointer">
                Enable Speech Output
              </Label>
              <button
                id="synthesis-toggle"
                type="button"
                onClick={() => onSynthesisEnabledChange(!synthesisEnabled)}
                className={cn(
                  "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                  synthesisEnabled
                    ? "bg-purple-600"
                    : "bg-neutral-300 dark:bg-neutral-700"
                )}
              >
                <span
                  className={cn(
                    "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                    synthesisEnabled ? "translate-x-6" : "translate-x-1"
                  )}
                />
              </button>
            </div>

            {synthesisEnabled && (
              <>
                {/* Voice Selection */}
                <div className="space-y-2">
                  <Label htmlFor="synthesis-language">Response Language</Label>
                  <select
                    id="synthesis-language"
                    value={synthesisLanguage}
                    onChange={(e) =>
                      onSynthesisLanguageChange(e.target.value)
                    }
                    className={cn(
                      "w-full rounded-lg border border-neutral-300 dark:border-neutral-700",
                      "bg-white dark:bg-neutral-900 px-3 py-2 text-sm",
                      "focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                    )}
                  >
                    {LANGUAGES.map((lang) => (
                      <option key={`syn-${lang.code}`} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-neutral-500">
                    {filteredVoices.length} voice(s) available
                  </p>
                </div>

                {/* Gender Selection */}
                <div className="space-y-2">
                  <Label>Voice Gender</Label>
                  <div className="flex flex-wrap gap-2">
                    {GENDER_OPTIONS.map((option) => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() =>
                          onVoiceGenderChange(
                            option.value as typeof voiceGender
                          )
                        }
                        className={cn(
                          "px-3 py-1.5 text-sm rounded-lg border transition-colors",
                          voiceGender === option.value
                            ? "bg-purple-100 dark:bg-purple-900/30 border-purple-300 dark:border-purple-700 text-purple-700 dark:text-purple-300"
                            : "bg-white dark:bg-neutral-900 border-neutral-300 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-800"
                        )}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Test Button */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleTestVoice}
                  disabled={filteredVoices.length === 0}
                  className="w-full gap-2"
                >
                  {isSpeaking ? (
                    <>
                      <Pause className="h-4 w-4" />
                      Stop Test
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      Test Voice
                    </>
                  )}
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Info Banner */}
        <div className="rounded-lg bg-neutral-100 dark:bg-neutral-800 p-3 text-xs text-neutral-600 dark:text-neutral-400">
          <p className="font-semibold mb-1">Voice Commands</p>
          <p className="mb-2">
            Try saying things like:
          </p>
          <ul className="space-y-1 ml-4 list-disc">
            <li>"Add a task to buy groceries"</li>
            <li>"Show my tasks"</li>
            <li>"Mark task 3 complete"</li>
            <li>"What's pending?"</li>
          </ul>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default VoiceSettings;
