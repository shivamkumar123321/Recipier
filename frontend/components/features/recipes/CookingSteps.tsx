/**
 * CookingSteps Component
 *
 * Display recipe instructions step by step
 */

'use client';

import { useState } from 'react';
import { Clock, ChefHat, CheckCircle2 } from 'lucide-react';
import { RecipeInstruction } from '@/lib/api/recipes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';

interface CookingStepsProps {
  instructions: RecipeInstruction[];
  prepTime?: number;
  cookTime?: number;
  className?: string;
  interactive?: boolean;
}

export function CookingSteps({
  instructions,
  prepTime,
  cookTime,
  className,
  interactive = false,
}: CookingStepsProps) {
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const sortedInstructions = [...instructions].sort(
    (a, b) => a.step_number - b.step_number
  );

  const toggleStep = (stepNumber: number) => {
    const newCompleted = new Set(completedSteps);
    if (newCompleted.has(stepNumber)) {
      newCompleted.delete(stepNumber);
    } else {
      newCompleted.add(stepNumber);
    }
    setCompletedSteps(newCompleted);
  };

  const getTotalTime = (): number => {
    return instructions.reduce(
      (total, inst) => total + (inst.time_minutes || 0),
      0
    );
  };

  const completionPercentage = interactive
    ? Math.round((completedSteps.size / instructions.length) * 100)
    : 0;

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <ChefHat className="h-5 w-5" />
            Instructions
          </CardTitle>
          <div className="flex items-center gap-2">
            {prepTime && (
              <Badge variant="outline" className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Prep: {prepTime}min
              </Badge>
            )}
            {cookTime && (
              <Badge variant="outline" className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Cook: {cookTime}min
              </Badge>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {interactive && (
          <div className="mt-3">
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">
                {completedSteps.size} / {instructions.length} steps
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {sortedInstructions.map((instruction) => {
          const isCompleted = completedSteps.has(instruction.step_number);

          return (
            <div
              key={instruction.id}
              className={cn(
                'flex gap-4 rounded-lg border p-4 transition-colors',
                isCompleted && 'border-green-200 bg-green-50',
                !isCompleted && 'border-muted'
              )}
            >
              {/* Step Number or Checkbox */}
              {interactive ? (
                <Checkbox
                  checked={isCompleted}
                  onCheckedChange={() => toggleStep(instruction.step_number)}
                  className="mt-1"
                />
              ) : (
                <div
                  className={cn(
                    'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border-2 font-semibold',
                    isCompleted
                      ? 'border-green-500 bg-green-500 text-white'
                      : 'border-primary text-primary'
                  )}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="h-5 w-5" />
                  ) : (
                    instruction.step_number
                  )}
                </div>
              )}

              {/* Instruction Content */}
              <div className="flex-1">
                <div className="flex items-start justify-between gap-4">
                  <p
                    className={cn(
                      'text-sm leading-relaxed',
                      isCompleted && 'text-green-900 line-through'
                    )}
                  >
                    {instruction.instruction}
                  </p>
                  {instruction.time_minutes && (
                    <Badge
                      variant="secondary"
                      className="flex-shrink-0 flex items-center gap-1"
                    >
                      <Clock className="h-3 w-3" />
                      {instruction.time_minutes}min
                    </Badge>
                  )}
                </div>

                {/* Optional Image */}
                {instruction.image_url && (
                  <img
                    src={instruction.image_url}
                    alt={`Step ${instruction.step_number}`}
                    className="mt-3 h-40 w-full rounded-md object-cover"
                  />
                )}
              </div>
            </div>
          );
        })}

        {/* Summary */}
        <div className="flex items-center justify-between rounded-lg bg-muted p-4 text-sm">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Estimated time:</span>
            <span className="font-medium">
              {prepTime && cookTime ? prepTime + cookTime : getTotalTime()} minutes
            </span>
          </div>

          {interactive && completedSteps.size === instructions.length && (
            <Badge className="bg-green-500">
              <CheckCircle2 className="mr-1 h-3 w-3" />
              Completed!
            </Badge>
          )}
        </div>

        {/* Tips */}
        {interactive && (
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <h4 className="mb-2 font-medium text-blue-900">Cooking Tips</h4>
            <ul className="space-y-1 text-sm text-blue-800">
              <li>• Read all steps before starting</li>
              <li>• Prepare all ingredients (mise en place)</li>
              <li>• Use the voice assistant for hands-free cooking</li>
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
