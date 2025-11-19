/**
 * Voice Recognition Hook
 *
 * Uses Web Speech API for real-time speech-to-text
 */

import { useState, useEffect, useRef, useCallback } from 'react';

interface UseVoiceRecognitionOptions {
  continuous?: boolean;
  interimResults?: boolean;
  language?: string;
  onTranscript?: (transcript: string, isFinal: boolean) => void;
  onError?: (error: Error) => void;
}

interface UseVoiceRecognitionReturn {
  transcript: string;
  interimTranscript: string;
  isListening: boolean;
  isSupported: boolean;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
  error: Error | null;
}

// Extend Window interface for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export function useVoiceRecognition(
  options: UseVoiceRecognitionOptions = {}
): UseVoiceRecognitionReturn {
  const {
    continuous = false,
    interimResults = true,
    language = 'en-US',
    onTranscript,
    onError,
  } = options;

  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const recognitionRef = useRef<any>(null);

  // Check if Web Speech API is supported
  const isSupported =
    typeof window !== 'undefined' &&
    (window.SpeechRecognition || window.webkitSpeechRecognition);

  useEffect(() => {
    if (!isSupported) return;

    // Initialize SpeechRecognition
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();

    const recognition = recognitionRef.current;
    recognition.continuous = continuous;
    recognition.interimResults = interimResults;
    recognition.lang = language;
    recognition.maxAlternatives = 1;

    // Handle results
    recognition.onresult = (event: any) => {
      let interimText = '';
      let finalText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;

        if (result.isFinal) {
          finalText += text + ' ';
        } else {
          interimText += text;
        }
      }

      if (finalText) {
        setTranscript((prev) => prev + finalText);
        onTranscript?.(finalText.trim(), true);
      }

      if (interimText) {
        setInterimTranscript(interimText);
        onTranscript?.(interimText, false);
      }
    };

    // Handle errors
    recognition.onerror = (event: any) => {
      const error = new Error(`Speech recognition error: ${event.error}`);
      setError(error);
      setIsListening(false);
      onError?.(error);
    };

    // Handle end
    recognition.onend = () => {
      setIsListening(false);
    };

    // Handle start
    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, [continuous, interimResults, language, onTranscript, onError, isSupported]);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;

    try {
      setError(null);
      setInterimTranscript('');
      recognitionRef.current.start();
    } catch (error) {
      // Recognition might already be started
      console.error('Error starting recognition:', error);
    }
  }, []);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return;

    try {
      recognitionRef.current.stop();
    } catch (error) {
      console.error('Error stopping recognition:', error);
    }
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  return {
    transcript,
    interimTranscript,
    isListening,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
    error,
  };
}

/**
 * Hook for wake word detection
 */
export function useWakeWordDetection(
  wakeWord: string,
  onDetected: () => void,
  options: { enabled?: boolean; sensitivity?: number } = {}
): { isActive: boolean } {
  const { enabled = true, sensitivity = 0.8 } = options;
  const [isActive, setIsActive] = useState(false);

  const { isListening, startListening } = useVoiceRecognition({
    continuous: true,
    interimResults: true,
    onTranscript: (transcript, isFinal) => {
      if (!enabled) return;

      const lowerTranscript = transcript.toLowerCase();
      const lowerWakeWord = wakeWord.toLowerCase();

      // Simple fuzzy matching for wake word
      if (lowerTranscript.includes(lowerWakeWord)) {
        setIsActive(true);
        onDetected();

        // Auto-deactivate after detection
        setTimeout(() => setIsActive(false), 5000);
      }
    },
  });

  useEffect(() => {
    if (enabled && !isListening) {
      startListening();
    }
  }, [enabled, isListening, startListening]);

  return { isActive };
}
