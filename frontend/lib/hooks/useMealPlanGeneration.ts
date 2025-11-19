/**
 * WebSocket Hook for Real-time Meal Plan Generation
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  CreateMealPlanRequest,
  MealPlanGenerationProgress,
  getMealPlanWebSocketUrl,
} from '../api/meal-plans';

interface UseMealPlanGenerationOptions {
  onComplete?: (mealPlan: any) => void;
  onError?: (error: string) => void;
}

export function useMealPlanGeneration(options?: UseMealPlanGenerationOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<MealPlanGenerationProgress | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 3;

  // Connect to WebSocket
  const connect = useCallback(() => {
    try {
      const wsUrl = getMealPlanWebSocketUrl();
      const token = localStorage.getItem('access_token');

      if (!token) {
        setError('Authentication required');
        return;
      }

      // Add token to WebSocket URL
      const ws = new WebSocket(`${wsUrl}?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'progress') {
            setProgress(data.data);

            // Check if generation is complete
            if (data.data.status === 'complete') {
              setIsGenerating(false);
              if (data.data.meal_plan && options?.onComplete) {
                options.onComplete(data.data.meal_plan);
              }
            } else if (data.data.status === 'error') {
              setIsGenerating(false);
              const errorMsg = data.data.error || 'Generation failed';
              setError(errorMsg);
              if (options?.onError) {
                options.onError(errorMsg);
              }
            }
          } else if (data.type === 'error') {
            setError(data.message || 'An error occurred');
            setIsGenerating(false);
            if (options?.onError) {
              options.onError(data.message);
            }
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Connection error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;

        // Attempt to reconnect if we were generating
        if (
          isGenerating &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          reconnectAttemptsRef.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(
              `Reconnecting... Attempt ${reconnectAttemptsRef.current}`
            );
            connect();
          }, 2000);
        }
      };
    } catch (err) {
      console.error('Failed to connect to WebSocket:', err);
      setError('Failed to connect');
    }
  }, [isGenerating, options]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsGenerating(false);
  }, []);

  // Generate meal plan
  const generate = useCallback(
    (request: CreateMealPlanRequest) => {
      if (!isConnected || !wsRef.current) {
        setError('Not connected to server');
        return;
      }

      if (isGenerating) {
        setError('Generation already in progress');
        return;
      }

      setIsGenerating(true);
      setError(null);
      setProgress({
        status: 'thinking',
        progress: 0,
        current_step: 'Initializing...',
      });

      // Send generation request
      wsRef.current.send(
        JSON.stringify({
          type: 'generate',
          data: request,
        })
      );
    },
    [isConnected, isGenerating]
  );

  // Cancel generation
  const cancel = useCallback(() => {
    if (wsRef.current && isGenerating) {
      wsRef.current.send(
        JSON.stringify({
          type: 'cancel',
        })
      );
      setIsGenerating(false);
      setProgress(null);
    }
  }, [isGenerating]);

  // Auto-connect on mount
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return {
    isConnected,
    isGenerating,
    progress,
    error,
    generate,
    cancel,
    connect,
    disconnect,
  };
}
