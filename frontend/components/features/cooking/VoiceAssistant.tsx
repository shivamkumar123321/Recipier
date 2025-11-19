/**
 * VoiceAssistant Component
 *
 * Real-time voice interaction with AI cooking assistant
 */

'use client';

import { useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { useState } from 'react';

interface VoiceAssistantMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface VoiceAssistantProps {
  isListening: boolean;
  transcript: string;
  interimTranscript: string;
  messages: VoiceAssistantMessage[];
  isProcessing: boolean;
  isSpeaking: boolean;
  isSupported: boolean;
  onStartListening: () => void;
  onStopListening: () => void;
  onSendMessage?: (message: string) => void;
  suggestions?: string[];
  className?: string;
}

export function VoiceAssistant({
  isListening,
  transcript,
  interimTranscript,
  messages,
  isProcessing,
  isSpeaking,
  isSupported,
  onStartListening,
  onStopListening,
  onSendMessage,
  suggestions = [
    "What's next?",
    'Set a timer for 5 minutes',
    'How long do I cook this?',
    'Show ingredients',
  ],
  className,
}: VoiceAssistantProps) {
  const [textInput, setTextInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Waveform animation
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const draw = () => {
      const width = canvas.width;
      const height = canvas.height;
      const centerY = height / 2;

      ctx.clearRect(0, 0, width, height);

      if (isListening || isSpeaking) {
        // Draw animated waveform
        const time = Date.now() / 1000;
        const barCount = 20;
        const barWidth = width / barCount;

        for (let i = 0; i < barCount; i++) {
          const barHeight =
            Math.sin(time * 3 + i * 0.5) * (height / 4) +
            Math.random() * (height / 8);

          const x = i * barWidth;
          const y = centerY - barHeight / 2;

          ctx.fillStyle = isListening
            ? 'rgba(59, 130, 246, 0.8)' // Blue for listening
            : 'rgba(34, 197, 94, 0.8)'; // Green for speaking

          ctx.fillRect(x + 2, y, barWidth - 4, barHeight);
        }
      } else {
        // Draw idle line
        ctx.strokeStyle = 'rgba(156, 163, 175, 0.5)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(width, centerY);
        ctx.stroke();
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isListening, isSpeaking]);

  const handleSendText = () => {
    if (textInput.trim() && onSendMessage) {
      onSendMessage(textInput.trim());
      setTextInput('');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (onSendMessage) {
      onSendMessage(suggestion);
    }
  };

  if (!isSupported) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="text-center text-sm text-muted-foreground">
            <MicOff className="mx-auto mb-2 h-8 w-8 opacity-50" />
            <p>Voice assistant is not supported in your browser</p>
            <p className="mt-1 text-xs">
              Try using Chrome, Edge, or Safari for voice features
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn('flex flex-col shadow-lg', className)}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-lg">
          <div className="flex items-center gap-2">
            <Volume2 className="h-5 w-5" />
            AI Cooking Assistant
          </div>
          <div className="flex gap-1">
            {isListening && (
              <Badge variant="default" className="animate-pulse">
                Listening
              </Badge>
            )}
            {isSpeaking && (
              <Badge variant="secondary">Speaking</Badge>
            )}
            {isProcessing && (
              <Badge variant="outline">
                <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                Thinking
              </Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex flex-1 flex-col space-y-4">
        {/* Waveform Visualization */}
        <div className="relative rounded-lg border bg-muted/30 p-4">
          <canvas
            ref={canvasRef}
            width={600}
            height={80}
            className="h-20 w-full"
          />

          {/* Transcript Display */}
          <div className="mt-3 min-h-[40px]">
            {isListening && (interimTranscript || transcript) && (
              <div className="rounded bg-blue-50 p-2 text-sm">
                <p className="font-medium text-blue-900">
                  {interimTranscript || transcript}
                </p>
              </div>
            )}
            {!isListening && !isProcessing && messages.length === 0 && (
              <p className="text-center text-sm text-muted-foreground">
                Hold the mic button and speak, or type your question below
              </p>
            )}
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 pr-4" ref={scrollRef}>
          <div className="space-y-3">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-4 py-2',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  )}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="mt-1 text-xs opacity-70">
                    {new Date(message.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* Suggestions */}
        {messages.length === 0 && suggestions.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">
              Try asking:
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Text Input */}
        <div className="flex gap-2">
          <Input
            placeholder="Type your question or command..."
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendText();
              }
            }}
            disabled={isProcessing}
          />
          <Button
            size="icon"
            onClick={handleSendText}
            disabled={!textInput.trim() || isProcessing}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* Voice Button */}
        <div className="flex justify-center">
          <Button
            size="lg"
            className={cn(
              'h-16 w-16 rounded-full transition-all',
              isListening && 'scale-110 bg-blue-600 shadow-lg hover:bg-blue-700'
            )}
            variant={isListening ? 'default' : 'outline'}
            onMouseDown={onStartListening}
            onMouseUp={onStopListening}
            onTouchStart={onStartListening}
            onTouchEnd={onStopListening}
            disabled={isProcessing}
          >
            {isListening ? (
              <Mic className="h-6 w-6 animate-pulse" />
            ) : (
              <MicOff className="h-6 w-6" />
            )}
          </Button>
        </div>

        <p className="text-center text-xs text-muted-foreground">
          Hold to speak • Release to send
        </p>
      </CardContent>
    </Card>
  );
}
