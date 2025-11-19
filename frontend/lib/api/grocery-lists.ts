/**
 * Grocery Lists API Client
 *
 * Handles grocery list and item operations
 */

import { api } from './client';

export interface GroceryList {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  meal_plan_id?: number;
  is_active: boolean;
  is_completed: boolean;
  total_items: number;
  purchased_items: number;
  created_at: string;
  updated_at: string;
  items?: GroceryListItem[];
  meal_plan?: {
    id: number;
    name: string;
  };
}

export interface GroceryListItem {
  id: number;
  grocery_list_id: number;
  name: string;
  quantity: number;
  unit: string;
  category: FoodCategory;
  is_purchased: boolean;
  notes?: string;
  recipe_id?: number;
  order_index: number;
  created_at: string;
  updated_at: string;
}

export type FoodCategory =
  | 'produce'
  | 'dairy'
  | 'meat'
  | 'seafood'
  | 'bakery'
  | 'pantry'
  | 'frozen'
  | 'beverages'
  | 'snacks'
  | 'condiments'
  | 'spices'
  | 'other';

export interface CreateGroceryListRequest {
  name: string;
  description?: string;
  meal_plan_id?: number;
}

export interface UpdateGroceryListRequest {
  name?: string;
  description?: string;
  is_active?: boolean;
  is_completed?: boolean;
}

export interface CreateGroceryItemRequest {
  name: string;
  quantity: number;
  unit: string;
  category?: FoodCategory;
  notes?: string;
  recipe_id?: number;
}

export interface UpdateGroceryItemRequest {
  name?: string;
  quantity?: number;
  unit?: string;
  category?: FoodCategory;
  is_purchased?: boolean;
  notes?: string;
  order_index?: number;
}

export interface GenerateFromMealPlanRequest {
  meal_plan_id: number;
  name?: string;
  exclude_inventory?: boolean; // Exclude items already in inventory
}

/**
 * Get all grocery lists for current user
 */
export async function getGroceryLists(params?: {
  is_active?: boolean;
  is_completed?: boolean;
}): Promise<GroceryList[]> {
  const response = await api.get<GroceryList[]>('/api/v1/grocery-lists', {
    params,
  });
  return response.data;
}

/**
 * Get grocery list by ID
 */
export async function getGroceryList(id: number): Promise<GroceryList> {
  const response = await api.get<GroceryList>(`/api/v1/grocery-lists/${id}`);
  return response.data;
}

/**
 * Create new grocery list
 */
export async function createGroceryList(
  data: CreateGroceryListRequest
): Promise<GroceryList> {
  const response = await api.post<GroceryList>('/api/v1/grocery-lists', data);
  return response.data;
}

/**
 * Update grocery list
 */
export async function updateGroceryList(
  id: number,
  data: UpdateGroceryListRequest
): Promise<GroceryList> {
  const response = await api.patch<GroceryList>(
    `/api/v1/grocery-lists/${id}`,
    data
  );
  return response.data;
}

/**
 * Delete grocery list
 */
export async function deleteGroceryList(id: number): Promise<void> {
  await api.delete(`/api/v1/grocery-lists/${id}`);
}

/**
 * Generate grocery list from meal plan
 */
export async function generateGroceryListFromMealPlan(
  data: GenerateFromMealPlanRequest
): Promise<GroceryList> {
  const response = await api.post<GroceryList>(
    '/api/v1/grocery-lists/generate-from-meal-plan',
    data
  );
  return response.data;
}

/**
 * Add item to grocery list
 */
export async function addGroceryItem(
  listId: number,
  data: CreateGroceryItemRequest
): Promise<GroceryListItem> {
  const response = await api.post<GroceryListItem>(
    `/api/v1/grocery-lists/${listId}/items`,
    data
  );
  return response.data;
}

/**
 * Update grocery item
 */
export async function updateGroceryItem(
  listId: number,
  itemId: number,
  data: UpdateGroceryItemRequest
): Promise<GroceryListItem> {
  const response = await api.patch<GroceryListItem>(
    `/api/v1/grocery-lists/${listId}/items/${itemId}`,
    data
  );
  return response.data;
}

/**
 * Delete grocery item
 */
export async function deleteGroceryItem(
  listId: number,
  itemId: number
): Promise<void> {
  await api.delete(`/api/v1/grocery-lists/${listId}/items/${itemId}`);
}

/**
 * Toggle item purchased status
 */
export async function toggleItemPurchased(
  listId: number,
  itemId: number
): Promise<GroceryListItem> {
  const response = await api.patch<GroceryListItem>(
    `/api/v1/grocery-lists/${listId}/items/${itemId}/toggle-purchased`
  );
  return response.data;
}

/**
 * Add all purchased items to inventory
 */
export async function addPurchasedItemsToInventory(
  listId: number
): Promise<{ items_added: number }> {
  const response = await api.post<{ items_added: number }>(
    `/api/v1/grocery-lists/${listId}/add-to-inventory`
  );
  return response.data;
}

/**
 * Share grocery list (get shareable link)
 */
export async function shareGroceryList(id: number): Promise<{ share_url: string }> {
  const response = await api.post<{ share_url: string }>(
    `/api/v1/grocery-lists/${id}/share`
  );
  return response.data;
}

/**
 * Auto-categorize a grocery item by name
 */
export function categorizeFoodItem(itemName: string): FoodCategory {
  const name = itemName.toLowerCase();

  // Produce
  if (
    /\b(apple|banana|orange|lettuce|tomato|onion|garlic|potato|carrot|broccoli|spinach|pepper|cucumber|avocado|berry|fruit|vegetable)\b/.test(
      name
    )
  ) {
    return 'produce';
  }

  // Dairy
  if (/\b(milk|cheese|yogurt|butter|cream|egg)\b/.test(name)) {
    return 'dairy';
  }

  // Meat
  if (/\b(chicken|beef|pork|turkey|lamb|bacon|sausage|ham)\b/.test(name)) {
    return 'meat';
  }

  // Seafood
  if (/\b(fish|salmon|tuna|shrimp|crab|lobster|seafood)\b/.test(name)) {
    return 'seafood';
  }

  // Bakery
  if (/\b(bread|bagel|muffin|croissant|roll|bun|tortilla)\b/.test(name)) {
    return 'bakery';
  }

  // Frozen
  if (/\b(frozen|ice cream)\b/.test(name)) {
    return 'frozen';
  }

  // Beverages
  if (/\b(juice|soda|water|coffee|tea|drink|beverage)\b/.test(name)) {
    return 'beverages';
  }

  // Condiments
  if (
    /\b(ketchup|mustard|mayo|sauce|dressing|vinegar|oil|marinade)\b/.test(name)
  ) {
    return 'condiments';
  }

  // Spices
  if (
    /\b(salt|pepper|spice|herb|oregano|basil|thyme|cumin|paprika|cinnamon)\b/.test(
      name
    )
  ) {
    return 'spices';
  }

  // Snacks
  if (/\b(chips|crackers|cookies|candy|snack|nuts)\b/.test(name)) {
    return 'snacks';
  }

  // Pantry (default for common pantry items)
  if (
    /\b(flour|sugar|rice|pasta|beans|cereal|oats|quinoa|canned|can)\b/.test(
      name
    )
  ) {
    return 'pantry';
  }

  return 'other';
}

/**
 * Get category display name
 */
export function getCategoryLabel(category: FoodCategory): string {
  const labels: Record<FoodCategory, string> = {
    produce: 'Produce',
    dairy: 'Dairy & Eggs',
    meat: 'Meat & Poultry',
    seafood: 'Seafood',
    bakery: 'Bakery',
    pantry: 'Pantry',
    frozen: 'Frozen',
    beverages: 'Beverages',
    snacks: 'Snacks',
    condiments: 'Condiments & Sauces',
    spices: 'Spices & Herbs',
    other: 'Other',
  };
  return labels[category];
}

/**
 * Get category icon
 */
export function getCategoryIcon(category: FoodCategory): string {
  const icons: Record<FoodCategory, string> = {
    produce: '🥬',
    dairy: '🥛',
    meat: '🥩',
    seafood: '🐟',
    bakery: '🍞',
    pantry: '🥫',
    frozen: '🧊',
    beverages: '🥤',
    snacks: '🍿',
    condiments: '🧂',
    spices: '🌿',
    other: '📦',
  };
  return icons[category];
}

/**
 * Get category color
 */
export function getCategoryColor(category: FoodCategory): string {
  const colors: Record<FoodCategory, string> = {
    produce: 'bg-green-100 text-green-800 border-green-200',
    dairy: 'bg-blue-100 text-blue-800 border-blue-200',
    meat: 'bg-red-100 text-red-800 border-red-200',
    seafood: 'bg-cyan-100 text-cyan-800 border-cyan-200',
    bakery: 'bg-amber-100 text-amber-800 border-amber-200',
    pantry: 'bg-orange-100 text-orange-800 border-orange-200',
    frozen: 'bg-sky-100 text-sky-800 border-sky-200',
    beverages: 'bg-purple-100 text-purple-800 border-purple-200',
    snacks: 'bg-pink-100 text-pink-800 border-pink-200',
    condiments: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    spices: 'bg-lime-100 text-lime-800 border-lime-200',
    other: 'bg-gray-100 text-gray-800 border-gray-200',
  };
  return colors[category];
}
