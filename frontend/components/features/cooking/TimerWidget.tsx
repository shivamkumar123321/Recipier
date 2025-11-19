/**
 * TimerWidget Component
 *
 * Display and manage multiple cooking timers
 */

'use client';

import { useState } from 'react';
import { Timer as TimerIcon, Play, Pause, X, Plus, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Timer, formatTime, parseTimeToSeconds } from '@/lib/hooks/useTimers';
import { cn } from '@/lib/utils';

interface TimerWidgetProps {
  timers: Timer[];
  activeTimers: Timer[];
  onAddTimer: (duration: number, label?: string) => string;
  onStartTimer: (id: string) => void;
  onPauseTimer: (id: string) => void;
  onResumeTimer: (id: string) => void;
  onStopTimer: (id: string) => void;
  onRemoveTimer: (id: string) => void;
  className?: string;
}

export function TimerWidget({
  timers,
  activeTimers,
  onAddTimer,
  onStartTimer,
  onPauseTimer,
  onResumeTimer,
  onStopTimer,
  onRemoveTimer,
  className,
}: TimerWidgetProps) {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newTimerLabel, setNewTimerLabel] = useState('');
  const [newTimerDuration, setNewTimerDuration] = useState('');

  const handleAddTimer = () => {
    const duration = parseTimeToSeconds(newTimerDuration);
    if (duration > 0) {
      const timerId = onAddTimer(
        duration,
        newTimerLabel || `Timer ${formatTime(duration)}`
      );
      onStartTimer(timerId);
      setNewTimerLabel('');
      setNewTimerDuration('');
      setIsAddDialogOpen(false);
    }
  };

  const getTimerColor = (timer: Timer) => {
    if (timer.isCompleted) return 'border-green-500 bg-green-50';
    if (!timer.isRunning) return 'border-gray-300 bg-gray-50';

    const percentage = (timer.remaining / timer.duration) * 100;
    if (percentage < 10) return 'border-red-500 bg-red-50 animate-pulse';
    if (percentage < 30) return 'border-orange-500 bg-orange-50';
    return 'border-blue-500 bg-blue-50';
  };

  const getProgressPercentage = (timer: Timer) => {
    return ((timer.duration - timer.remaining) / timer.duration) * 100;
  };

  return (
    <Card className={cn('shadow-lg', className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TimerIcon className="h-5 w-5" />
          Timers
          {activeTimers.length > 0 && (
            <Badge variant="default" className="ml-2">
              {activeTimers.length}
            </Badge>
          )}
        </CardTitle>

        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" variant="outline">
              <Plus className="mr-1 h-4 w-4" />
              Add Timer
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Timer</DialogTitle>
              <DialogDescription>
                Set a timer to track cooking times hands-free
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="timer-duration">Duration</Label>
                <Input
                  id="timer-duration"
                  placeholder="e.g., 5m, 1h 30m, 90s"
                  value={newTimerDuration}
                  onChange={(e) => setNewTimerDuration(e.target.value)}
                  autoFocus
                />
                <p className="text-xs text-muted-foreground">
                  Formats: 5m, 1h 30m, 90s, 1:30
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="timer-label">Label (optional)</Label>
                <Input
                  id="timer-label"
                  placeholder="e.g., Boil pasta"
                  value={newTimerLabel}
                  onChange={(e) => setNewTimerLabel(e.target.value)}
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsAddDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddTimer}
                disabled={!newTimerDuration.trim()}
              >
                Start Timer
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardHeader>

      <CardContent className="space-y-3">
        {timers.length === 0 ? (
          <div className="py-8 text-center text-sm text-muted-foreground">
            <TimerIcon className="mx-auto mb-2 h-8 w-8 opacity-50" />
            <p>No active timers</p>
            <p className="mt-1 text-xs">
              Say "set a timer for 5 minutes" or click Add Timer
            </p>
          </div>
        ) : (
          timers.map((timer) => (
            <div
              key={timer.id}
              className={cn(
                'relative overflow-hidden rounded-lg border-2 p-3 transition-all',
                getTimerColor(timer)
              )}
            >
              {/* Progress bar background */}
              <div
                className="absolute inset-0 bg-primary/10 transition-all duration-1000"
                style={{
                  width: `${getProgressPercentage(timer)}%`,
                }}
              />

              <div className="relative flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium">{timer.label}</h4>
                    {timer.isCompleted && (
                      <AlertCircle className="h-4 w-4 text-green-600" />
                    )}
                  </div>
                  <div
                    className={cn(
                      'text-2xl font-bold tabular-nums',
                      timer.remaining < 10 && timer.isRunning && 'text-red-600'
                    )}
                  >
                    {formatTime(timer.remaining)}
                  </div>
                </div>

                <div className="flex items-center gap-1">
                  {!timer.isCompleted && (
                    <>
                      {timer.isRunning && !timer.isPaused ? (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => onPauseTimer(timer.id)}
                        >
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() =>
                            timer.isPaused
                              ? onResumeTimer(timer.id)
                              : onStartTimer(timer.id)
                          }
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                    </>
                  )}

                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onRemoveTimer(timer.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {timer.isPaused && (
                <div className="mt-2">
                  <Badge variant="secondary" className="text-xs">
                    Paused
                  </Badge>
                </div>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
