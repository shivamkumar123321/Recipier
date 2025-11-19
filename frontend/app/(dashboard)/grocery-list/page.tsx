/**
 * Grocery Lists Page
 *
 * View all grocery lists with filtering and creation options
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Plus, ShoppingCart, CheckCircle2, Clock, Trash2, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
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
import { useGroceryLists, useDeleteGroceryList } from '@/lib/hooks/useGroceryLists';
import { GenerateListDialog } from '@/components/features/grocery/GenerateListDialog';
import { GroceryList } from '@/lib/api/grocery-lists';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';

export default function GroceryListsPage() {
  const [filter, setFilter] = useState<'active' | 'completed' | 'all'>('active');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [listToDelete, setListToDelete] = useState<number | null>(null);

  // Fetch grocery lists
  const { data: allLists = [], isLoading } = useGroceryLists();
  const deleteMutation = useDeleteGroceryList();

  const activeLists = allLists.filter((list) => list.is_active && !list.is_completed);
  const completedLists = allLists.filter((list) => list.is_completed);

  const displayLists =
    filter === 'active'
      ? activeLists
      : filter === 'completed'
        ? completedLists
        : allLists;

  const handleDeleteClick = (id: number) => {
    setListToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (listToDelete) {
      await deleteMutation.mutateAsync(listToDelete);
      setDeleteDialogOpen(false);
      setListToDelete(null);
    }
  };

  return (
    <div className="container mx-auto space-y-8 py-8">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Grocery Lists</h1>
          <p className="mt-2 text-muted-foreground">
            Manage your shopping lists and track purchases
          </p>
        </div>
        <div className="flex gap-2">
          <GenerateListDialog />
          <Link href="/grocery-list/new">
            <Button variant="outline" size="lg">
              <Plus className="mr-2 h-5 w-5" />
              Create New List
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <Tabs value={filter} onValueChange={(v) => setFilter(v as any)}>
        <TabsList>
          <TabsTrigger value="active">
            <Clock className="mr-2 h-4 w-4" />
            Active ({activeLists.length})
          </TabsTrigger>
          <TabsTrigger value="completed">
            <CheckCircle2 className="mr-2 h-4 w-4" />
            Completed ({completedLists.length})
          </TabsTrigger>
          <TabsTrigger value="all">All ({allLists.length})</TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-6">
          {/* Loading State */}
          {isLoading && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="space-y-3">
                  <Skeleton className="h-48 w-full rounded-lg" />
                </div>
              ))}
            </div>
          )}

          {/* Grocery Lists Grid */}
          {!isLoading && displayLists.length > 0 && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {displayLists.map((list) => (
                <GroceryListCard
                  key={list.id}
                  list={list}
                  onDelete={() => handleDeleteClick(list.id)}
                />
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && displayLists.length === 0 && (
            <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-dashed">
              <ShoppingCart className="h-16 w-16 text-muted-foreground/50" />
              <h3 className="mt-4 text-lg font-semibold">
                {filter === 'completed'
                  ? 'No completed lists'
                  : filter === 'active'
                    ? 'No active grocery lists'
                    : 'No grocery lists yet'}
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {filter === 'completed'
                  ? 'Complete a shopping trip to see it here'
                  : 'Create a new list or generate one from a meal plan'}
              </p>
              <div className="mt-4 flex gap-2">
                <GenerateListDialog
                  trigger={
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Generate from Meal Plan
                    </Button>
                  }
                />
                <Link href="/grocery-list/new">
                  <Button variant="outline">Create Manually</Button>
                </Link>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Quick Tips */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Generate from Meal Plans
          </h4>
          <p className="mt-2 text-sm">
            Automatically create shopping lists from your weekly meal plans
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Smart Categorization
          </h4>
          <p className="mt-2 text-sm">
            Items are auto-organized by store sections for efficient shopping
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Sync with Inventory
          </h4>
          <p className="mt-2 text-sm">
            Add purchased items directly to your pantry and fridge inventory
          </p>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Grocery List</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this grocery list? This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

interface GroceryListCardProps {
  list: GroceryList;
  onDelete: () => void;
}

function GroceryListCard({ list, onDelete }: GroceryListCardProps) {
  const progressPercentage =
    list.total_items > 0 ? (list.purchased_items / list.total_items) * 100 : 0;

  return (
    <Card className="group overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="relative">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-semibold">{list.name}</h3>
            {list.description && (
              <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                {list.description}
              </p>
            )}
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link href={`/grocery-list/${list.id}`}>View List</Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onDelete} className="text-destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {list.is_completed ? (
            <Badge variant="default" className="bg-green-600">
              <CheckCircle2 className="mr-1 h-3 w-3" />
              Completed
            </Badge>
          ) : (
            <Badge variant="secondary">
              <Clock className="mr-1 h-3 w-3" />
              Active
            </Badge>
          )}
          {list.meal_plan && (
            <Badge variant="outline">From: {list.meal_plan.name}</Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress */}
        <div>
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Shopping Progress</span>
            <span className="font-medium">
              {list.purchased_items} / {list.total_items} items
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-muted">
            <div
              className={cn(
                'h-full transition-all duration-300',
                list.is_completed ? 'bg-green-500' : 'bg-primary'
              )}
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Date */}
        <div className="text-xs text-muted-foreground">
          Created {format(new Date(list.created_at), 'MMM d, yyyy')}
        </div>
      </CardContent>

      <CardFooter className="border-t bg-muted/30">
        <Link href={`/grocery-list/${list.id}`} className="w-full">
          <Button variant="outline" className="w-full">
            <ShoppingCart className="mr-2 h-4 w-4" />
            {list.is_completed ? 'View List' : 'Start Shopping'}
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
