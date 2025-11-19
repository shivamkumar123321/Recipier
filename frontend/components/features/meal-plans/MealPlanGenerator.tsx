/**
 * MealPlanGenerator Component
 *
 * Real-time meal plan generation with WebSocket and progressive rendering
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { useMealPlanGeneration } from '@/lib/hooks/useMealPlanGeneration';
import { CreateMealPlanRequest } from '@/lib/api/meal-plans';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';

interface MealPlanGeneratorProps {
  request: CreateMealPlanRequest;
  onCancel?: () => void;
}

export function MealPlanGenerator({
  request,
  onCancel,
}: MealPlanGeneratorProps) {
  const router = useRouter();
  const { isConnected, isGenerating, progress, error, generate, cancel } =
    useMealPlanGeneration({
      onComplete: (mealPlan) => {
        // Navigate to the generated meal plan
        setTimeout(() => {
          router.push(`/meal-plans/${mealPlan.id}`);
        }, 1500);
      },
      onError: (errorMsg) => {
        console.error('Generation failed:', errorMsg);
      },
    });

  // Start generation when component mounts
  useEffect(() => {
    if (isConnected && !isGenerating) {
      generate(request);
    }
  }, [isConnected]);

  const handleCancel = () => {
    cancel();
    onCancel?.();
  };

  const getStatusIcon = () => {
    if (error) {
      return <AlertCircle className="h-8 w-8 text-destructive" />;
    }
    if (progress?.status === 'complete') {
      return <CheckCircle2 className="h-8 w-8 text-green-600" />;
    }
    return <Loader2 className="h-8 w-8 animate-spin text-primary" />;
  };

  const getStatusText = () => {
    if (error) return 'Generation Failed';
    if (!isConnected) return 'Connecting...';
    if (progress?.status === 'complete') return 'Plan Generated Successfully!';
    if (progress?.status === 'thinking') return 'Analyzing Your Preferences...';
    if (progress?.status === 'generating') return 'Generating Your Meal Plan...';
    return 'Initializing...';
  };

  const getProgressValue = () => {
    if (progress?.status === 'complete') return 100;
    return progress?.progress || 0;
  };

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-center space-x-4">
            {getStatusIcon()}
            <CardTitle className="text-2xl">{getStatusText()}</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>{progress?.current_step || 'Preparing...'}</span>
              <span>{Math.round(getProgressValue())}%</span>
            </div>
            <Progress value={getProgressValue()} className="h-2" />
          </div>

          {/* Meals Generated Counter */}
          {progress && progress.meals_generated !== undefined && (
            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                Meals Generated:{' '}
                <span className="font-semibold text-foreground">
                  {progress.meals_generated} / {progress.total_meals || '...'}
                </span>
              </p>
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Success Message */}
          {progress?.status === 'complete' && (
            <Alert>
              <CheckCircle2 className="h-4 w-4" />
              <AlertDescription>
                Your personalized meal plan is ready! Redirecting...
              </AlertDescription>
            </Alert>
          )}

          {/* Cancel Button */}
          {isGenerating && progress?.status !== 'complete' && (
            <div className="flex justify-center">
              <Button variant="outline" onClick={handleCancel}>
                Cancel Generation
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Progressive Meal Preview */}
      {isGenerating && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            <Sparkles className="mr-2 inline h-5 w-5 text-primary" />
            Your Personalized Meal Plan
          </h3>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Show skeleton loaders for meals being generated */}
            {Array.from({
              length: progress?.meals_generated || 3,
            }).map((_, index) => (
              <Card key={index} className="overflow-hidden">
                <div className="relative h-32 bg-gradient-to-br from-primary/10 to-secondary/10">
                  <Skeleton className="h-full w-full" />
                </div>
                <CardContent className="space-y-2 p-4">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-4 w-32" />
                </CardContent>
              </Card>
            ))}

            {/* Show placeholders for remaining meals */}
            {progress &&
              progress.total_meals &&
              progress.meals_generated !== undefined &&
              Array.from({
                length: progress.total_meals - progress.meals_generated,
              }).map((_, index) => (
                <Card
                  key={`placeholder-${index}`}
                  className="overflow-hidden opacity-40"
                >
                  <div className="relative h-32 bg-muted">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  </div>
                  <CardContent className="space-y-2 p-4">
                    <div className="h-4 w-24 bg-muted rounded" />
                    <div className="h-6 w-full bg-muted rounded" />
                    <div className="h-4 w-32 bg-muted rounded" />
                  </CardContent>
                </Card>
              ))}
          </div>
        </div>
      )}

      {/* Generation Info */}
      <Card className="bg-muted/50">
        <CardContent className="p-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Duration
              </p>
              <p className="text-lg font-semibold">
                {request.total_days} Days
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Goal</p>
              <p className="text-lg font-semibold capitalize">
                {request.goal.replace('_', ' ')}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Dietary Preferences
              </p>
              <p className="text-lg font-semibold">
                {request.dietary_preferences.length > 0
                  ? request.dietary_preferences.join(', ')
                  : 'None'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
