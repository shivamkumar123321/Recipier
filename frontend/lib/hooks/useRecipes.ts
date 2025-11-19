/**
 * React Query Hooks for Recipes
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  searchRecipes,
  getRecipe,
  createRecipe,
  updateRecipe,
  deleteRecipe,
  getSavedRecipes,
  getCustomRecipes,
  saveRecipe,
  unsaveRecipe,
  rateRecipe,
  getRecipeRecommendations,
  getPopularRecipes,
  getRecentRecipes,
  matchRecipeWithInventory,
  RecipeSearchParams,
  CreateRecipeRequest,
} from '../api/recipes';
import { toast } from 'sonner';

// ============================================================================
// Query Keys
// ============================================================================

export const recipeKeys = {
  all: ['recipes'] as const,
  lists: () => [...recipeKeys.all, 'list'] as const,
  list: (params?: RecipeSearchParams) => [...recipeKeys.lists(), params] as const,
  details: () => [...recipeKeys.all, 'detail'] as const,
  detail: (id: number) => [...recipeKeys.details(), id] as const,
  saved: () => [...recipeKeys.all, 'saved'] as const,
  custom: () => [...recipeKeys.all, 'custom'] as const,
  recommendations: () => [...recipeKeys.all, 'recommendations'] as const,
  popular: () => [...recipeKeys.all, 'popular'] as const,
  recent: () => [...recipeKeys.all, 'recent'] as const,
  inventoryMatch: (id: number) => [...recipeKeys.detail(id), 'match'] as const,
};

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * Search recipes with filters
 */
export function useRecipes(params?: RecipeSearchParams) {
  return useQuery({
    queryKey: recipeKeys.list(params),
    queryFn: () => searchRecipes(params),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * Fetch a single recipe
 */
export function useRecipe(id: number) {
  return useQuery({
    queryKey: recipeKeys.detail(id),
    queryFn: () => getRecipe(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 10,
  });
}

/**
 * Fetch saved recipes
 */
export function useSavedRecipes(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: recipeKeys.saved(),
    queryFn: () => getSavedRecipes(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Fetch custom recipes
 */
export function useCustomRecipes(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: recipeKeys.custom(),
    queryFn: () => getCustomRecipes(params),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Fetch recipe recommendations
 */
export function useRecipeRecommendations(params?: {
  use_inventory?: boolean;
  limit?: number;
}) {
  return useQuery({
    queryKey: recipeKeys.recommendations(),
    queryFn: () => getRecipeRecommendations(params),
    staleTime: 1000 * 60 * 15,
  });
}

/**
 * Fetch popular recipes
 */
export function usePopularRecipes(limit: number = 10) {
  return useQuery({
    queryKey: recipeKeys.popular(),
    queryFn: () => getPopularRecipes(limit),
    staleTime: 1000 * 60 * 30,
  });
}

/**
 * Fetch recently viewed recipes
 */
export function useRecentRecipes(limit: number = 10) {
  return useQuery({
    queryKey: recipeKeys.recent(),
    queryFn: () => getRecentRecipes(limit),
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Match recipe with inventory
 */
export function useRecipeInventoryMatch(recipeId: number) {
  return useQuery({
    queryKey: recipeKeys.inventoryMatch(recipeId),
    queryFn: () => matchRecipeWithInventory(recipeId),
    enabled: !!recipeId,
    staleTime: 1000 * 60 * 5,
  });
}

// ============================================================================
// Mutation Hooks
// ============================================================================

/**
 * Create a new recipe
 */
export function useCreateRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createRecipe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
      queryClient.invalidateQueries({ queryKey: recipeKeys.custom() });
      toast.success('Recipe created successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create recipe: ${error.message}`);
    },
  });
}

/**
 * Update a recipe
 */
export function useUpdateRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<CreateRecipeRequest> }) =>
      updateRecipe(id, data),
    onSuccess: (data) => {
      queryClient.setQueryData(recipeKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
      toast.success('Recipe updated');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update recipe: ${error.message}`);
    },
  });
}

/**
 * Delete a recipe
 */
export function useDeleteRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteRecipe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
      queryClient.invalidateQueries({ queryKey: recipeKeys.custom() });
      toast.success('Recipe deleted');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete recipe: ${error.message}`);
    },
  });
}

/**
 * Save/favorite a recipe
 */
export function useSaveRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: saveRecipe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.saved() });
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
      toast.success('Recipe saved to favorites');
    },
    onError: (error: Error) => {
      toast.error(`Failed to save recipe: ${error.message}`);
    },
  });
}

/**
 * Unsave/unfavorite a recipe
 */
export function useUnsaveRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: unsaveRecipe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.saved() });
      queryClient.invalidateQueries({ queryKey: recipeKeys.lists() });
      toast.success('Recipe removed from favorites');
    },
    onError: (error: Error) => {
      toast.error(`Failed to remove recipe: ${error.message}`);
    },
  });
}

/**
 * Rate a recipe
 */
export function useRateRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, rating }: { id: number; rating: number }) =>
      rateRecipe(id, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: recipeKeys.saved() });
      toast.success('Rating saved');
    },
    onError: (error: Error) => {
      toast.error(`Failed to rate recipe: ${error.message}`);
    },
  });
}
