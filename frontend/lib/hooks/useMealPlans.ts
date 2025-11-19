/**
 * React Query Hooks for Meal Plans
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getMealPlans,
  getMealPlan,
  createMealPlan,
  updateMealPlan,
  deleteMealPlan,
  getMealPlanItems,
  updateMealPlanItem,
  deleteMealPlanItem,
  getRecipe,
  createGroceryListFromMealPlan,
  CreateMealPlanRequest,
} from '../api/meal-plans';
import { toast } from 'sonner';

// ============================================================================
// Query Keys
// ============================================================================

export const mealPlanKeys = {
  all: ['meal-plans'] as const,
  lists: () => [...mealPlanKeys.all, 'list'] as const,
  list: (filters?: any) => [...mealPlanKeys.lists(), filters] as const,
  details: () => [...mealPlanKeys.all, 'detail'] as const,
  detail: (id: number) => [...mealPlanKeys.details(), id] as const,
  items: (id: number) => [...mealPlanKeys.detail(id), 'items'] as const,
};

export const recipeKeys = {
  all: ['recipes'] as const,
  detail: (id: number) => [...recipeKeys.all, id] as const,
};

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * Fetch all meal plans
 */
export function useMealPlans(params?: {
  is_active?: boolean;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: mealPlanKeys.list(params),
    queryFn: () => getMealPlans(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Fetch a single meal plan
 */
export function useMealPlan(id: number) {
  return useQuery({
    queryKey: mealPlanKeys.detail(id),
    queryFn: () => getMealPlan(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Fetch meal plan items
 */
export function useMealPlanItems(mealPlanId: number) {
  return useQuery({
    queryKey: mealPlanKeys.items(mealPlanId),
    queryFn: () => getMealPlanItems(mealPlanId),
    enabled: !!mealPlanId,
    staleTime: 1000 * 60 * 5,
  });
}

/**
 * Fetch a recipe
 */
export function useRecipe(id: number) {
  return useQuery({
    queryKey: recipeKeys.detail(id),
    queryFn: () => getRecipe(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

// ============================================================================
// Mutation Hooks
// ============================================================================

/**
 * Create a new meal plan
 */
export function useCreateMealPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createMealPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.lists() });
      toast.success('Meal plan created successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create meal plan: ${error.message}`);
    },
  });
}

/**
 * Update a meal plan
 */
export function useUpdateMealPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<any> }) =>
      updateMealPlan(id, data),
    onSuccess: (data) => {
      queryClient.setQueryData(mealPlanKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.lists() });
      toast.success('Meal plan updated');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update meal plan: ${error.message}`);
    },
  });
}

/**
 * Delete a meal plan
 */
export function useDeleteMealPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteMealPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.lists() });
      toast.success('Meal plan deleted');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete meal plan: ${error.message}`);
    },
  });
}

/**
 * Update a meal plan item
 */
export function useUpdateMealPlanItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<any> }) =>
      updateMealPlanItem(id, data),
    onSuccess: (_, variables) => {
      // Invalidate the meal plan items query
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.all });
      toast.success('Meal updated');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update meal: ${error.message}`);
    },
  });
}

/**
 * Delete a meal plan item
 */
export function useDeleteMealPlanItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteMealPlanItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: mealPlanKeys.all });
      toast.success('Meal removed');
    },
    onError: (error: Error) => {
      toast.error(`Failed to remove meal: ${error.message}`);
    },
  });
}

/**
 * Create grocery list from meal plan
 */
export function useCreateGroceryList() {
  return useMutation({
    mutationFn: createGroceryListFromMealPlan,
    onSuccess: () => {
      toast.success('Grocery list created successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create grocery list: ${error.message}`);
    },
  });
}
