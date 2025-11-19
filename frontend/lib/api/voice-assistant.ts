/**
 * Voice Assistant API Client
 *
 * Handles communication with voice cooking assistant backend
 */

import { api } from './client';

export interface VoiceAssistantMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface VoiceAssistantContext {
  recipe_id: number;
  current_step: number;
  elapsed_time?: number;
  completed_steps?: number[];
}

export interface VoiceCommandRequest {
  transcript: string;
  context: VoiceAssistantContext;
  audio_data?: string; // Base64 encoded audio
}

export interface VoiceCommandResponse {
  response_text: string;
  response_audio_url?: string;
  action?: VoiceAction;
  suggestions?: string[];
}

export interface VoiceAction {
  type:
    | 'next_step'
    | 'previous_step'
    | 'set_timer'
    | 'show_ingredient'
    | 'show_nutrition'
    | 'repeat_step'
    | 'conversion'
    | 'substitution'
    | 'none';
  payload?: any;
}

export interface TimerAction {
  duration_seconds: number;
  label?: string;
}

export interface ConversionAction {
  from_amount: number;
  from_unit: string;
  to_unit: string;
  result: number;
}

/**
 * Send voice command to assistant
 */
export async function sendVoiceCommand(
  request: VoiceCommandRequest
): Promise<VoiceCommandResponse> {
  const response = await api.post<VoiceCommandResponse>(
    '/api/v1/voice-assistant/command',
    request
  );
  return response.data;
}

/**
 * Get AI cooking assistance via WebSocket for streaming responses
 */
export function createVoiceAssistantWebSocket(
  recipeId: number,
  onMessage: (response: VoiceCommandResponse) => void,
  onError?: (error: Error) => void
): WebSocket {
  const wsUrl = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || '';
  const ws = new WebSocket(
    `${wsUrl}/api/v1/voice-assistant/ws/${recipeId}`
  );

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      onError?.(error as Error);
    }
  };

  ws.onerror = (event) => {
    console.error('WebSocket error:', event);
    onError?.(new Error('WebSocket connection error'));
  };

  return ws;
}

/**
 * Parse user intent from transcript
 */
export async function parseUserIntent(
  transcript: string,
  context: VoiceAssistantContext
): Promise<VoiceAction> {
  const response = await api.post<VoiceAction>(
    '/api/v1/voice-assistant/parse-intent',
    { transcript, context }
  );
  return response.data;
}

/**
 * Convert text to speech (using backend OpenAI TTS)
 */
export async function textToSpeech(text: string): Promise<string> {
  const response = await api.post<{ audio_url: string }>(
    '/api/v1/voice-assistant/tts',
    { text }
  );
  return response.data.audio_url;
}

/**
 * Transcribe audio using Whisper API
 */
export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const formData = new FormData();
  formData.append('audio', audioBlob);

  const response = await api.post<{ transcript: string }>(
    '/api/v1/voice-assistant/transcribe',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data.transcript;
}

/**
 * Get cooking suggestions based on current context
 */
export async function getCookingSuggestions(
  context: VoiceAssistantContext
): Promise<string[]> {
  const response = await api.post<{ suggestions: string[] }>(
    '/api/v1/voice-assistant/suggestions',
    { context }
  );
  return response.data.suggestions;
}
