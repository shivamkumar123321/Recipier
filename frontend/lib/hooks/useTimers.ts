/**
 * Timers Hook
 *
 * Manage multiple concurrent cooking timers
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export interface Timer {
  id: string;
  label: string;
  duration: number; // Total duration in seconds
  remaining: number; // Remaining time in seconds
  isRunning: boolean;
  isPaused: boolean;
  isCompleted: boolean;
  startedAt?: Date;
  completedAt?: Date;
}

interface UseTimersReturn {
  timers: Timer[];
  activeTimers: Timer[];
  completedTimers: Timer[];
  addTimer: (duration: number, label?: string) => string;
  startTimer: (id: string) => void;
  pauseTimer: (id: string) => void;
  resumeTimer: (id: string) => void;
  stopTimer: (id: string) => void;
  removeTimer: (id: string) => void;
  clearAllTimers: () => void;
}

export function useTimers(
  onTimerComplete?: (timer: Timer) => void
): UseTimersReturn {
  const [timers, setTimers] = useState<Timer[]>([]);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Initialize audio for timer completion
  useEffect(() => {
    if (typeof window !== 'undefined') {
      audioRef.current = new Audio('/sounds/timer-complete.mp3');
    }
  }, []);

  // Update timer countdown
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setTimers((prevTimers) => {
        let hasChanges = false;
        const updatedTimers = prevTimers.map((timer) => {
          if (timer.isRunning && !timer.isPaused && timer.remaining > 0) {
            hasChanges = true;
            const newRemaining = timer.remaining - 1;

            // Timer completed
            if (newRemaining <= 0) {
              const completedTimer = {
                ...timer,
                remaining: 0,
                isRunning: false,
                isCompleted: true,
                completedAt: new Date(),
              };

              // Play notification sound
              audioRef.current?.play().catch(console.error);

              // Show browser notification
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('Timer Complete!', {
                  body: `${timer.label} - ${formatTime(timer.duration)}`,
                  icon: '/icons/timer.png',
                });
              }

              // Call callback
              onTimerComplete?.(completedTimer);

              return completedTimer;
            }

            return { ...timer, remaining: newRemaining };
          }
          return timer;
        });

        return hasChanges ? updatedTimers : prevTimers;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [onTimerComplete]);

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const addTimer = useCallback(
    (duration: number, label?: string): string => {
      const id = `timer-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const newTimer: Timer = {
        id,
        label: label || `Timer ${formatTime(duration)}`,
        duration,
        remaining: duration,
        isRunning: false,
        isPaused: false,
        isCompleted: false,
      };

      setTimers((prev) => [...prev, newTimer]);
      return id;
    },
    []
  );

  const startTimer = useCallback((id: string) => {
    setTimers((prev) =>
      prev.map((timer) =>
        timer.id === id
          ? {
              ...timer,
              isRunning: true,
              isPaused: false,
              startedAt: new Date(),
            }
          : timer
      )
    );
  }, []);

  const pauseTimer = useCallback((id: string) => {
    setTimers((prev) =>
      prev.map((timer) =>
        timer.id === id ? { ...timer, isPaused: true } : timer
      )
    );
  }, []);

  const resumeTimer = useCallback((id: string) => {
    setTimers((prev) =>
      prev.map((timer) =>
        timer.id === id ? { ...timer, isPaused: false } : timer
      )
    );
  }, []);

  const stopTimer = useCallback((id: string) => {
    setTimers((prev) =>
      prev.map((timer) =>
        timer.id === id
          ? {
              ...timer,
              isRunning: false,
              isPaused: false,
              remaining: timer.duration,
            }
          : timer
      )
    );
  }, []);

  const removeTimer = useCallback((id: string) => {
    setTimers((prev) => prev.filter((timer) => timer.id !== id));
  }, []);

  const clearAllTimers = useCallback(() => {
    setTimers([]);
  }, []);

  const activeTimers = timers.filter(
    (t) => !t.isCompleted && (t.isRunning || t.remaining > 0)
  );
  const completedTimers = timers.filter((t) => t.isCompleted);

  return {
    timers,
    activeTimers,
    completedTimers,
    addTimer,
    startTimer,
    pauseTimer,
    resumeTimer,
    stopTimer,
    removeTimer,
    clearAllTimers,
  };
}

/**
 * Format seconds to MM:SS or HH:MM:SS
 */
export function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Parse time string to seconds
 * Supports formats like "5m", "1h 30m", "90s", "1:30"
 */
export function parseTimeToSeconds(input: string): number {
  const trimmed = input.trim().toLowerCase();

  // Format: "1:30" or "1:30:45"
  if (trimmed.includes(':')) {
    const parts = trimmed.split(':').map(Number);
    if (parts.length === 2) {
      return parts[0] * 60 + parts[1];
    } else if (parts.length === 3) {
      return parts[0] * 3600 + parts[1] * 60 + parts[2];
    }
  }

  // Format: "5m", "1h 30m", "90s"
  let totalSeconds = 0;

  const hourMatch = trimmed.match(/(\d+)\s*h/);
  if (hourMatch) totalSeconds += parseInt(hourMatch[1]) * 3600;

  const minuteMatch = trimmed.match(/(\d+)\s*m/);
  if (minuteMatch) totalSeconds += parseInt(minuteMatch[1]) * 60;

  const secondMatch = trimmed.match(/(\d+)\s*s/);
  if (secondMatch) totalSeconds += parseInt(secondMatch[1]);

  // If just a number, assume minutes
  if (totalSeconds === 0 && /^\d+$/.test(trimmed)) {
    totalSeconds = parseInt(trimmed) * 60;
  }

  return totalSeconds;
}
