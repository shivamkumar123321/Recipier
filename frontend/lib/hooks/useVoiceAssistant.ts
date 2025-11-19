/**
 * Voice Assistant Hook
 *
 * Integrates voice recognition with AI cooking assistant
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useVoiceRecognition } from './useVoiceRecognition';
import { useTimers, parseTimeToSeconds } from './useTimers';
import {
  sendVoiceCommand,
  VoiceAssistantContext,
  VoiceCommandResponse,
  VoiceAction,
  createVoiceAssistantWebSocket,
} from '../api/voice-assistant';

interface UseVoiceAssistantOptions {
  recipeId: number;
  currentStep: number;
  onStepChange?: (direction: 'next' | 'previous') => void;
  onShowIngredient?: (ingredient: string) => void;
  onShowNutrition?: () => void;
  useWebSocket?: boolean;
}

interface VoiceAssistantMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface UseVoiceAssistantReturn {
  // Voice recognition
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  startListening: () => void;
  stopListening: () => void;

  // AI assistant
  messages: VoiceAssistantMessage[];
  isProcessing: boolean;
  currentResponse: string;
  sendMessage: (message: string) => Promise<void>;
  speak: (text: string) => void;
  isSpeaking: boolean;

  // Timers
  timers: ReturnType<typeof useTimers>['timers'];
  activeTimers: ReturnType<typeof useTimers>['activeTimers'];
  addTimer: ReturnType<typeof useTimers>['addTimer'];

  // State
  error: Error | null;
  isSupported: boolean;
}

export function useVoiceAssistant(
  options: UseVoiceAssistantOptions
): UseVoiceAssistantReturn {
  const {
    recipeId,
    currentStep,
    onStepChange,
    onShowIngredient,
    onShowNutrition,
    useWebSocket = false,
  } = options;

  const [messages, setMessages] = useState<VoiceAssistantMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const speechSynthesisRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Timer management
  const timerHook = useTimers((timer) => {
    // Timer completed - announce it
    speak(`Timer complete: ${timer.label}`);
  });

  // Voice recognition
  const voiceRecognition = useVoiceRecognition({
    continuous: false,
    interimResults: true,
    onTranscript: (transcript, isFinal) => {
      if (isFinal && transcript.trim()) {
        handleVoiceCommand(transcript.trim());
      }
    },
    onError: (err) => setError(err),
  });

  const isSupported = voiceRecognition.isSupported;

  // Initialize WebSocket if enabled
  useEffect(() => {
    if (!useWebSocket) return;

    wsRef.current = createVoiceAssistantWebSocket(
      recipeId,
      handleWebSocketResponse,
      (err) => setError(err)
    );

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [recipeId, useWebSocket]);

  // Build context for AI
  const getContext = useCallback((): VoiceAssistantContext => {
    return {
      recipe_id: recipeId,
      current_step: currentStep,
      completed_steps: [], // Could track this
    };
  }, [recipeId, currentStep]);

  // Handle voice command with AI
  const handleVoiceCommand = useCallback(
    async (transcript: string) => {
      // Add user message
      const userMessage: VoiceAssistantMessage = {
        id: `msg-${Date.now()}`,
        role: 'user',
        content: transcript,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      setIsProcessing(true);
      setError(null);

      try {
        // Check for quick commands first
        const quickAction = parseQuickCommand(transcript);
        if (quickAction) {
          await executeAction(quickAction, transcript);
          setIsProcessing(false);
          return;
        }

        // Send to AI backend
        const context = getContext();
        const response = await sendVoiceCommand({
          transcript,
          context,
        });

        // Add assistant message
        const assistantMessage: VoiceAssistantMessage = {
          id: `msg-${Date.now()}-ai`,
          role: 'assistant',
          content: response.response_text,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Execute any actions
        if (response.action) {
          await executeAction(response.action, transcript);
        }

        // Speak response
        speak(response.response_text);
      } catch (err) {
        console.error('Error processing voice command:', err);
        setError(err as Error);
        speak('Sorry, I had trouble processing that. Could you try again?');
      } finally {
        setIsProcessing(false);
      }
    },
    [getContext]
  );

  // Parse quick commands (timers, navigation)
  const parseQuickCommand = (transcript: string): VoiceAction | null => {
    const lower = transcript.toLowerCase();

    // Timer commands
    if (lower.includes('timer') || lower.includes('set') || lower.includes('remind')) {
      const timeMatch = lower.match(/(\d+)\s*(minute|min|second|sec|hour|hr)s?/);
      if (timeMatch) {
        const duration = parseTimeToSeconds(`${timeMatch[1]}${timeMatch[2][0]}`);
        return {
          type: 'set_timer',
          payload: { duration_seconds: duration, label: 'Cooking Timer' },
        };
      }
    }

    // Navigation commands
    if (lower.includes('next') || lower.includes('continue')) {
      return { type: 'next_step' };
    }
    if (lower.includes('back') || lower.includes('previous')) {
      return { type: 'previous_step' };
    }
    if (lower.includes('repeat') || lower.includes('again')) {
      return { type: 'repeat_step' };
    }

    // Ingredient/nutrition
    if (lower.includes('ingredient')) {
      return { type: 'show_ingredient' };
    }
    if (lower.includes('nutrition') || lower.includes('calories')) {
      return { type: 'show_nutrition' };
    }

    return null;
  };

  // Execute action from voice command
  const executeAction = async (action: VoiceAction, originalTranscript: string) => {
    switch (action.type) {
      case 'next_step':
        onStepChange?.('next');
        speak('Moving to next step');
        break;

      case 'previous_step':
        onStepChange?.('previous');
        speak('Going back to previous step');
        break;

      case 'set_timer':
        if (action.payload) {
          const { duration_seconds, label } = action.payload;
          const timerId = timerHook.addTimer(duration_seconds, label);
          timerHook.startTimer(timerId);
          speak(`Timer set for ${formatDuration(duration_seconds)}`);
        }
        break;

      case 'show_ingredient':
        onShowIngredient?.(originalTranscript);
        break;

      case 'show_nutrition':
        onShowNutrition?.();
        speak('Showing nutrition information');
        break;

      case 'repeat_step':
        speak('Let me repeat the current step');
        // The calling component should handle re-reading the step
        break;

      default:
        break;
    }
  };

  // Handle WebSocket response
  const handleWebSocketResponse = useCallback(
    (response: VoiceCommandResponse) => {
      setCurrentResponse(response.response_text);

      if (response.action) {
        executeAction(response.action, '');
      }

      // If streaming is complete, add to messages
      if (!response.response_text.endsWith('...')) {
        const assistantMessage: VoiceAssistantMessage = {
          id: `msg-${Date.now()}-ws`,
          role: 'assistant',
          content: response.response_text,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
        speak(response.response_text);
      }
    },
    []
  );

  // Text-to-speech using Web Speech API
  const speak = useCallback((text: string) => {
    if (!('speechSynthesis' in window)) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    speechSynthesisRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, []);

  // Send text message manually
  const sendMessage = useCallback(
    async (message: string) => {
      await handleVoiceCommand(message);
    },
    [handleVoiceCommand]
  );

  // Cleanup
  useEffect(() => {
    return () => {
      if (speechSynthesisRef.current) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return {
    // Voice recognition
    isListening: voiceRecognition.isListening,
    transcript: voiceRecognition.transcript,
    interimTranscript: voiceRecognition.interimTranscript,
    startListening: voiceRecognition.startListening,
    stopListening: voiceRecognition.stopListening,

    // AI assistant
    messages,
    isProcessing,
    currentResponse,
    sendMessage,
    speak,
    isSpeaking,

    // Timers
    timers: timerHook.timers,
    activeTimers: timerHook.activeTimers,
    addTimer: timerHook.addTimer,

    // State
    error,
    isSupported,
  };
}

// Helper to format duration for speech
function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts: string[] = [];
  if (hours > 0) parts.push(`${hours} hour${hours > 1 ? 's' : ''}`);
  if (minutes > 0) parts.push(`${minutes} minute${minutes > 1 ? 's' : ''}`);
  if (secs > 0) parts.push(`${secs} second${secs > 1 ? 's' : ''}`);

  return parts.join(' and ') || '0 seconds';
}
