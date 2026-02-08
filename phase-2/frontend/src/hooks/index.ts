/**
 * Voice hooks exports
 *
 * Centralized exports for voice-related hooks.
 */

export {
  useSpeechRecognition,
  supportsSpeechRecognition,
  SPEECH_RECOGNITION_LANGUAGES,
  type SpeechRecognitionOptions,
  type SpeechRecognitionResult,
  type SpeechRecognitionError,
  type SpeechRecognitionLanguage,
} from "./useSpeechRecognition";

export {
  useSpeechSynthesis,
  supportsSpeechSynthesis,
  findVoiceByPreference,
  getAvailableLanguages,
  getVoicesByLanguage,
  getMaleVoices,
  getFemaleVoices,
  type SpeechSynthesisOptions,
  type SpeechSynthesisState,
  type VoicePreference,
} from "./useSpeechSynthesis";
