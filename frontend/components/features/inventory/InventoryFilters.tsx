/**
 * InventoryFilters Component
 *
 * Search, filter, and sort controls for inventory
 */

'use client';

import { Search, SlidersHorizontal } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FoodCategory } from '@/lib/api/inventory';

interface InventoryFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedCategory?: number;
  onCategoryChange: (category?: number) => void;
  categories: FoodCategory[];
  sortBy: string;
  onSortChange: (sort: string) => void;
  showExpired?: boolean;
  onShowExpiredChange?: (show: boolean) => void;
}

export function InventoryFilters({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  categories,
  sortBy,
  onSortChange,
  showExpired,
  onShowExpiredChange,
}: InventoryFiltersProps) {
  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search inventory..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Sort Dropdown */}
        <Select value={sortBy} onValueChange={onSortChange}>
          <SelectTrigger className="w-[180px]">
            <SlidersHorizontal className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Name (A-Z)</SelectItem>
            <SelectItem value="-name">Name (Z-A)</SelectItem>
            <SelectItem value="expiration_date">Expiring Soon</SelectItem>
            <SelectItem value="-expiration_date">Expiring Last</SelectItem>
            <SelectItem value="quantity">Quantity (Low-High)</SelectItem>
            <SelectItem value="-quantity">Quantity (High-Low)</SelectItem>
            <SelectItem value="-created_at">Recently Added</SelectItem>
            <SelectItem value="created_at">Oldest First</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category Tabs */}
      <Tabs
        value={selectedCategory?.toString() || 'all'}
        onValueChange={(value) =>
          onCategoryChange(value === 'all' ? undefined : parseInt(value))
        }
      >
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="all">All Items</TabsTrigger>
          {categories.map((category) => (
            <TabsTrigger key={category.id} value={category.id.toString()}>
              {category.icon && <span className="mr-1">{category.icon}</span>}
              {category.name}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Additional Filters */}
      {onShowExpiredChange && (
        <div className="flex items-center gap-2">
          <Button
            variant={showExpired ? 'default' : 'outline'}
            size="sm"
            onClick={() => onShowExpiredChange(!showExpired)}
          >
            {showExpired ? 'Hide' : 'Show'} Expired Items
          </Button>
        </div>
      )}
    </div>
  );
}
