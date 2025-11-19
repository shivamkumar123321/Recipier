/**
 * GoalsForm Component
 *
 * Manage health goals, calorie targets, and macro preferences
 */

'use client';

import { useState, useEffect } from 'react';
import { Loader2, Save, Target, TrendingDown, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useUserProfile, useUpdateGoals } from '@/lib/hooks/useUser';
import { calculateRecommendedCalories, calculateRecommendedMacros } from '@/lib/api/user';

export function GoalsForm() {
  const { data: profile } = useUserProfile();
  const updateMutation = useUpdateGoals();

  const [goal, setGoal] = useState<string>('');
  const [targetWeightKg, setTargetWeightKg] = useState('');
  const [activityLevel, setActivityLevel] = useState<string>('');
  const [targetCalories, setTargetCalories] = useState('');
  const [targetProteinG, setTargetProteinG] = useState('');
  const [targetCarbsG, setTargetCarbsG] = useState('');
  const [targetFatG, setTargetFatG] = useState('');

  // Load existing data
  useEffect(() => {
    if (profile) {
      setGoal(profile.goal || '');
      setTargetWeightKg(profile.target_weight_kg?.toString() || '');
      setActivityLevel(profile.activity_level || '');
      setTargetCalories(profile.target_calories?.toString() || '');
      setTargetProteinG(profile.target_protein_g?.toString() || '');
      setTargetCarbsG(profile.target_carbs_g?.toString() || '');
      setTargetFatG(profile.target_fat_g?.toString() || '');
    }
  }, [profile]);

  const handleCalculateRecommended = () => {
    if (!profile?.height_cm || !profile?.current_weight_kg || !profile?.date_of_birth) {
      alert('Please complete your profile information first');
      return;
    }

    const age = new Date().getFullYear() - new Date(profile.date_of_birth).getFullYear();
    const gender = profile.gender === 'male' ? 'male' : 'female';
    const selectedGoal = goal as 'weight_loss' | 'maintenance' | 'muscle_gain';
    const selectedActivity = activityLevel as any;

    const recommendedCalories = calculateRecommendedCalories(
      profile.current_weight_kg,
      profile.height_cm,
      age,
      gender,
      selectedActivity,
      selectedGoal
    );

    const recommendedMacros = calculateRecommendedMacros(
      recommendedCalories,
      selectedGoal
    );

    setTargetCalories(recommendedCalories.toString());
    setTargetProteinG(recommendedMacros.protein_g.toString());
    setTargetCarbsG(recommendedMacros.carbs_g.toString());
    setTargetFatG(recommendedMacros.fat_g.toString());
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await updateMutation.mutateAsync({
        goal: goal as any,
        target_weight_kg: targetWeightKg ? parseFloat(targetWeightKg) : undefined,
        activity_level: activityLevel as any,
        target_calories: targetCalories ? parseInt(targetCalories) : undefined,
        target_protein_g: targetProteinG ? parseInt(targetProteinG) : undefined,
        target_carbs_g: targetCarbsG ? parseInt(targetCarbsG) : undefined,
        target_fat_g: targetFatG ? parseInt(targetFatG) : undefined,
      });

      alert('Goals updated successfully!');
    } catch (error) {
      console.error('Failed to update goals:', error);
      alert('Failed to update goals. Please try again.');
    }
  };

  // Calculate progress towards goal
  const weightProgress = profile?.current_weight_kg && profile?.target_weight_kg && targetWeightKg
    ? Math.abs(
        ((profile.current_weight_kg - parseFloat(targetWeightKg)) /
          (profile.current_weight_kg - profile.target_weight_kg)) *
          100
      )
    : 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Primary Goal */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Primary Goal
          </CardTitle>
          <CardDescription>
            What do you want to achieve with your nutrition plan?
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            <button
              type="button"
              onClick={() => setGoal('weight_loss')}
              className={`rounded-lg border-2 p-4 text-center transition-all ${
                goal === 'weight_loss'
                  ? 'border-red-500 bg-red-50'
                  : 'border-border hover:border-red-300'
              }`}
            >
              <TrendingDown className="mx-auto h-8 w-8 text-red-600" />
              <p className="mt-2 font-semibold">Weight Loss</p>
              <p className="mt-1 text-xs text-muted-foreground">Lose fat</p>
            </button>

            <button
              type="button"
              onClick={() => setGoal('maintenance')}
              className={`rounded-lg border-2 p-4 text-center transition-all ${
                goal === 'maintenance'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-border hover:border-blue-300'
              }`}
            >
              <Target className="mx-auto h-8 w-8 text-blue-600" />
              <p className="mt-2 font-semibold">Maintenance</p>
              <p className="mt-1 text-xs text-muted-foreground">Stay healthy</p>
            </button>

            <button
              type="button"
              onClick={() => setGoal('muscle_gain')}
              className={`rounded-lg border-2 p-4 text-center transition-all ${
                goal === 'muscle_gain'
                  ? 'border-green-500 bg-green-50'
                  : 'border-border hover:border-green-300'
              }`}
            >
              <Activity className="mx-auto h-8 w-8 text-green-600" />
              <p className="mt-2 font-semibold">Muscle Gain</p>
              <p className="mt-1 text-xs text-muted-foreground">Build muscle</p>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Weight & Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Weight & Activity</CardTitle>
          <CardDescription>
            Set your target weight and activity level
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="target-weight">Target Weight (kg)</Label>
              <Input
                id="target-weight"
                type="number"
                value={targetWeightKg}
                onChange={(e) => setTargetWeightKg(e.target.value)}
                placeholder="65"
                step="0.1"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="activity-level">Activity Level</Label>
              <Select value={activityLevel} onValueChange={setActivityLevel}>
                <SelectTrigger id="activity-level">
                  <SelectValue placeholder="Select activity level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sedentary">
                    Sedentary (little/no exercise)
                  </SelectItem>
                  <SelectItem value="light">
                    Light (exercise 1-3 days/week)
                  </SelectItem>
                  <SelectItem value="moderate">
                    Moderate (exercise 3-5 days/week)
                  </SelectItem>
                  <SelectItem value="active">
                    Active (exercise 6-7 days/week)
                  </SelectItem>
                  <SelectItem value="very_active">
                    Very Active (physical job + exercise)
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Weight Progress */}
          {profile?.current_weight_kg && targetWeightKg && (
            <div className="rounded-lg border bg-muted/50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Progress to Goal</span>
                <span className="text-sm text-muted-foreground">
                  {profile.current_weight_kg}kg → {targetWeightKg}kg
                </span>
              </div>
              <Progress value={Math.min(weightProgress, 100)} className="h-2" />
              <p className="mt-2 text-xs text-muted-foreground">
                {Math.abs(profile.current_weight_kg - parseFloat(targetWeightKg)).toFixed(1)}kg{' '}
                to go
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Calorie & Macro Targets */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Calorie & Macro Targets</CardTitle>
              <CardDescription>
                Set your daily nutritional goals
              </CardDescription>
            </div>
            <Button
              type="button"
              variant="outline"
              onClick={handleCalculateRecommended}
              disabled={!goal || !activityLevel}
            >
              Calculate Recommended
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="target-calories">Daily Calorie Target</Label>
            <Input
              id="target-calories"
              type="number"
              value={targetCalories}
              onChange={(e) => setTargetCalories(e.target.value)}
              placeholder="2000"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="protein">Protein (g/day)</Label>
              <Input
                id="protein"
                type="number"
                value={targetProteinG}
                onChange={(e) => setTargetProteinG(e.target.value)}
                placeholder="150"
              />
              <p className="text-xs text-muted-foreground">
                {targetCalories && targetProteinG
                  ? `${Math.round((parseInt(targetProteinG) * 4 * 100) / parseInt(targetCalories))}% of calories`
                  : ''}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="carbs">Carbs (g/day)</Label>
              <Input
                id="carbs"
                type="number"
                value={targetCarbsG}
                onChange={(e) => setTargetCarbsG(e.target.value)}
                placeholder="200"
              />
              <p className="text-xs text-muted-foreground">
                {targetCalories && targetCarbsG
                  ? `${Math.round((parseInt(targetCarbsG) * 4 * 100) / parseInt(targetCalories))}% of calories`
                  : ''}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="fat">Fat (g/day)</Label>
              <Input
                id="fat"
                type="number"
                value={targetFatG}
                onChange={(e) => setTargetFatG(e.target.value)}
                placeholder="65"
              />
              <p className="text-xs text-muted-foreground">
                {targetCalories && targetFatG
                  ? `${Math.round((parseInt(targetFatG) * 9 * 100) / parseInt(targetCalories))}% of calories`
                  : ''}
              </p>
            </div>
          </div>

          {/* Macro Distribution Visualization */}
          {targetProteinG && targetCarbsG && targetFatG && (
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="mb-2 text-sm font-medium">Macro Distribution</p>
              <div className="flex h-4 overflow-hidden rounded-full">
                <div
                  className="bg-red-500"
                  style={{
                    width: `${
                      (parseInt(targetProteinG) * 4 * 100) /
                      (parseInt(targetProteinG) * 4 +
                        parseInt(targetCarbsG) * 4 +
                        parseInt(targetFatG) * 9)
                    }%`,
                  }}
                />
                <div
                  className="bg-blue-500"
                  style={{
                    width: `${
                      (parseInt(targetCarbsG) * 4 * 100) /
                      (parseInt(targetProteinG) * 4 +
                        parseInt(targetCarbsG) * 4 +
                        parseInt(targetFatG) * 9)
                    }%`,
                  }}
                />
                <div
                  className="bg-yellow-500"
                  style={{
                    width: `${
                      (parseInt(targetFatG) * 9 * 100) /
                      (parseInt(targetProteinG) * 4 +
                        parseInt(targetCarbsG) * 4 +
                        parseInt(targetFatG) * 9)
                    }%`,
                  }}
                />
              </div>
              <div className="mt-2 flex justify-between text-xs">
                <span className="text-red-700">Protein</span>
                <span className="text-blue-700">Carbs</span>
                <span className="text-yellow-700">Fat</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-end">
        <Button type="submit" size="lg" disabled={updateMutation.isPending}>
          {updateMutation.isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Goals
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
