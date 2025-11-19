/**
 * ProfileForm Component
 *
 * User profile information form
 */

'use client';

import { useState, useEffect } from 'react';
import { Loader2, Save } from 'lucide-react';
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
import { AvatarUpload } from './AvatarUpload';
import { useCurrentUser, useUpdateProfile, useUserProfile } from '@/lib/hooks/useUser';
import { calculateBMI } from '@/lib/api/user';

export function ProfileForm() {
  const { data: user } = useCurrentUser();
  const { data: profile } = useUserProfile();
  const updateMutation = useUpdateProfile();

  const [fullName, setFullName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [gender, setGender] = useState<string>('');
  const [heightCm, setHeightCm] = useState('');
  const [currentWeightKg, setCurrentWeightKg] = useState('');

  // Load existing data
  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
    }
  }, [user]);

  useEffect(() => {
    if (profile) {
      setDateOfBirth(profile.date_of_birth || '');
      setGender(profile.gender || '');
      setHeightCm(profile.height_cm?.toString() || '');
      setCurrentWeightKg(profile.current_weight_kg?.toString() || '');
    }
  }, [profile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await updateMutation.mutateAsync({
        full_name: fullName || undefined,
        date_of_birth: dateOfBirth || undefined,
        gender: gender as any,
        height_cm: heightCm ? parseFloat(heightCm) : undefined,
        current_weight_kg: currentWeightKg ? parseFloat(currentWeightKg) : undefined,
      });

      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      alert('Failed to update profile. Please try again.');
    }
  };

  const bmi =
    heightCm && currentWeightKg
      ? calculateBMI(parseFloat(currentWeightKg), parseFloat(heightCm))
      : null;

  const getBMICategory = (bmi: number): string => {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal weight';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Avatar Upload */}
      <Card>
        <CardHeader>
          <CardTitle>Profile Picture</CardTitle>
          <CardDescription>
            Upload a profile picture to personalize your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <AvatarUpload
            currentAvatarUrl={user?.avatar_url}
            userName={user?.full_name}
          />
        </CardContent>
      </Card>

      {/* Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
          <CardDescription>
            Update your personal details
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="full-name">Full Name</Label>
              <Input
                id="full-name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={user?.email || ''}
                disabled
                className="bg-muted"
              />
              <p className="text-xs text-muted-foreground">
                Email cannot be changed
              </p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="date-of-birth">Date of Birth</Label>
              <Input
                id="date-of-birth"
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gender">Gender</Label>
              <Select value={gender} onValueChange={setGender}>
                <SelectTrigger id="gender">
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                  <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Physical Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Physical Stats</CardTitle>
          <CardDescription>
            Track your height and weight for personalized recommendations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="height">Height (cm)</Label>
              <Input
                id="height"
                type="number"
                value={heightCm}
                onChange={(e) => setHeightCm(e.target.value)}
                placeholder="170"
                step="0.1"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="weight">Current Weight (kg)</Label>
              <Input
                id="weight"
                type="number"
                value={currentWeightKg}
                onChange={(e) => setCurrentWeightKg(e.target.value)}
                placeholder="70"
                step="0.1"
              />
            </div>
          </div>

          {/* BMI Display */}
          {bmi && (
            <div className="rounded-lg border bg-muted/50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">Body Mass Index (BMI)</p>
                  <p className="text-xs text-muted-foreground">
                    {getBMICategory(bmi)}
                  </p>
                </div>
                <div className="text-3xl font-bold">{bmi.toFixed(1)}</div>
              </div>
              <div className="mt-3">
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className={`h-full transition-all ${
                      bmi < 18.5
                        ? 'bg-blue-500'
                        : bmi < 25
                          ? 'bg-green-500'
                          : bmi < 30
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min((bmi / 40) * 100, 100)}%` }}
                  />
                </div>
                <div className="mt-1 flex justify-between text-xs text-muted-foreground">
                  <span>18.5</span>
                  <span>25</span>
                  <span>30</span>
                  <span>40+</span>
                </div>
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
              Save Changes
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
