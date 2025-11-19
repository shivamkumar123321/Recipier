/**
 * Recipes API Client
 *
 * All API calls related to recipes and user recipes
 */

import { apiClient } from './client';

// ============================================================================
// Types
// ============================================================================

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
  dietary_tags?: string[];
  calories_per_serving: number;
  protein_per_serving: number;
  carbs_per_serving: number;
  fat_per_serving: number;
  fiber_per_serving?: number;
  sodium_per_serving?: number;
  is_public: boolean;
  created_by?: number;
  created_at: string;
  updated_at: string;
  ingredients?: RecipeIngredient[];
  instructions?: RecipeInstruction[];
  is_favorited?: boolean;
}

export interface RecipeIngredient {
  id: number;
  recipe_id: number;
  name: string;
  quantity: number;
  unit: string;
  notes?: string;
  order_index: number;
  in_inventory?: boolean; // Client-side flag for inventory matching
}

export interface RecipeInstruction {
  id: number;
  recipe_id: number;
  step_number: number;
  instruction: string;
  time_minutes?: number;
  image_url?: string;
}

export interface UserRecipe {
  id: number;
  user_id: number;
  recipe_id: number;
  type: 'saved' | 'custom';
  notes?: string;
  rating?: number;
  last_cooked?: string;
  cook_count: number;
  created_at: string;
  recipe?: Recipe;
}

export interface RecipeSearchParams {
  search?: string;
  cuisine?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  max_cook_time?: number;
  min_protein?: number;
  max_calories?: number;
  dietary_tags?: string[];
  ingredients?: string[];
  skip?: number;
  limit?: number;
  sort_by?: 'name' | 'cook_time' | 'calories' | 'created_at';
  sort_order?: 'asc' | 'desc';
}

export interface CreateRecipeRequest {
  name: string;
  description?: string;
  image_url?: string;
  prep_time: number;
  cook_time: number;
  servings: number;
  difficulty: 'easy' | 'medium' | 'hard';
  cuisine?: string;
  dietary_tags?: string[];
  calories_per_serving: number;
  protein_per_serving: number;
  carbs_per_serving: number;
  fat_per_serving: number;
  ingredients: Array<{
    name: string;
    quantity: number;
    unit: string;
    notes?: string;
    order_index: number;
  }>;
  instructions: Array<{
    step_number: number;
    instruction: string;
    time_minutes?: number;
  }>;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Search recipes with filters
 */
export async function searchRecipes(
  params?: RecipeSearchParams
): Promise<Recipe[]> {
  const response = await apiClient.get<Recipe[]>('/recipes', { params });
  return response.data;
}

/**
 * Get a single recipe by ID
 */
export async function getRecipe(id: number): Promise<Recipe> {
  const response = await apiClient.get<Recipe>(`/recipes/${id}`);
  return response.data;
}

/**
 * Create a new recipe
 */
export async function createRecipe(
  data: CreateRecipeRequest
): Promise<Recipe> {
  const response = await apiClient.post<Recipe>('/recipes', data);
  return response.data;
}

/**
 * Update an existing recipe
 */
export async function updateRecipe(
  id: number,
  data: Partial<CreateRecipeRequest>
): Promise<Recipe> {
  const response = await apiClient.patch<Recipe>(`/recipes/${id}`, data);
  return response.data;
}

/**
 * Delete a recipe
 */
export async function deleteRecipe(id: number): Promise<void> {
  await apiClient.delete(`/recipes/${id}`);
}

/**
 * Get user's saved recipes
 */
export async function getSavedRecipes(params?: {
  skip?: number;
  limit?: number;
}): Promise<UserRecipe[]> {
  const response = await apiClient.get<UserRecipe[]>('/user-recipes', {
    params: { ...params, type: 'saved' },
  });
  return response.data;
}

/**
 * Get user's custom recipes
 */
export async function getCustomRecipes(params?: {
  skip?: number;
  limit?: number;
}): Promise<UserRecipe[]> {
  const response = await apiClient.get<UserRecipe[]>('/user-recipes', {
    params: { ...params, type: 'custom' },
  });
  return response.data;
}

/**
 * Save/favorite a recipe
 */
export async function saveRecipe(recipeId: number): Promise<UserRecipe> {
  const response = await apiClient.post<UserRecipe>('/user-recipes', {
    recipe_id: recipeId,
    type: 'saved',
  });
  return response.data;
}

/**
 * Unsave/unfavorite a recipe
 */
export async function unsaveRecipe(userRecipeId: number): Promise<void> {
  await apiClient.delete(`/user-recipes/${userRecipeId}`);
}

/**
 * Rate a recipe
 */
export async function rateRecipe(
  userRecipeId: number,
  rating: number
): Promise<UserRecipe> {
  const response = await apiClient.patch<UserRecipe>(
    `/user-recipes/${userRecipeId}`,
    { rating }
  );
  return response.data;
}

/**
 * Get recipe recommendations based on inventory
 */
export async function getRecipeRecommendations(params?: {
  use_inventory?: boolean;
  limit?: number;
}): Promise<Recipe[]> {
  const response = await apiClient.get<Recipe[]>('/recipes/recommendations', {
    params,
  });
  return response.data;
}

/**
 * Get popular recipes
 */
export async function getPopularRecipes(limit: number = 10): Promise<Recipe[]> {
  const response = await apiClient.get<Recipe[]>('/recipes/popular', {
    params: { limit },
  });
  return response.data;
}

/**
 * Get recently viewed recipes
 */
export async function getRecentRecipes(limit: number = 10): Promise<Recipe[]> {
  const response = await apiClient.get<Recipe[]>('/recipes/recent', {
    params: { limit },
  });
  return response.data;
}

/**
 * Match recipe ingredients with inventory
 */
export async function matchRecipeWithInventory(
  recipeId: number
): Promise<{
  matched_ingredients: string[];
  missing_ingredients: string[];
  match_percentage: number;
}> {
  const response = await apiClient.get(
    `/recipes/${recipeId}/inventory-match`
  );
  return response.data;
}
