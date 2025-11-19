/**
 * VoiceInputTab Component
 *
 * Voice input for adding inventory items
 * Uses Web Audio API for recording
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  useParseVoiceInput,
  useBulkCreateInventoryItems,
  useFoodCategories,
} from '@/lib/hooks/useInventory';
import { ParsedInventoryItem } from '@/lib/api/inventory';
import { ParsedItemsList } from './ParsedItemsList';

interface VoiceInputTabProps {
  onSuccess?: () => void;
}

export function VoiceInputTab({ onSuccess }: VoiceInputTabProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [transcription, setTranscription] = useState('');
  const [parsedItems, setParsedItems] = useState<ParsedInventoryItem[]>([]);
  const [error, setError] = useState<string>('');

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const parseVoice = useParseVoiceInput();
  const bulkCreate = useBulkCreateInventoryItems();
  const { data: categories = [] } = useFoodCategories();

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [isRecording]);

  const startRecording = async () => {
    try {
      setError('');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: 'audio/webm',
        });
        setAudioBlob(audioBlob);

        // Stop all tracks to release the microphone
        stream.getTracks().forEach((track) => track.stop());

        // Automatically process the audio
        await processAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError(
        'Unable to access microphone. Please check your browser permissions.'
      );
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (blob: Blob) => {
    try {
      const result = await parseVoice.mutateAsync(blob);
      setTranscription(result.transcription);
      setParsedItems(result.items);
    } catch (err) {
      setError('Failed to process voice input. Please try again.');
    }
  };

  const handleAddItems = async () => {
    if (parsedItems.length === 0) return;

    try {
      // Map parsed items to create requests with category IDs
      const itemsToCreate = parsedItems.map((item) => {
        // Find category by name or use first category as default
        const category = categories.find(
          (cat) =>
            cat.name.toLowerCase() === item.category?.toLowerCase()
        ) || categories[0];

        return {
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          category_id: category?.id || 1,
          expiration_date: item.expiration_date,
        };
      });

      await bulkCreate.mutateAsync(itemsToCreate);

      // Reset state
      setAudioBlob(null);
      setTranscription('');
      setParsedItems([]);

      onSuccess?.();
    } catch (err) {
      setError('Failed to add items. Please try again.');
    }
  };

  const handleReset = () => {
    setAudioBlob(null);
    setTranscription('');
    setParsedItems([]);
    setError('');
  };

  return (
    <div className="space-y-6">
      {/* Instructions */}
      {!audioBlob && !isRecording && (
        <Alert>
          <AlertDescription>
            Click the microphone button and say something like: "I bought 2
            pounds of chicken, 1 gallon of milk, and 6 eggs"
          </AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Recording Interface */}
      <div className="flex flex-col items-center justify-center space-y-4 py-8">
        {isRecording ? (
          <>
            <div className="relative">
              <div className="absolute inset-0 animate-ping rounded-full bg-red-400 opacity-75"></div>
              <Button
                size="lg"
                variant="destructive"
                className="relative h-24 w-24 rounded-full"
                onClick={stopRecording}
              >
                <MicOff className="h-12 w-12" />
              </Button>
            </div>
            <p className="text-lg font-medium">Recording... Click to stop</p>
          </>
        ) : audioBlob ? (
          <>
            <div className="flex items-center gap-4">
              <Button onClick={handleReset} variant="outline">
                Record Again
              </Button>
            </div>
          </>
        ) : (
          <>
            <Button
              size="lg"
              className="h-24 w-24 rounded-full"
              onClick={startRecording}
              disabled={parseVoice.isPending}
            >
              <Mic className="h-12 w-12" />
            </Button>
            <p className="text-sm text-muted-foreground">Click to start recording</p>
          </>
        )}
      </div>

      {/* Processing State */}
      {parseVoice.isPending && (
        <div className="flex items-center justify-center gap-2 py-4">
          <Loader2 className="h-5 w-5 animate-spin" />
          <p className="text-sm text-muted-foreground">
            Processing your voice input...
          </p>
        </div>
      )}

      {/* Transcription */}
      {transcription && (
        <div className="rounded-lg border bg-muted p-4">
          <h4 className="mb-2 font-medium">You said:</h4>
          <p className="text-sm">{transcription}</p>
        </div>
      )}

      {/* Parsed Items */}
      {parsedItems.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-medium">Detected Items:</h4>
          <ParsedItemsList
            items={parsedItems}
            categories={categories}
            onUpdate={setParsedItems}
          />

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={handleReset}>
              Cancel
            </Button>
            <Button
              onClick={handleAddItems}
              disabled={bulkCreate.isPending}
            >
              {bulkCreate.isPending ? 'Adding...' : `Add ${parsedItems.length} Item(s)`}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
