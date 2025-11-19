/**
 * DietaryPreferencesForm Component
 *
 * Manage dietary preferences, allergies, and cuisine preferences
 */

'use client';

import { useState, useEffect } from 'react';
import { Loader2, Save, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { useUserProfile, useUpdateDietaryPreferences } from '@/lib/hooks/useUser';
import { DIETARY_PREFERENCES, COMMON_ALLERGIES, CUISINES } from '@/lib/api/user';
import { cn } from '@/lib/utils';

export function DietaryPreferencesForm() {
  const { data: profile } = useUserProfile();
  const updateMutation = useUpdateDietaryPreferences();

  const [selectedPreferences, setSelectedPreferences] = useState<string[]>([]);
  const [selectedAllergies, setSelectedAllergies] = useState<string[]>([]);
  const [customAllergy, setCustomAllergy] = useState('');
  const [likedCuisines, setLikedCuisines] = useState<string[]>([]);
  const [dislikedCuisines, setDislikedCuisines] = useState<string[]>([]);

  // Load existing data
  useEffect(() => {
    if (profile) {
      setSelectedPreferences(profile.dietary_preferences || []);
      setSelectedAllergies(profile.allergies || []);
      setLikedCuisines(profile.cuisines_liked || []);
      setDislikedCuisines(profile.cuisines_disliked || []);
    }
  }, [profile]);

  const togglePreference = (pref: string) => {
    setSelectedPreferences((prev) =>
      prev.includes(pref)
        ? prev.filter((p) => p !== pref)
        : [...prev, pref]
    );
  };

  const toggleAllergy = (allergy: string) => {
    setSelectedAllergies((prev) =>
      prev.includes(allergy)
        ? prev.filter((a) => a !== allergy)
        : [...prev, allergy]
    );
  };

  const addCustomAllergy = () => {
    if (customAllergy.trim() && !selectedAllergies.includes(customAllergy.trim())) {
      setSelectedAllergies((prev) => [...prev, customAllergy.trim()]);
      setCustomAllergy('');
    }
  };

  const removeAllergy = (allergy: string) => {
    setSelectedAllergies((prev) => prev.filter((a) => a !== allergy));
  };

  const toggleCuisineLike = (cuisine: string) => {
    // Remove from disliked if present
    setDislikedCuisines((prev) => prev.filter((c) => c !== cuisine));

    // Toggle in liked
    setLikedCuisines((prev) =>
      prev.includes(cuisine)
        ? prev.filter((c) => c !== cuisine)
        : [...prev, cuisine]
    );
  };

  const toggleCuisineDislike = (cuisine: string) => {
    // Remove from liked if present
    setLikedCuisines((prev) => prev.filter((c) => c !== cuisine));

    // Toggle in disliked
    setDislikedCuisines((prev) =>
      prev.includes(cuisine)
        ? prev.filter((c) => c !== cuisine)
        : [...prev, cuisine]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await updateMutation.mutateAsync({
        dietary_preferences: selectedPreferences,
        allergies: selectedAllergies,
        cuisines_liked: likedCuisines,
        cuisines_disliked: dislikedCuisines,
      });

      alert('Dietary preferences updated successfully!');
    } catch (error) {
      console.error('Failed to update preferences:', error);
      alert('Failed to update preferences. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Dietary Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Dietary Preferences</CardTitle>
          <CardDescription>
            Select your dietary lifestyle and restrictions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {DIETARY_PREFERENCES.map((pref) => (
              <div key={pref} className="flex items-center space-x-2">
                <Checkbox
                  id={`pref-${pref}`}
                  checked={selectedPreferences.includes(pref)}
                  onCheckedChange={() => togglePreference(pref)}
                />
                <label
                  htmlFor={`pref-${pref}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {pref}
                </label>
              </div>
            ))}
          </div>

          {selectedPreferences.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="text-sm text-muted-foreground">Selected:</span>
              {selectedPreferences.map((pref) => (
                <Badge key={pref} variant="secondary">
                  {pref}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Allergies */}
      <Card>
        <CardHeader>
          <CardTitle>Allergies & Intolerances</CardTitle>
          <CardDescription>
            Tell us about your food allergies to avoid them in recipes
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {COMMON_ALLERGIES.map((allergy) => (
              <div key={allergy} className="flex items-center space-x-2">
                <Checkbox
                  id={`allergy-${allergy}`}
                  checked={selectedAllergies.includes(allergy)}
                  onCheckedChange={() => toggleAllergy(allergy)}
                />
                <label
                  htmlFor={`allergy-${allergy}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {allergy}
                </label>
              </div>
            ))}
          </div>

          {/* Custom Allergy Input */}
          <div className="space-y-2">
            <Label>Add Custom Allergy</Label>
            <div className="flex gap-2">
              <Input
                placeholder="e.g., Mustard, Celery"
                value={customAllergy}
                onChange={(e) => setCustomAllergy(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addCustomAllergy();
                  }
                }}
              />
              <Button type="button" onClick={addCustomAllergy} variant="outline">
                Add
              </Button>
            </div>
          </div>

          {/* Selected Allergies */}
          {selectedAllergies.length > 0 && (
            <div className="space-y-2">
              <Label>Your Allergies:</Label>
              <div className="flex flex-wrap gap-2">
                {selectedAllergies.map((allergy) => (
                  <Badge
                    key={allergy}
                    variant="destructive"
                    className="gap-1"
                  >
                    {allergy}
                    <button
                      type="button"
                      onClick={() => removeAllergy(allergy)}
                      className="ml-1 hover:text-destructive-foreground"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cuisine Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Cuisine Preferences</CardTitle>
          <CardDescription>
            Tell us which cuisines you love and which you'd prefer to avoid
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            {CUISINES.map((cuisine) => {
              const isLiked = likedCuisines.includes(cuisine);
              const isDisliked = dislikedCuisines.includes(cuisine);

              return (
                <div
                  key={cuisine}
                  className={cn(
                    'flex items-center justify-between rounded-lg border p-3 transition-colors',
                    isLiked && 'border-green-500 bg-green-50',
                    isDisliked && 'border-red-500 bg-red-50'
                  )}
                >
                  <span className="font-medium">{cuisine}</span>
                  <div className="flex gap-1">
                    <Button
                      type="button"
                      size="sm"
                      variant={isLiked ? 'default' : 'outline'}
                      className={cn(
                        'h-8 w-16',
                        isLiked && 'bg-green-600 hover:bg-green-700'
                      )}
                      onClick={() => toggleCuisineLike(cuisine)}
                    >
                      {isLiked ? '✓ Like' : 'Like'}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant={isDisliked ? 'destructive' : 'outline'}
                      className="h-8 w-20"
                      onClick={() => toggleCuisineDislike(cuisine)}
                    >
                      {isDisliked ? '✓ Avoid' : 'Avoid'}
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
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
              Save Preferences
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
