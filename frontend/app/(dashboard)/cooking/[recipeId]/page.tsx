/**
 * Cooking Mode Page
 *
 * Full-screen interactive cooking assistant with voice control
 */

'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
  Maximize2,
  Minimize2,
  Volume2,
  Settings,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent } from '@/components/ui/card';
import { useRecipe } from '@/lib/hooks/useRecipes';
import { useVoiceAssistant } from '@/lib/hooks/useVoiceAssistant';
import { VoiceAssistant } from '@/components/features/cooking/VoiceAssistant';
import { TimerWidget } from '@/components/features/cooking/TimerWidget';
import { cn } from '@/lib/utils';

export default function CookingModePage() {
  const params = useParams();
  const router = useRouter();
  const recipeId = Number(params.recipeId);

  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showVoicePanel, setShowVoicePanel] = useState(true);
  const [autoAdvance, setAutoAdvance] = useState(false);

  // Fetch recipe
  const { data: recipe, isLoading } = useRecipe(recipeId);

  // Voice assistant
  const voiceAssistant = useVoiceAssistant({
    recipeId,
    currentStep,
    onStepChange: (direction) => {
      if (direction === 'next') handleNextStep();
      else handlePreviousStep();
    },
    onShowIngredient: () => {
      // Could show ingredient modal
      console.log('Show ingredients requested');
    },
    onShowNutrition: () => {
      // Could show nutrition modal
      console.log('Show nutrition requested');
    },
  });

  const instructions = recipe?.instructions || [];
  const currentInstruction = instructions[currentStep];
  const progressPercentage = instructions.length
    ? ((currentStep + 1) / instructions.length) * 100
    : 0;

  // Auto-advance when step is marked complete
  useEffect(() => {
    if (autoAdvance && completedSteps.has(currentStep)) {
      const timer = setTimeout(() => {
        if (currentStep < instructions.length - 1) {
          handleNextStep();
        }
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [autoAdvance, completedSteps, currentStep, instructions.length]);

  // Read current step aloud when changed
  useEffect(() => {
    if (currentInstruction && showVoicePanel) {
      const textToSpeak = `Step ${currentStep + 1}. ${currentInstruction.instruction}`;
      voiceAssistant.speak(textToSpeak);
    }
  }, [currentStep, currentInstruction, showVoicePanel]);

  // Fullscreen handling
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleNextStep = () => {
    if (currentStep < instructions.length - 1) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const toggleStepComplete = () => {
    const newCompleted = new Set(completedSteps);
    if (newCompleted.has(currentStep)) {
      newCompleted.delete(currentStep);
    } else {
      newCompleted.add(currentStep);
    }
    setCompletedSteps(newCompleted);
  };

  const handleFinishCooking = () => {
    voiceAssistant.speak('Great job! Your dish is complete.');
    setTimeout(() => {
      router.push(`/recipes/${recipeId}`);
    }, 1500);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto max-w-7xl space-y-8 py-8">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="container mx-auto max-w-7xl py-16 text-center">
        <h2 className="text-2xl font-bold">Recipe not found</h2>
        <Link href="/recipes">
          <Button className="mt-6">Back to Recipes</Button>
        </Link>
      </div>
    );
  }

  const isLastStep = currentStep === instructions.length - 1;
  const allStepsCompleted = completedSteps.size === instructions.length;

  return (
    <div
      className={cn(
        'min-h-screen bg-background',
        isFullscreen && 'bg-black text-white'
      )}
    >
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <div className="flex items-center gap-4">
            <Link href={`/recipes/${recipeId}`}>
              <Button variant="ghost" size="sm">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Exit Cooking
              </Button>
            </Link>
            <div>
              <h1 className="text-xl font-bold">{recipe.name}</h1>
              <p className="text-sm text-muted-foreground">
                Step {currentStep + 1} of {instructions.length}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowVoicePanel(!showVoicePanel)}
            >
              <Volume2 className="mr-2 h-4 w-4" />
              {showVoicePanel ? 'Hide' : 'Show'} Assistant
            </Button>
            <Button variant="outline" size="sm" onClick={toggleFullscreen}>
              {isFullscreen ? (
                <Minimize2 className="h-4 w-4" />
              ) : (
                <Maximize2 className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Progress Bar */}
        <Progress value={progressPercentage} className="h-2 rounded-none" />
      </div>

      {/* Main Content */}
      <div className="container mx-auto grid gap-8 p-8 lg:grid-cols-3">
        {/* Left: Current Step (Large Display) */}
        <div className="lg:col-span-2">
          <Card className="border-2">
            <CardContent className="p-8">
              {/* Step Number Badge */}
              <div className="mb-6 flex items-center justify-between">
                <Badge variant="outline" className="text-lg px-4 py-2">
                  Step {currentStep + 1} / {instructions.length}
                </Badge>
                {currentInstruction?.time_estimate && (
                  <Badge variant="secondary" className="text-base px-4 py-2">
                    ~{currentInstruction.time_estimate} min
                  </Badge>
                )}
              </div>

              {/* Instruction Text - Large for readability */}
              <div className="mb-8 min-h-[200px]">
                <p
                  className={cn(
                    'text-3xl font-medium leading-relaxed',
                    isFullscreen && 'text-4xl'
                  )}
                >
                  {currentInstruction?.instruction}
                </p>
              </div>

              {/* Step Image (if available) */}
              {currentInstruction?.image_url && (
                <div className="mb-6">
                  <img
                    src={currentInstruction.image_url}
                    alt={`Step ${currentStep + 1}`}
                    className="h-64 w-full rounded-lg object-cover"
                  />
                </div>
              )}

              {/* Navigation & Actions */}
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex gap-2">
                  <Button
                    size="lg"
                    variant="outline"
                    onClick={handlePreviousStep}
                    disabled={currentStep === 0}
                  >
                    <ChevronLeft className="mr-2 h-5 w-5" />
                    Previous
                  </Button>

                  <Button
                    size="lg"
                    variant={
                      completedSteps.has(currentStep) ? 'secondary' : 'outline'
                    }
                    onClick={toggleStepComplete}
                    className="gap-2"
                  >
                    {completedSteps.has(currentStep) ? (
                      <>
                        <Check className="h-5 w-5" />
                        Completed
                      </>
                    ) : (
                      <>
                        <X className="h-5 w-5" />
                        Mark Complete
                      </>
                    )}
                  </Button>
                </div>

                {!isLastStep ? (
                  <Button size="lg" onClick={handleNextStep}>
                    Next Step
                    <ChevronRight className="ml-2 h-5 w-5" />
                  </Button>
                ) : (
                  <Button
                    size="lg"
                    variant="default"
                    onClick={handleFinishCooking}
                    disabled={!allStepsCompleted}
                  >
                    Finish Cooking
                    <Check className="ml-2 h-5 w-5" />
                  </Button>
                )}
              </div>

              {/* Step Progress Dots */}
              <div className="mt-8 flex flex-wrap gap-2">
                {instructions.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentStep(index)}
                    className={cn(
                      'h-3 w-3 rounded-full transition-all',
                      index === currentStep && 'ring-2 ring-primary ring-offset-2',
                      completedSteps.has(index)
                        ? 'bg-green-500'
                        : index === currentStep
                          ? 'bg-primary'
                          : 'bg-muted'
                    )}
                    title={`Step ${index + 1}`}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right: Voice Assistant & Timers */}
        <div className="space-y-6">
          {/* Voice Assistant */}
          {showVoicePanel && (
            <VoiceAssistant
              isListening={voiceAssistant.isListening}
              transcript={voiceAssistant.transcript}
              interimTranscript={voiceAssistant.interimTranscript}
              messages={voiceAssistant.messages}
              isProcessing={voiceAssistant.isProcessing}
              isSpeaking={voiceAssistant.isSpeaking}
              isSupported={voiceAssistant.isSupported}
              onStartListening={voiceAssistant.startListening}
              onStopListening={voiceAssistant.stopListening}
              onSendMessage={voiceAssistant.sendMessage}
              suggestions={[
                "What's next?",
                'Set a timer for 5 minutes',
                'How long do I cook this?',
                'Repeat the step',
                'Show ingredients',
              ]}
              className="max-h-[500px]"
            />
          )}

          {/* Timers */}
          <TimerWidget
            timers={voiceAssistant.timers}
            activeTimers={voiceAssistant.activeTimers}
            onAddTimer={voiceAssistant.addTimer}
            onStartTimer={(id) => {
              // Find timer in the hook and start it
              const timer = voiceAssistant.timers.find((t) => t.id === id);
              if (timer) {
                // This would need to be exposed from useVoiceAssistant
                console.log('Start timer:', id);
              }
            }}
            onPauseTimer={(id) => console.log('Pause timer:', id)}
            onResumeTimer={(id) => console.log('Resume timer:', id)}
            onStopTimer={(id) => console.log('Stop timer:', id)}
            onRemoveTimer={(id) => console.log('Remove timer:', id)}
          />

          {/* Quick Settings */}
          <Card>
            <CardContent className="space-y-3 pt-6">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Auto-advance steps</span>
                <Button
                  variant={autoAdvance ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setAutoAdvance(!autoAdvance)}
                >
                  {autoAdvance ? 'ON' : 'OFF'}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Automatically move to next step when marked complete
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
