/**
 * User API Client
 *
 * Handles user profile, preferences, and account operations
 */

import { api } from './client';

export interface User {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  id: number;
  user_id: number;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  height_cm?: number;
  current_weight_kg?: number;
  target_weight_kg?: number;
  activity_level?: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
  dietary_preferences?: string[];
  allergies?: string[];
  cuisines_liked?: string[];
  cuisines_disliked?: string[];
  goal?: 'weight_loss' | 'maintenance' | 'muscle_gain';
  target_calories?: number;
  target_protein_g?: number;
  target_carbs_g?: number;
  target_fat_g?: number;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  full_name?: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  height_cm?: number;
  current_weight_kg?: number;
}

export interface UpdateDietaryPreferencesRequest {
  dietary_preferences?: string[];
  allergies?: string[];
  cuisines_liked?: string[];
  cuisines_disliked?: string[];
}

export interface UpdateGoalsRequest {
  goal?: 'weight_loss' | 'maintenance' | 'muscle_gain';
  target_weight_kg?: number;
  activity_level?: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
  target_calories?: number;
  target_protein_g?: number;
  target_carbs_g?: number;
  target_fat_g?: number;
}

export interface NotificationSettings {
  id: number;
  user_id: number;
  email_meal_reminders: boolean;
  email_grocery_lists: boolean;
  email_weekly_summary: boolean;
  email_recipe_suggestions: boolean;
  push_meal_reminders: boolean;
  push_timer_alerts: boolean;
  push_grocery_reminders: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateNotificationSettingsRequest {
  email_meal_reminders?: boolean;
  email_grocery_lists?: boolean;
  email_weekly_summary?: boolean;
  email_recipe_suggestions?: boolean;
  push_meal_reminders?: boolean;
  push_timer_alerts?: boolean;
  push_grocery_reminders?: boolean;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface DeleteAccountRequest {
  password: string;
  confirmation: string; // Must be "DELETE"
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>('/api/v1/users/me');
  return response.data;
}

/**
 * Update user profile
 */
export async function updateProfile(data: UpdateProfileRequest): Promise<User> {
  const response = await api.patch<User>('/api/v1/users/me', data);
  return response.data;
}

/**
 * Upload user avatar
 */
export async function uploadAvatar(file: File): Promise<{ avatar_url: string }> {
  const formData = new FormData();
  formData.append('avatar', file);

  const response = await api.post<{ avatar_url: string }>(
    '/api/v1/users/me/avatar',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}

/**
 * Delete user avatar
 */
export async function deleteAvatar(): Promise<void> {
  await api.delete('/api/v1/users/me/avatar');
}

/**
 * Get user profile details
 */
export async function getUserProfile(): Promise<UserProfile> {
  const response = await api.get<UserProfile>('/api/v1/users/me/profile');
  return response.data;
}

/**
 * Update dietary preferences
 */
export async function updateDietaryPreferences(
  data: UpdateDietaryPreferencesRequest
): Promise<UserProfile> {
  const response = await api.patch<UserProfile>(
    '/api/v1/users/me/dietary-preferences',
    data
  );
  return response.data;
}

/**
 * Update health goals
 */
export async function updateGoals(data: UpdateGoalsRequest): Promise<UserProfile> {
  const response = await api.patch<UserProfile>('/api/v1/users/me/goals', data);
  return response.data;
}

/**
 * Get notification settings
 */
export async function getNotificationSettings(): Promise<NotificationSettings> {
  const response = await api.get<NotificationSettings>(
    '/api/v1/users/me/notification-settings'
  );
  return response.data;
}

/**
 * Update notification settings
 */
export async function updateNotificationSettings(
  data: UpdateNotificationSettingsRequest
): Promise<NotificationSettings> {
  const response = await api.patch<NotificationSettings>(
    '/api/v1/users/me/notification-settings',
    data
  );
  return response.data;
}

/**
 * Change password
 */
export async function changePassword(data: ChangePasswordRequest): Promise<void> {
  await api.post('/api/v1/users/me/change-password', data);
}

/**
 * Delete account
 */
export async function deleteAccount(data: DeleteAccountRequest): Promise<void> {
  await api.post('/api/v1/users/me/delete-account', data);
}

/**
 * Helper: Calculate BMI
 */
export function calculateBMI(weightKg: number, heightCm: number): number {
  const heightM = heightCm / 100;
  return weightKg / (heightM * heightM);
}

/**
 * Helper: Calculate recommended calories
 */
export function calculateRecommendedCalories(
  weightKg: number,
  heightCm: number,
  age: number,
  gender: 'male' | 'female',
  activityLevel: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active',
  goal: 'weight_loss' | 'maintenance' | 'muscle_gain'
): number {
  // Mifflin-St Jeor Equation
  let bmr: number;
  if (gender === 'male') {
    bmr = 10 * weightKg + 6.25 * heightCm - 5 * age + 5;
  } else {
    bmr = 10 * weightKg + 6.25 * heightCm - 5 * age - 161;
  }

  // Activity multiplier
  const activityMultipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    active: 1.725,
    very_active: 1.9,
  };

  let tdee = bmr * activityMultipliers[activityLevel];

  // Goal adjustment
  if (goal === 'weight_loss') {
    tdee -= 500; // 500 calorie deficit
  } else if (goal === 'muscle_gain') {
    tdee += 300; // 300 calorie surplus
  }

  return Math.round(tdee);
}

/**
 * Helper: Calculate recommended macros
 */
export function calculateRecommendedMacros(
  calories: number,
  goal: 'weight_loss' | 'maintenance' | 'muscle_gain'
): { protein_g: number; carbs_g: number; fat_g: number } {
  let proteinPercent: number;
  let fatPercent: number;
  let carbsPercent: number;

  if (goal === 'weight_loss') {
    proteinPercent = 0.35; // 35%
    fatPercent = 0.25; // 25%
    carbsPercent = 0.4; // 40%
  } else if (goal === 'muscle_gain') {
    proteinPercent = 0.3; // 30%
    fatPercent = 0.25; // 25%
    carbsPercent = 0.45; // 45%
  } else {
    // maintenance
    proteinPercent = 0.3; // 30%
    fatPercent = 0.3; // 30%
    carbsPercent = 0.4; // 40%
  }

  return {
    protein_g: Math.round((calories * proteinPercent) / 4),
    carbs_g: Math.round((calories * carbsPercent) / 4),
    fat_g: Math.round((calories * fatPercent) / 9),
  };
}

/**
 * Common dietary preferences
 */
export const DIETARY_PREFERENCES = [
  'Vegetarian',
  'Vegan',
  'Pescatarian',
  'Gluten-Free',
  'Dairy-Free',
  'Keto',
  'Paleo',
  'Low-Carb',
  'Low-Fat',
  'High-Protein',
  'Mediterranean',
  'Whole30',
];

/**
 * Common allergies
 */
export const COMMON_ALLERGIES = [
  'Peanuts',
  'Tree Nuts',
  'Milk',
  'Eggs',
  'Wheat',
  'Soy',
  'Fish',
  'Shellfish',
  'Sesame',
  'Sulfites',
];

/**
 * Common cuisines
 */
export const CUISINES = [
  'Italian',
  'Mexican',
  'Chinese',
  'Japanese',
  'Thai',
  'Indian',
  'French',
  'Mediterranean',
  'American',
  'Korean',
  'Vietnamese',
  'Greek',
  'Spanish',
  'Middle Eastern',
];
