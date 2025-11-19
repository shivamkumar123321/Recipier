/**
 * GroceryListItem Component
 *
 * Individual grocery item with checkbox and swipe to delete
 */

'use client';

import { useState, useRef, TouchEvent, MouseEvent } from 'react';
import { Trash2, GripVertical, Edit2 } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { GroceryListItem as GroceryItemType, getCategoryColor } from '@/lib/api/grocery-lists';
import { cn } from '@/lib/utils';

interface GroceryListItemProps {
  item: GroceryItemType;
  onTogglePurchased: (itemId: number) => void;
  onDelete: (itemId: number) => void;
  onUpdate?: (itemId: number, data: { quantity?: number; notes?: string }) => void;
  isDraggable?: boolean;
}

export function GroceryListItem({
  item,
  onTogglePurchased,
  onDelete,
  onUpdate,
  isDraggable = false,
}: GroceryListItemProps) {
  const [swipeOffset, setSwipeOffset] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editedQuantity, setEditedQuantity] = useState(item.quantity.toString());
  const [editedNotes, setEditedNotes] = useState(item.notes || '');

  const startX = useRef(0);
  const currentX = useRef(0);
  const isDragging = useRef(false);

  const handleTouchStart = (e: TouchEvent) => {
    startX.current = e.touches[0].clientX;
    isDragging.current = true;
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (!isDragging.current) return;

    currentX.current = e.touches[0].clientX;
    const diff = currentX.current - startX.current;

    // Only allow left swipe (negative values)
    if (diff < 0) {
      setSwipeOffset(Math.max(diff, -100)); // Max swipe distance: 100px
    }
  };

  const handleTouchEnd = () => {
    isDragging.current = false;

    // If swiped more than 60px, show delete button
    if (swipeOffset < -60) {
      setSwipeOffset(-80);
    } else {
      setSwipeOffset(0);
    }
  };

  const handleMouseDown = (e: MouseEvent) => {
    if (window.matchMedia('(pointer: fine)').matches) {
      // Desktop/mouse device
      startX.current = e.clientX;
      isDragging.current = true;
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging.current) return;

    currentX.current = e.clientX;
    const diff = currentX.current - startX.current;

    if (diff < 0) {
      setSwipeOffset(Math.max(diff, -100));
    }
  };

  const handleMouseUp = () => {
    if (!isDragging.current) return;

    isDragging.current = false;

    if (swipeOffset < -60) {
      setSwipeOffset(-80);
    } else {
      setSwipeOffset(0);
    }
  };

  const handleDelete = () => {
    setSwipeOffset(0);
    onDelete(item.id);
  };

  const handleSaveEdit = () => {
    if (onUpdate) {
      onUpdate(item.id, {
        quantity: parseFloat(editedQuantity) || item.quantity,
        notes: editedNotes || undefined,
      });
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedQuantity(item.quantity.toString());
    setEditedNotes(item.notes || '');
    setIsEditing(false);
  };

  return (
    <div className="relative overflow-hidden">
      {/* Delete button (revealed on swipe) */}
      <div
        className={cn(
          'absolute right-0 top-0 flex h-full items-center bg-red-500 px-4 transition-opacity',
          swipeOffset < -60 ? 'opacity-100' : 'opacity-0'
        )}
      >
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDelete}
          className="text-white hover:bg-red-600 hover:text-white"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      {/* Main item content */}
      <div
        className={cn(
          'flex items-center gap-3 rounded-lg border bg-card p-3 transition-all',
          item.is_purchased && 'bg-muted/50 opacity-60',
          swipeOffset < 0 && 'shadow-md'
        )}
        style={{
          transform: `translateX(${swipeOffset}px)`,
          transition: isDragging.current ? 'none' : 'transform 0.2s ease-out',
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Drag handle */}
        {isDraggable && (
          <div className="cursor-move text-muted-foreground">
            <GripVertical className="h-4 w-4" />
          </div>
        )}

        {/* Checkbox */}
        <Checkbox
          checked={item.is_purchased}
          onCheckedChange={() => onTogglePurchased(item.id)}
          className="h-5 w-5"
        />

        {/* Item details */}
        <div className="flex-1">
          {isEditing ? (
            <div className="space-y-2">
              <div className="flex gap-2">
                <Input
                  type="number"
                  value={editedQuantity}
                  onChange={(e) => setEditedQuantity(e.target.value)}
                  className="w-20"
                  step="0.1"
                />
                <span className="flex items-center text-sm text-muted-foreground">
                  {item.unit}
                </span>
                <span
                  className={cn(
                    'flex items-center font-medium',
                    item.is_purchased && 'line-through'
                  )}
                >
                  {item.name}
                </span>
              </div>
              <Input
                placeholder="Add notes..."
                value={editedNotes}
                onChange={(e) => setEditedNotes(e.target.value)}
                className="text-xs"
              />
              <div className="flex gap-1">
                <Button size="sm" onClick={handleSaveEdit}>
                  Save
                </Button>
                <Button size="sm" variant="outline" onClick={handleCancelEdit}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-baseline gap-2">
                <span
                  className={cn(
                    'font-medium',
                    item.is_purchased && 'line-through text-muted-foreground'
                  )}
                >
                  {item.name}
                </span>
                <span className="text-sm text-muted-foreground">
                  {item.quantity} {item.unit}
                </span>
                <Badge
                  variant="outline"
                  className={cn('text-xs', getCategoryColor(item.category))}
                >
                  {item.category}
                </Badge>
              </div>
              {item.notes && (
                <p className="mt-1 text-xs text-muted-foreground">{item.notes}</p>
              )}
            </>
          )}
        </div>

        {/* Edit button */}
        {!isEditing && !item.is_purchased && onUpdate && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsEditing(true)}
            className="h-8 w-8 p-0"
          >
            <Edit2 className="h-4 w-4" />
          </Button>
        )}

        {/* Desktop delete button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDelete}
          className="hidden h-8 w-8 p-0 text-destructive hover:bg-destructive/10 hover:text-destructive sm:flex"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
