/**
 * NutritionInfo Component
 *
 * Display nutrition information with visual indicators
 */

'use client';

import { Flame, Droplet, Wheat } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface NutritionInfoProps {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber?: number;
  sodium?: number;
  servings?: number;
  className?: string;
}

export function NutritionInfo({
  calories,
  protein,
  carbs,
  fat,
  fiber,
  sodium,
  servings = 1,
  className,
}: NutritionInfoProps) {
  // Calculate macros percentage
  const proteinCalories = protein * 4;
  const carbsCalories = carbs * 4;
  const fatCalories = fat * 9;
  const totalMacroCalories = proteinCalories + carbsCalories + fatCalories;

  const proteinPercent = (proteinCalories / totalMacroCalories) * 100;
  const carbsPercent = (carbsCalories / totalMacroCalories) * 100;
  const fatPercent = (fatCalories / totalMacroCalories) * 100;

  // Daily value percentages (based on 2000 calorie diet)
  const dailyValues = {
    calories: (calories / 2000) * 100,
    protein: (protein / 50) * 100,
    carbs: (carbs / 300) * 100,
    fat: (fat / 65) * 100,
    fiber: fiber ? (fiber / 25) * 100 : 0,
    sodium: sodium ? (sodium / 2300) * 100 : 0,
  };

  const getMacroColor = (macro: string) => {
    const colors = {
      protein: 'bg-red-500',
      carbs: 'bg-blue-500',
      fat: 'bg-yellow-500',
    };
    return colors[macro as keyof typeof colors];
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="h-5 w-5" />
          Nutrition Facts
        </CardTitle>
        {servings > 1 && (
          <p className="text-sm text-muted-foreground">
            Per serving ({servings} servings)
          </p>
        )}
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Calories */}
        <div className="rounded-lg border-2 border-primary/20 bg-primary/5 p-4 text-center">
          <p className="text-sm font-medium text-muted-foreground">Calories</p>
          <p className="text-4xl font-bold text-primary">{calories}</p>
          <p className="text-xs text-muted-foreground">
            {Math.round(dailyValues.calories)}% of daily value
          </p>
        </div>

        {/* Macros Breakdown */}
        <div>
          <h4 className="mb-3 font-medium">Macronutrients</h4>
          <div className="space-y-4">
            {/* Protein */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-500" />
                  <span className="font-medium">Protein</span>
                </div>
                <div className="text-right">
                  <span className="font-semibold">{protein}g</span>
                  <span className="ml-2 text-sm text-muted-foreground">
                    {Math.round(proteinPercent)}%
                  </span>
                </div>
              </div>
              <Progress
                value={dailyValues.protein}
                className="h-2"
                style={
                  {
                    '--progress-background': 'rgb(239 68 68)',
                  } as React.CSSProperties
                }
              />
              <p className="mt-1 text-xs text-muted-foreground">
                {Math.round(dailyValues.protein)}% DV
              </p>
            </div>

            {/* Carbs */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-blue-500" />
                  <span className="font-medium">Carbohydrates</span>
                </div>
                <div className="text-right">
                  <span className="font-semibold">{carbs}g</span>
                  <span className="ml-2 text-sm text-muted-foreground">
                    {Math.round(carbsPercent)}%
                  </span>
                </div>
              </div>
              <Progress
                value={dailyValues.carbs}
                className="h-2"
                style={
                  {
                    '--progress-background': 'rgb(59 130 246)',
                  } as React.CSSProperties
                }
              />
              <p className="mt-1 text-xs text-muted-foreground">
                {Math.round(dailyValues.carbs)}% DV
              </p>
            </div>

            {/* Fat */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-yellow-500" />
                  <span className="font-medium">Fat</span>
                </div>
                <div className="text-right">
                  <span className="font-semibold">{fat}g</span>
                  <span className="ml-2 text-sm text-muted-foreground">
                    {Math.round(fatPercent)}%
                  </span>
                </div>
              </div>
              <Progress
                value={dailyValues.fat}
                className="h-2"
                style={
                  {
                    '--progress-background': 'rgb(234 179 8)',
                  } as React.CSSProperties
                }
              />
              <p className="mt-1 text-xs text-muted-foreground">
                {Math.round(dailyValues.fat)}% DV
              </p>
            </div>
          </div>
        </div>

        {/* Macro Distribution Pie */}
        <div className="rounded-lg bg-muted/50 p-4">
          <h4 className="mb-3 text-sm font-medium">Macro Distribution</h4>
          <div className="flex h-4 overflow-hidden rounded-full">
            <div
              className="bg-red-500"
              style={{ width: `${proteinPercent}%` }}
              title={`Protein: ${Math.round(proteinPercent)}%`}
            />
            <div
              className="bg-blue-500"
              style={{ width: `${carbsPercent}%` }}
              title={`Carbs: ${Math.round(carbsPercent)}%`}
            />
            <div
              className="bg-yellow-500"
              style={{ width: `${fatPercent}%` }}
              title={`Fat: ${Math.round(fatPercent)}%`}
            />
          </div>
          <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
            <div className="text-center">
              <div className="font-medium text-red-700">
                {Math.round(proteinPercent)}%
              </div>
              <div className="text-muted-foreground">Protein</div>
            </div>
            <div className="text-center">
              <div className="font-medium text-blue-700">
                {Math.round(carbsPercent)}%
              </div>
              <div className="text-muted-foreground">Carbs</div>
            </div>
            <div className="text-center">
              <div className="font-medium text-yellow-700">
                {Math.round(fatPercent)}%
              </div>
              <div className="text-muted-foreground">Fat</div>
            </div>
          </div>
        </div>

        {/* Other Nutrients */}
        {(fiber || sodium) && (
          <div>
            <h4 className="mb-3 font-medium">Other Nutrients</h4>
            <div className="space-y-2 rounded-lg border p-3">
              {fiber && (
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Wheat className="h-4 w-4 text-muted-foreground" />
                    <span>Dietary Fiber</span>
                  </div>
                  <div className="text-right">
                    <span className="font-medium">{fiber}g</span>
                    <span className="ml-2 text-muted-foreground">
                      {Math.round(dailyValues.fiber)}% DV
                    </span>
                  </div>
                </div>
              )}
              {sodium && (
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Droplet className="h-4 w-4 text-muted-foreground" />
                    <span>Sodium</span>
                  </div>
                  <div className="text-right">
                    <span className="font-medium">{sodium}mg</span>
                    <span className="ml-2 text-muted-foreground">
                      {Math.round(dailyValues.sodium)}% DV
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <p className="text-xs text-muted-foreground">
          * Percent Daily Values are based on a 2,000 calorie diet. Your daily
          values may be higher or lower depending on your calorie needs.
        </p>
      </CardContent>
    </Card>
  );
}
