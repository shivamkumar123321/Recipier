/**
 * Meal Plans API Client
 *
 * All API calls related to meal planning
 */

import { apiClient } from './client';

// ============================================================================
// Types
// ============================================================================

export interface MealPlan {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  start_date: string;
  end_date: string;
  total_days: number;
  dietary_preferences: string[];
  goal: 'weight_loss' | 'maintenance' | 'muscle_gain';
  target_calories: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  items?: MealPlanItem[];
}

export interface MealPlanItem {
  id: number;
  meal_plan_id: number;
  day_number: number;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  recipe_id: number;
  recipe?: Recipe;
  servings: number;
  notes?: string;
  created_at: string;
}

export interface Recipe {
  id: number;
  name: string;
  description?: string;
  image_url?: string;
  prep_time: number;
  cook_time: number;
  total_time: number;
  servings: number;
  difficulty: 'easy' | 'medium' | 'hard';
  cuisine?: string;
  calories_per_serving: number;
  protein_per_serving: number;
  carbs_per_serving: number;
  fat_per_serving: number;
  ingredients?: RecipeIngredient[];
  instructions?: RecipeInstruction[];
}

export interface RecipeIngredient {
  id: number;
  recipe_id: number;
  name: string;
  quantity: number;
  unit: string;
  notes?: string;
  order_index: number;
}

export interface RecipeInstruction {
  id: number;
  recipe_id: number;
  step_number: number;
  instruction: string;
  time_minutes?: number;
}

export interface CreateMealPlanRequest {
  name?: string;
  start_date: string;
  end_date?: string;
  total_days: number;
  dietary_preferences: string[];
  goal: 'weight_loss' | 'maintenance' | 'muscle_gain';
  target_calories?: number;
  servings?: number;
  cuisine_preferences?: string[];
  avoid_ingredients?: string[];
  use_inventory?: boolean;
}

export interface MealPlanGenerationProgress {
  status: 'thinking' | 'generating' | 'complete' | 'error';
  progress: number;
  current_step?: string;
  meals_generated?: number;
  total_meals?: number;
  meal_plan?: MealPlan;
  error?: string;
}

export interface GroceryList {
  id: number;
  user_id: number;
  name: string;
  meal_plan_id?: number;
  created_at: string;
  items?: GroceryListItem[];
}

export interface GroceryListItem {
  id: number;
  grocery_list_id: number;
  name: string;
  quantity: number;
  unit: string;
  category?: string;
  is_purchased: boolean;
  notes?: string;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get all meal plans for the current user
 */
export async function getMealPlans(params?: {
  is_active?: boolean;
  skip?: number;
  limit?: number;
}): Promise<MealPlan[]> {
  const response = await apiClient.get<MealPlan[]>('/meal-plans', { params });
  return response.data;
}

/**
 * Get a single meal plan by ID
 */
export async function getMealPlan(id: number): Promise<MealPlan> {
  const response = await apiClient.get<MealPlan>(`/meal-plans/${id}`);
  return response.data;
}

/**
 * Create a new meal plan (initiates generation)
 */
export async function createMealPlan(
  data: CreateMealPlanRequest
): Promise<MealPlan> {
  const response = await apiClient.post<MealPlan>('/meal-plans', data);
  return response.data;
}

/**
 * Update a meal plan
 */
export async function updateMealPlan(
  id: number,
  data: Partial<MealPlan>
): Promise<MealPlan> {
  const response = await apiClient.patch<MealPlan>(`/meal-plans/${id}`, data);
  return response.data;
}

/**
 * Delete a meal plan
 */
export async function deleteMealPlan(id: number): Promise<void> {
  await apiClient.delete(`/meal-plans/${id}`);
}

/**
 * Get meal plan items for a specific plan
 */
export async function getMealPlanItems(
  mealPlanId: number
): Promise<MealPlanItem[]> {
  const response = await apiClient.get<MealPlanItem[]>(
    `/meal-plans/${mealPlanId}/items`
  );
  return response.data;
}

/**
 * Update a meal plan item
 */
export async function updateMealPlanItem(
  id: number,
  data: Partial<MealPlanItem>
): Promise<MealPlanItem> {
  const response = await apiClient.patch<MealPlanItem>(
    `/meal-plan-items/${id}`,
    data
  );
  return response.data;
}

/**
 * Delete a meal plan item
 */
export async function deleteMealPlanItem(id: number): Promise<void> {
  await apiClient.delete(`/meal-plan-items/${id}`);
}

/**
 * Get a recipe by ID
 */
export async function getRecipe(id: number): Promise<Recipe> {
  const response = await apiClient.get<Recipe>(`/recipes/${id}`);
  return response.data;
}

/**
 * Create a grocery list from a meal plan
 */
export async function createGroceryListFromMealPlan(
  mealPlanId: number
): Promise<GroceryList> {
  const response = await apiClient.post<GroceryList>(
    `/grocery-lists/from-meal-plan`,
    { meal_plan_id: mealPlanId }
  );
  return response.data;
}

/**
 * Get WebSocket URL for meal plan generation
 */
export function getMealPlanWebSocketUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const wsUrl = apiUrl.replace(/^http/, 'ws');
  return `${wsUrl}/ws/meal-plan-generation`;
}
