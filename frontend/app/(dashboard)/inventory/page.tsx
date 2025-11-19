/**
 * Inventory Page
 *
 * Manage pantry and fridge items with search, filters, and multiple input methods
 */

'use client';

import { useState } from 'react';
import { Plus, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useInventoryItems, useFoodCategories } from '@/lib/hooks/useInventory';
import { InventoryItem } from '@/components/features/inventory/InventoryItem';
import { InventoryFilters } from '@/components/features/inventory/InventoryFilters';
import { AddItemDialog } from '@/components/features/inventory/AddItemDialog';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { InventoryItem as InventoryItemType } from '@/lib/api/inventory';
import { getExpirationStatus } from '@/components/features/inventory/ExpirationBadge';

export default function InventoryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();
  const [sortBy, setSortBy] = useState('name');
  const [showExpired, setShowExpired] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItemType | null>(null);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);

  // Fetch categories
  const { data: categories = [], isLoading: categoriesLoading } =
    useFoodCategories();

  // Parse sort option
  const getSortParams = (sortValue: string) => {
    if (sortValue.startsWith('-')) {
      return { sort_by: sortValue.slice(1), sort_order: 'desc' as const };
    }
    return { sort_by: sortValue, sort_order: 'asc' as const };
  };

  const sortParams = getSortParams(sortBy);

  // Fetch inventory items
  const { data: items = [], isLoading: itemsLoading } = useInventoryItems({
    category_id: selectedCategory,
    search: searchQuery || undefined,
    sort_by: sortParams.sort_by as any,
    sort_order: sortParams.sort_order,
  });

  // Filter items based on expiration
  const filteredItems = showExpired
    ? items
    : items.filter((item) => {
        const status = getExpirationStatus(item.expiration_date);
        return status.status !== 'expired';
      });

  // Find expiring soon items for alert
  const expiringSoonItems = items.filter((item) => {
    const status = getExpirationStatus(item.expiration_date);
    return status.status === 'expiring_soon';
  });

  const handleEditItem = (item: InventoryItemType) => {
    setEditingItem(item);
    setIsAddDialogOpen(true);
  };

  return (
    <div className="container mx-auto space-y-6 py-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Inventory</h1>
          <p className="text-muted-foreground">
            Manage your pantry and fridge items
          </p>
        </div>
        <AddItemDialog
          trigger={
            <Button size="lg">
              <Plus className="mr-2 h-5 w-5" />
              Add Item
            </Button>
          }
          open={isAddDialogOpen}
          onOpenChange={setIsAddDialogOpen}
        />
      </div>

      {/* Expiring Soon Alert */}
      {expiringSoonItems.length > 0 && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertTitle className="text-orange-900">
            ⚠️ {expiringSoonItems.length} item(s) expiring soon
          </AlertTitle>
          <AlertDescription className="text-orange-800">
            {expiringSoonItems.slice(0, 3).map((item) => item.name).join(', ')}
            {expiringSoonItems.length > 3 && ` and ${expiringSoonItems.length - 3} more`}
          </AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <InventoryFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        categories={categories}
        sortBy={sortBy}
        onSortChange={setSortBy}
        showExpired={showExpired}
        onShowExpiredChange={setShowExpired}
      />

      {/* Loading State */}
      {(itemsLoading || categoriesLoading) && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-lg" />
          ))}
        </div>
      )}

      {/* Items Grid */}
      {!itemsLoading && !categoriesLoading && (
        <>
          {filteredItems.length > 0 ? (
            <>
              <div className="text-sm text-muted-foreground">
                Showing {filteredItems.length} item(s)
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {filteredItems.map((item) => (
                  <InventoryItem
                    key={item.id}
                    item={item}
                    onEdit={handleEditItem}
                  />
                ))}
              </div>
            </>
          ) : (
            /* Empty State */
            <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-dashed">
              <Package className="h-16 w-16 text-muted-foreground/50" />
              <h3 className="mt-4 text-lg font-semibold">No items found</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {searchQuery || selectedCategory
                  ? 'Try adjusting your filters'
                  : 'Get started by adding your first item'}
              </p>
              {!searchQuery && !selectedCategory && (
                <Button
                  className="mt-4"
                  onClick={() => setIsAddDialogOpen(true)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Add Your First Item
                </Button>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
