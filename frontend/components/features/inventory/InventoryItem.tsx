/**
 * InventoryItem Component
 *
 * Individual inventory item card with actions
 */

'use client';

import { useState } from 'react';
import { MoreVertical, Edit2, Trash2, Package } from 'lucide-react';
import { InventoryItem as InventoryItemType } from '@/lib/api/inventory';
import { ExpirationBadge } from './ExpirationBadge';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useDeleteInventoryItem } from '@/lib/hooks/useInventory';
import { cn } from '@/lib/utils';

interface InventoryItemProps {
  item: InventoryItemType;
  onEdit?: (item: InventoryItemType) => void;
  className?: string;
}

export function InventoryItem({ item, onEdit, className }: InventoryItemProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const deleteItem = useDeleteInventoryItem();

  const handleDelete = async () => {
    await deleteItem.mutateAsync(item.id);
    setShowDeleteDialog(false);
  };

  const getCategoryColor = (categoryName?: string) => {
    const colors: Record<string, string> = {
      Vegetables: 'bg-green-100 text-green-800 border-green-200',
      Fruits: 'bg-red-100 text-red-800 border-red-200',
      Proteins: 'bg-pink-100 text-pink-800 border-pink-200',
      Grains: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      Dairy: 'bg-blue-100 text-blue-800 border-blue-200',
      Other: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[categoryName || 'Other'] || colors.Other;
  };

  const isLowStock = item.quantity <= 1;

  return (
    <>
      <div
        className={cn(
          'group relative rounded-lg border bg-card p-4 shadow-sm transition-all hover:shadow-md',
          className
        )}
      >
        <div className="flex items-start justify-between gap-3">
          {/* Item Icon/Image */}
          <div className="flex-shrink-0">
            {item.image_url ? (
              <img
                src={item.image_url}
                alt={item.name}
                className="h-12 w-12 rounded-md object-cover"
              />
            ) : (
              <div className="flex h-12 w-12 items-center justify-center rounded-md bg-muted">
                <Package className="h-6 w-6 text-muted-foreground" />
              </div>
            )}
          </div>

          {/* Item Details */}
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-foreground truncate">
              {item.name}
            </h3>

            <div className="mt-1 flex flex-wrap items-center gap-2">
              {/* Quantity */}
              <span
                className={cn(
                  'text-sm font-medium',
                  isLowStock ? 'text-orange-600' : 'text-muted-foreground'
                )}
              >
                {item.quantity} {item.unit}
              </span>

              {/* Category */}
              {item.category && (
                <Badge
                  variant="outline"
                  className={cn('text-xs', getCategoryColor(item.category.name))}
                >
                  {item.category.name}
                </Badge>
              )}

              {/* Low Stock Warning */}
              {isLowStock && (
                <Badge variant="outline" className="bg-orange-100 text-orange-800 border-orange-200">
                  Low Stock
                </Badge>
              )}
            </div>

            {/* Expiration */}
            {item.expiration_date && (
              <div className="mt-2">
                <ExpirationBadge expirationDate={item.expiration_date} />
              </div>
            )}

            {/* Location */}
            {item.location && (
              <p className="mt-1 text-xs text-muted-foreground">
                📍 {item.location}
              </p>
            )}

            {/* Notes */}
            {item.notes && (
              <p className="mt-1 text-xs text-muted-foreground line-clamp-1">
                💬 {item.notes}
              </p>
            )}
          </div>

          {/* Actions */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 opacity-0 transition-opacity group-hover:opacity-100"
              >
                <MoreVertical className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={() => onEdit?.(item)}
                className="cursor-pointer"
              >
                <Edit2 className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => setShowDeleteDialog(true)}
                className="cursor-pointer text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Item</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{item.name}"? This action cannot
              be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteItem.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
