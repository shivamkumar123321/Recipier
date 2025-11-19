/**
 * Inventory API Client
 *
 * All API calls related to inventory management
 */

import { apiClient } from './client';

// ============================================================================
// Types
// ============================================================================

export interface InventoryItem {
  id: number;
  user_id: number;
  name: string;
  quantity: number;
  unit: string;
  category_id: number;
  category?: FoodCategory;
  expiration_date?: string;
  purchase_date?: string;
  location?: string;
  notes?: string;
  barcode?: string;
  image_url?: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface FoodCategory {
  id: number;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
}

export interface InventoryStats {
  total_items: number;
  expiring_soon: number;
  expired: number;
  low_stock: number;
  categories_count: number;
}

export interface CreateInventoryItemRequest {
  name: string;
  quantity: number;
  unit: string;
  category_id: number;
  expiration_date?: string;
  purchase_date?: string;
  location?: string;
  notes?: string;
  barcode?: string;
  image_url?: string;
}

export interface UpdateInventoryItemRequest {
  name?: string;
  quantity?: number;
  unit?: string;
  category_id?: number;
  expiration_date?: string;
  purchase_date?: string;
  location?: string;
  notes?: string;
  barcode?: string;
  image_url?: string;
}

export interface InventoryQueryParams {
  category_id?: number;
  search?: string;
  sort_by?: 'name' | 'expiration_date' | 'quantity' | 'created_at';
  sort_order?: 'asc' | 'desc';
  expiring_soon?: boolean;
  expired?: boolean;
  low_stock?: boolean;
  skip?: number;
  limit?: number;
}

export interface ParsedInventoryItem {
  name: string;
  quantity: number;
  unit: string;
  category?: string;
  expiration_date?: string;
  confidence?: number;
}

export interface VoiceParseResponse {
  transcription: string;
  items: ParsedInventoryItem[];
}

export interface ImageParseResponse {
  items: ParsedInventoryItem[];
  image_url?: string;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get all inventory items with optional filters
 */
export async function getInventoryItems(
  params?: InventoryQueryParams
): Promise<InventoryItem[]> {
  const response = await apiClient.get<InventoryItem[]>('/inventory', {
    params,
  });
  return response.data;
}

/**
 * Get inventory statistics
 */
export async function getInventoryStats(): Promise<InventoryStats> {
  const response = await apiClient.get<InventoryStats>('/inventory/stats');
  return response.data;
}

/**
 * Get a single inventory item by ID
 */
export async function getInventoryItem(id: number): Promise<InventoryItem> {
  const response = await apiClient.get<InventoryItem>(`/inventory/${id}`);
  return response.data;
}

/**
 * Create a new inventory item
 */
export async function createInventoryItem(
  data: CreateInventoryItemRequest
): Promise<InventoryItem> {
  const response = await apiClient.post<InventoryItem>('/inventory', data);
  return response.data;
}

/**
 * Update an existing inventory item
 */
export async function updateInventoryItem(
  id: number,
  data: UpdateInventoryItemRequest
): Promise<InventoryItem> {
  const response = await apiClient.patch<InventoryItem>(
    `/inventory/${id}`,
    data
  );
  return response.data;
}

/**
 * Delete an inventory item (soft delete)
 */
export async function deleteInventoryItem(id: number): Promise<void> {
  await apiClient.delete(`/inventory/${id}`);
}

/**
 * Get all food categories
 */
export async function getFoodCategories(): Promise<FoodCategory[]> {
  const response = await apiClient.get<FoodCategory[]>('/food-categories');
  return response.data;
}

/**
 * Parse voice input to extract inventory items
 */
export async function parseVoiceInput(
  audioBlob: Blob
): Promise<VoiceParseResponse> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  const response = await apiClient.post<VoiceParseResponse>(
    '/inventory/parse-voice',
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
 * Parse image to identify food items
 */
export async function parseImageInput(
  imageFile: File
): Promise<ImageParseResponse> {
  const formData = new FormData();
  formData.append('image', imageFile);

  const response = await apiClient.post<ImageParseResponse>(
    '/inventory/parse-image',
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
 * Bulk create inventory items
 */
export async function bulkCreateInventoryItems(
  items: CreateInventoryItemRequest[]
): Promise<InventoryItem[]> {
  const response = await apiClient.post<InventoryItem[]>(
    '/inventory/bulk',
    { items }
  );
  return response.data;
}
