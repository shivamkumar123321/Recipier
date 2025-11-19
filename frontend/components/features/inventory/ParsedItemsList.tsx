/**
 * ParsedItemsList Component
 *
 * Display and edit parsed items from voice/camera input
 */

'use client';

import { X, Edit2, Check } from 'lucide-react';
import { useState } from 'react';
import { ParsedInventoryItem, FoodCategory } from '@/lib/api/inventory';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

interface ParsedItemsListProps {
  items: ParsedInventoryItem[];
  categories: FoodCategory[];
  onUpdate: (items: ParsedInventoryItem[]) => void;
}

export function ParsedItemsList({
  items,
  categories,
  onUpdate,
}: ParsedItemsListProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<ParsedInventoryItem | null>(null);

  const handleRemove = (index: number) => {
    const newItems = items.filter((_, i) => i !== index);
    onUpdate(newItems);
  };

  const handleEdit = (index: number) => {
    setEditingIndex(index);
    setEditForm({ ...items[index] });
  };

  const handleSaveEdit = () => {
    if (editingIndex !== null && editForm) {
      const newItems = [...items];
      newItems[editingIndex] = editForm;
      onUpdate(newItems);
      setEditingIndex(null);
      setEditForm(null);
    }
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditForm(null);
  };

  return (
    <div className="space-y-2">
      {items.map((item, index) => (
        <div
          key={index}
          className="flex items-center gap-2 rounded-lg border bg-card p-3"
        >
          {editingIndex === index && editForm ? (
            // Edit Mode
            <div className="flex flex-1 flex-wrap gap-2">
              <Input
                value={editForm.name}
                onChange={(e) =>
                  setEditForm({ ...editForm, name: e.target.value })
                }
                className="min-w-[150px] flex-1"
                placeholder="Item name"
              />
              <div className="flex gap-1">
                <Input
                  type="number"
                  value={editForm.quantity}
                  onChange={(e) =>
                    setEditForm({
                      ...editForm,
                      quantity: parseFloat(e.target.value),
                    })
                  }
                  className="w-20"
                  placeholder="Qty"
                />
                <Input
                  value={editForm.unit}
                  onChange={(e) =>
                    setEditForm({ ...editForm, unit: e.target.value })
                  }
                  className="w-20"
                  placeholder="Unit"
                />
              </div>
              <Select
                value={editForm.category}
                onValueChange={(value) =>
                  setEditForm({ ...editForm, category: value })
                }
              >
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.name}>
                      {cat.icon && `${cat.icon} `}
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                type="date"
                value={editForm.expiration_date || ''}
                onChange={(e) =>
                  setEditForm({ ...editForm, expiration_date: e.target.value })
                }
                className="w-[150px]"
                placeholder="Expiry"
              />
              <div className="flex gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleSaveEdit}
                  className="h-8 w-8 p-0"
                >
                  <Check className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleCancelEdit}
                  className="h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ) : (
            // View Mode
            <>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{item.name}</span>
                  {item.category && (
                    <Badge variant="outline" className="text-xs">
                      {item.category}
                    </Badge>
                  )}
                  {item.confidence !== undefined && item.confidence < 0.8 && (
                    <Badge variant="secondary" className="text-xs">
                      Low confidence
                    </Badge>
                  )}
                </div>
                <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
                  <span>
                    {item.quantity} {item.unit}
                  </span>
                  {item.expiration_date && (
                    <span>Expires: {item.expiration_date}</span>
                  )}
                </div>
              </div>
              <div className="flex gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleEdit(index)}
                  className="h-8 w-8 p-0"
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleRemove(index)}
                  className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
