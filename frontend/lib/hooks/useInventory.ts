/**
 * React Query Hooks for Inventory
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getInventoryItems,
  getInventoryStats,
  getInventoryItem,
  createInventoryItem,
  updateInventoryItem,
  deleteInventoryItem,
  getFoodCategories,
  parseVoiceInput,
  parseImageInput,
  bulkCreateInventoryItems,
  InventoryQueryParams,
  CreateInventoryItemRequest,
  UpdateInventoryItemRequest,
} from '../api/inventory';
import { toast } from 'sonner';

// ============================================================================
// Query Keys
// ============================================================================

export const inventoryKeys = {
  all: ['inventory'] as const,
  lists: () => [...inventoryKeys.all, 'list'] as const,
  list: (params?: InventoryQueryParams) =>
    [...inventoryKeys.lists(), params] as const,
  details: () => [...inventoryKeys.all, 'detail'] as const,
  detail: (id: number) => [...inventoryKeys.details(), id] as const,
  stats: () => [...inventoryKeys.all, 'stats'] as const,
  categories: ['food-categories'] as const,
};

// ============================================================================
// Query Hooks
// ============================================================================

/**
 * Fetch inventory items with optional filters
 */
export function useInventoryItems(params?: InventoryQueryParams) {
  return useQuery({
    queryKey: inventoryKeys.list(params),
    queryFn: () => getInventoryItems(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Fetch inventory statistics
 */
export function useInventoryStats() {
  return useQuery({
    queryKey: inventoryKeys.stats(),
    queryFn: getInventoryStats,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Fetch a single inventory item
 */
export function useInventoryItem(id: number) {
  return useQuery({
    queryKey: inventoryKeys.detail(id),
    queryFn: () => getInventoryItem(id),
    enabled: !!id,
  });
}

/**
 * Fetch food categories
 */
export function useFoodCategories() {
  return useQuery({
    queryKey: inventoryKeys.categories,
    queryFn: getFoodCategories,
    staleTime: 1000 * 60 * 30, // 30 minutes (categories rarely change)
  });
}

// ============================================================================
// Mutation Hooks
// ============================================================================

/**
 * Create a new inventory item
 */
export function useCreateInventoryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createInventoryItem,
    onSuccess: () => {
      // Invalidate and refetch inventory queries
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
      toast.success('Item added to inventory');
    },
    onError: (error: Error) => {
      toast.error(`Failed to add item: ${error.message}`);
    },
  });
}

/**
 * Update an existing inventory item
 */
export function useUpdateInventoryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: UpdateInventoryItemRequest;
    }) => updateInventoryItem(id, data),
    onSuccess: (data) => {
      // Update cache for this specific item
      queryClient.setQueryData(inventoryKeys.detail(data.id), data);
      // Invalidate list queries
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
      toast.success('Item updated');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update item: ${error.message}`);
    },
  });
}

/**
 * Delete an inventory item
 */
export function useDeleteInventoryItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteInventoryItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
      toast.success('Item deleted');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete item: ${error.message}`);
    },
  });
}

/**
 * Bulk create inventory items
 */
export function useBulkCreateInventoryItems() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: bulkCreateInventoryItems,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: inventoryKeys.stats() });
      toast.success(`${data.length} items added to inventory`);
    },
    onError: (error: Error) => {
      toast.error(`Failed to add items: ${error.message}`);
    },
  });
}

/**
 * Parse voice input
 */
export function useParseVoiceInput() {
  return useMutation({
    mutationFn: parseVoiceInput,
    onError: (error: Error) => {
      toast.error(`Failed to process voice input: ${error.message}`);
    },
  });
}

/**
 * Parse image input
 */
export function useParseImageInput() {
  return useMutation({
    mutationFn: parseImageInput,
    onError: (error: Error) => {
      toast.error(`Failed to process image: ${error.message}`);
    },
  });
}
