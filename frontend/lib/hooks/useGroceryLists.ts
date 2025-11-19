/**
 * Grocery Lists Hooks
 *
 * React Query hooks for grocery list operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getGroceryLists,
  getGroceryList,
  createGroceryList,
  updateGroceryList,
  deleteGroceryList,
  generateGroceryListFromMealPlan,
  addGroceryItem,
  updateGroceryItem,
  deleteGroceryItem,
  toggleItemPurchased,
  addPurchasedItemsToInventory,
  shareGroceryList,
  CreateGroceryListRequest,
  UpdateGroceryListRequest,
  CreateGroceryItemRequest,
  UpdateGroceryItemRequest,
  GenerateFromMealPlanRequest,
} from '../api/grocery-lists';

/**
 * Query keys for grocery lists
 */
export const groceryListKeys = {
  all: ['grocery-lists'] as const,
  lists: () => [...groceryListKeys.all, 'list'] as const,
  list: (params?: any) => [...groceryListKeys.lists(), params] as const,
  details: () => [...groceryListKeys.all, 'detail'] as const,
  detail: (id: number) => [...groceryListKeys.details(), id] as const,
};

/**
 * Fetch all grocery lists
 */
export function useGroceryLists(params?: {
  is_active?: boolean;
  is_completed?: boolean;
}) {
  return useQuery({
    queryKey: groceryListKeys.list(params),
    queryFn: () => getGroceryLists(params),
  });
}

/**
 * Fetch single grocery list by ID
 */
export function useGroceryList(id: number) {
  return useQuery({
    queryKey: groceryListKeys.detail(id),
    queryFn: () => getGroceryList(id),
    enabled: !!id,
  });
}

/**
 * Create new grocery list
 */
export function useCreateGroceryList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateGroceryListRequest) => createGroceryList(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: groceryListKeys.lists() });
    },
  });
}

/**
 * Update grocery list
 */
export function useUpdateGroceryList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateGroceryListRequest }) =>
      updateGroceryList(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: groceryListKeys.detail(variables.id),
      });
      queryClient.invalidateQueries({ queryKey: groceryListKeys.lists() });
    },
  });
}

/**
 * Delete grocery list
 */
export function useDeleteGroceryList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteGroceryList(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: groceryListKeys.lists() });
    },
  });
}

/**
 * Generate grocery list from meal plan
 */
export function useGenerateGroceryList() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: GenerateFromMealPlanRequest) =>
      generateGroceryListFromMealPlan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: groceryListKeys.lists() });
    },
  });
}

/**
 * Add item to grocery list
 */
export function useAddGroceryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ listId, data }: { listId: number; data: CreateGroceryItemRequest }) =>
      addGroceryItem(listId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: groceryListKeys.detail(variables.listId),
      });
    },
  });
}

/**
 * Update grocery item
 */
export function useUpdateGroceryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      listId,
      itemId,
      data,
    }: {
      listId: number;
      itemId: number;
      data: UpdateGroceryItemRequest;
    }) => updateGroceryItem(listId, itemId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: groceryListKeys.detail(variables.listId),
      });
    },
  });
}

/**
 * Delete grocery item
 */
export function useDeleteGroceryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ listId, itemId }: { listId: number; itemId: number }) =>
      deleteGroceryItem(listId, itemId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: groceryListKeys.detail(variables.listId),
      });
    },
  });
}

/**
 * Toggle item purchased status
 */
export function useToggleItemPurchased() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ listId, itemId }: { listId: number; itemId: number }) =>
      toggleItemPurchased(listId, itemId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: groceryListKeys.detail(variables.listId),
      });
    },
  });
}

/**
 * Add purchased items to inventory
 */
export function useAddToInventory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (listId: number) => addPurchasedItemsToInventory(listId),
    onSuccess: (_, listId) => {
      queryClient.invalidateQueries({
        queryKey: groceryListKeys.detail(listId),
      });
      // Also invalidate inventory queries
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });
}

/**
 * Share grocery list
 */
export function useShareGroceryList() {
  return useMutation({
    mutationFn: (id: number) => shareGroceryList(id),
  });
}
