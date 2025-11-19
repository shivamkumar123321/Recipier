/**
 * Grocery List Detail Page
 *
 * View and manage individual grocery list with items
 */

'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  Plus,
  Share2,
  CheckCircle2,
  Package,
  Loader2,
  Copy,
  Check,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  useGroceryList,
  useUpdateGroceryList,
  useAddGroceryItem,
  useUpdateGroceryItem,
  useDeleteGroceryItem,
  useToggleItemPurchased,
  useAddToInventory,
  useShareGroceryList,
} from '@/lib/hooks/useGroceryLists';
import { CategorySection } from '@/components/features/grocery/CategorySection';
import {
  FoodCategory,
  getCategoryLabel,
  categorizeFoodItem,
} from '@/lib/api/grocery-lists';
import { cn } from '@/lib/utils';

export default function GroceryListDetailPage() {
  const params = useParams();
  const router = useRouter();
  const listId = Number(params.id);

  const [isAddItemDialogOpen, setIsAddItemDialogOpen] = useState(false);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [shareUrl, setShareUrl] = useState('');
  const [copied, setCopied] = useState(false);

  // Form state for adding items
  const [newItemName, setNewItemName] = useState('');
  const [newItemQuantity, setNewItemQuantity] = useState('1');
  const [newItemUnit, setNewItemUnit] = useState('unit');
  const [newItemCategory, setNewItemCategory] = useState<FoodCategory>('other');
  const [newItemNotes, setNewItemNotes] = useState('');

  // Fetch grocery list
  const { data: list, isLoading } = useGroceryList(listId);

  // Mutations
  const updateList = useUpdateGroceryList();
  const addItem = useAddGroceryItem();
  const updateItem = useUpdateGroceryItem();
  const deleteItem = useDeleteGroceryItem();
  const togglePurchased = useToggleItemPurchased();
  const addToInventory = useAddToInventory();
  const shareList = useShareGroceryList();

  // Auto-categorize when item name changes
  const handleItemNameChange = (name: string) => {
    setNewItemName(name);
    if (name.length > 2) {
      const suggestedCategory = categorizeFoodItem(name);
      setNewItemCategory(suggestedCategory);
    }
  };

  const handleAddItem = async () => {
    if (!newItemName.trim()) return;

    try {
      await addItem.mutateAsync({
        listId,
        data: {
          name: newItemName,
          quantity: parseFloat(newItemQuantity) || 1,
          unit: newItemUnit,
          category: newItemCategory,
          notes: newItemNotes || undefined,
        },
      });

      // Reset form
      setNewItemName('');
      setNewItemQuantity('1');
      setNewItemUnit('unit');
      setNewItemCategory('other');
      setNewItemNotes('');
      setIsAddItemDialogOpen(false);
    } catch (error) {
      console.error('Failed to add item:', error);
    }
  };

  const handleTogglePurchased = async (itemId: number) => {
    await togglePurchased.mutateAsync({ listId, itemId });
  };

  const handleDeleteItem = async (itemId: number) => {
    await deleteItem.mutateAsync({ listId, itemId });
  };

  const handleUpdateItem = async (
    itemId: number,
    data: { quantity?: number; notes?: string }
  ) => {
    await updateItem.mutateAsync({ listId, itemId, data });
  };

  const handleMarkComplete = async () => {
    await updateList.mutateAsync({
      id: listId,
      data: { is_completed: true },
    });
  };

  const handleAddToInventory = async () => {
    try {
      const result = await addToInventory.mutateAsync(listId);
      alert(`Added ${result.items_added} items to inventory!`);
    } catch (error) {
      console.error('Failed to add to inventory:', error);
    }
  };

  const handleShare = async () => {
    try {
      const result = await shareList.mutateAsync(listId);
      setShareUrl(result.share_url);
      setIsShareDialogOpen(true);
    } catch (error) {
      console.error('Failed to share list:', error);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto max-w-5xl space-y-8 py-8">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!list) {
    return (
      <div className="container mx-auto max-w-5xl py-16 text-center">
        <h2 className="text-2xl font-bold">Grocery list not found</h2>
        <Link href="/grocery-list">
          <Button className="mt-6">Back to Grocery Lists</Button>
        </Link>
      </div>
    );
  }

  // Group items by category
  const itemsByCategory = (list.items || []).reduce(
    (acc, item) => {
      if (!acc[item.category]) {
        acc[item.category] = [];
      }
      acc[item.category].push(item);
      return acc;
    },
    {} as Record<FoodCategory, typeof list.items>
  );

  const categories = Object.keys(itemsByCategory) as FoodCategory[];
  const progressPercentage =
    list.total_items > 0 ? (list.purchased_items / list.total_items) * 100 : 0;

  const allItemsPurchased =
    list.total_items > 0 && list.purchased_items === list.total_items;

  return (
    <div className="container mx-auto max-w-5xl space-y-8 py-8">
      {/* Header */}
      <div>
        <Link href="/grocery-list">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Lists
          </Button>
        </Link>
      </div>

      {/* Title & Actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{list.name}</h1>
          {list.description && (
            <p className="mt-2 text-muted-foreground">{list.description}</p>
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            {list.is_completed ? (
              <Badge variant="default" className="bg-green-600">
                <CheckCircle2 className="mr-1 h-3 w-3" />
                Completed
              </Badge>
            ) : (
              <Badge variant="secondary">Active</Badge>
            )}
            {list.meal_plan && (
              <Badge variant="outline">From: {list.meal_plan.name}</Badge>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={handleShare}>
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Button onClick={() => setIsAddItemDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Item
          </Button>
        </div>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Shopping Progress</h3>
                <p className="text-sm text-muted-foreground">
                  {list.purchased_items} of {list.total_items} items purchased
                </p>
              </div>
              <div className="text-3xl font-bold">{Math.round(progressPercentage)}%</div>
            </div>

            <Progress value={progressPercentage} className="h-3" />

            {allItemsPurchased && !list.is_completed && (
              <div className="flex items-center justify-between rounded-lg border border-green-200 bg-green-50 p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="font-medium text-green-900">
                      All items purchased!
                    </p>
                    <p className="text-sm text-green-700">
                      Add items to inventory or mark list as complete
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={handleAddToInventory}
                    disabled={addToInventory.isPending}
                  >
                    {addToInventory.isPending ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Package className="mr-2 h-4 w-4" />
                    )}
                    Add to Inventory
                  </Button>
                  <Button
                    onClick={handleMarkComplete}
                    disabled={updateList.isPending}
                  >
                    {updateList.isPending ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle2 className="mr-2 h-4 w-4" />
                    )}
                    Mark Complete
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Grocery Items by Category */}
      {list.items && list.items.length > 0 ? (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Items by Category</h2>
          {categories.map((category) => (
            <CategorySection
              key={category}
              category={category}
              items={itemsByCategory[category]}
              onTogglePurchased={handleTogglePurchased}
              onDeleteItem={handleDeleteItem}
              onUpdateItem={handleUpdateItem}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex min-h-[300px] flex-col items-center justify-center py-12">
            <Package className="h-16 w-16 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No items yet</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Add items to your grocery list to start shopping
            </p>
            <Button
              className="mt-4"
              onClick={() => setIsAddItemDialogOpen(true)}
            >
              <Plus className="mr-2 h-4 w-4" />
              Add First Item
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Add Item Dialog */}
      <Dialog open={isAddItemDialogOpen} onOpenChange={setIsAddItemDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Grocery Item</DialogTitle>
            <DialogDescription>
              Add a new item to your grocery list
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="item-name">Item Name</Label>
              <Input
                id="item-name"
                placeholder="e.g., Chicken breast"
                value={newItemName}
                onChange={(e) => handleItemNameChange(e.target.value)}
                autoFocus
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={newItemQuantity}
                  onChange={(e) => setNewItemQuantity(e.target.value)}
                  step="0.1"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="unit">Unit</Label>
                <Select value={newItemUnit} onValueChange={setNewItemUnit}>
                  <SelectTrigger id="unit">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="unit">unit</SelectItem>
                    <SelectItem value="lb">lb</SelectItem>
                    <SelectItem value="oz">oz</SelectItem>
                    <SelectItem value="g">g</SelectItem>
                    <SelectItem value="kg">kg</SelectItem>
                    <SelectItem value="cup">cup</SelectItem>
                    <SelectItem value="tbsp">tbsp</SelectItem>
                    <SelectItem value="tsp">tsp</SelectItem>
                    <SelectItem value="L">L</SelectItem>
                    <SelectItem value="ml">ml</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                value={newItemCategory}
                onValueChange={(v) => setNewItemCategory(v as FoodCategory)}
              >
                <SelectTrigger id="category">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(
                    [
                      'produce',
                      'dairy',
                      'meat',
                      'seafood',
                      'bakery',
                      'pantry',
                      'frozen',
                      'beverages',
                      'snacks',
                      'condiments',
                      'spices',
                      'other',
                    ] as FoodCategory[]
                  ).map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {getCategoryLabel(cat)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (optional)</Label>
              <Textarea
                id="notes"
                placeholder="e.g., organic, brand preference"
                value={newItemNotes}
                onChange={(e) => setNewItemNotes(e.target.value)}
                rows={2}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsAddItemDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleAddItem} disabled={!newItemName.trim() || addItem.isPending}>
              {addItem.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Item
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Share Dialog */}
      <Dialog open={isShareDialogOpen} onOpenChange={setIsShareDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Share Grocery List</DialogTitle>
            <DialogDescription>
              Share this grocery list with family or friends
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="flex gap-2">
              <Input value={shareUrl} readOnly />
              <Button variant="outline" onClick={handleCopyLink}>
                {copied ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Anyone with this link can view and edit this grocery list
            </p>
          </div>

          <DialogFooter>
            <Button onClick={() => setIsShareDialogOpen(false)}>Done</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
