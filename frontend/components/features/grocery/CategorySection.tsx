/**
 * CategorySection Component
 *
 * Groups grocery items by category with collapsible sections
 */

'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { GroceryListItem } from './GroceryListItem';
import {
  GroceryListItem as GroceryItemType,
  FoodCategory,
  getCategoryLabel,
  getCategoryIcon,
  getCategoryColor,
} from '@/lib/api/grocery-lists';
import { cn } from '@/lib/utils';

interface CategorySectionProps {
  category: FoodCategory;
  items: GroceryItemType[];
  onTogglePurchased: (itemId: number) => void;
  onDeleteItem: (itemId: number) => void;
  onUpdateItem?: (itemId: number, data: { quantity?: number; notes?: string }) => void;
  defaultExpanded?: boolean;
}

export function CategorySection({
  category,
  items,
  onTogglePurchased,
  onDeleteItem,
  onUpdateItem,
  defaultExpanded = true,
}: CategorySectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const totalItems = items.length;
  const purchasedItems = items.filter((item) => item.is_purchased).length;
  const progressPercentage = totalItems > 0 ? (purchasedItems / totalItems) * 100 : 0;

  if (items.length === 0) return null;

  return (
    <div className="space-y-2">
      {/* Category Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between rounded-lg border bg-card p-3 transition-colors hover:bg-muted/50"
      >
        <div className="flex items-center gap-3">
          {isExpanded ? (
            <ChevronDown className="h-5 w-5 text-muted-foreground" />
          ) : (
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          )}

          <span className="text-2xl">{getCategoryIcon(category)}</span>

          <div className="text-left">
            <h3 className="font-semibold">{getCategoryLabel(category)}</h3>
            <p className="text-xs text-muted-foreground">
              {purchasedItems} / {totalItems} items
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="outline" className={cn('text-xs', getCategoryColor(category))}>
            {totalItems}
          </Badge>

          {/* Progress indicator */}
          {purchasedItems > 0 && (
            <div className="h-2 w-24 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full bg-green-500 transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              />
            </div>
          )}
        </div>
      </button>

      {/* Category Items */}
      {isExpanded && (
        <div className="ml-8 space-y-2">
          {items.map((item) => (
            <GroceryListItem
              key={item.id}
              item={item}
              onTogglePurchased={onTogglePurchased}
              onDelete={onDeleteItem}
              onUpdate={onUpdateItem}
            />
          ))}
        </div>
      )}
    </div>
  );
}
