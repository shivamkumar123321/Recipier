/**
 * MealPlanCard Component
 *
 * Display meal plan summary in card format
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import {
  Calendar,
  Target,
  MoreVertical,
  Trash2,
  Eye,
  ShoppingCart,
} from 'lucide-react';
import { MealPlan } from '@/lib/api/meal-plans';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
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
import { useDeleteMealPlan, useCreateGroceryList } from '@/lib/hooks/useMealPlans';
import { cn } from '@/lib/utils';

interface MealPlanCardProps {
  mealPlan: MealPlan;
  className?: string;
}

export function MealPlanCard({ mealPlan, className }: MealPlanCardProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const deleteMealPlan = useDeleteMealPlan();
  const createGroceryList = useCreateGroceryList();

  const handleDelete = async () => {
    await deleteMealPlan.mutateAsync(mealPlan.id);
    setShowDeleteDialog(false);
  };

  const handleCreateGroceryList = async () => {
    await createGroceryList.mutateAsync(mealPlan.id);
  };

  const getGoalBadgeColor = (goal: string) => {
    const colors = {
      weight_loss: 'bg-red-100 text-red-800 border-red-200',
      maintenance: 'bg-blue-100 text-blue-800 border-blue-200',
      muscle_gain: 'bg-green-100 text-green-800 border-green-200',
    };
    return colors[goal as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const totalMeals = mealPlan.items?.length || mealPlan.total_days * 3; // Estimate 3 meals per day

  return (
    <>
      <Card className={cn('group overflow-hidden transition-all hover:shadow-md', className)}>
        <CardHeader className="relative">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold">{mealPlan.name}</h3>
              {mealPlan.description && (
                <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                  {mealPlan.description}
                </p>
              )}
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <Link href={`/meal-plans/${mealPlan.id}`} className="cursor-pointer">
                    <Eye className="mr-2 h-4 w-4" />
                    View Details
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={handleCreateGroceryList}
                  disabled={createGroceryList.isPending}
                >
                  <ShoppingCart className="mr-2 h-4 w-4" />
                  Create Grocery List
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => setShowDeleteDialog(true)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <Badge variant="outline" className={getGoalBadgeColor(mealPlan.goal)}>
              <Target className="mr-1 h-3 w-3" />
              {mealPlan.goal.replace('_', ' ')}
            </Badge>
            {mealPlan.is_active && (
              <Badge variant="default">Active</Badge>
            )}
            {mealPlan.dietary_preferences?.length > 0 && (
              <Badge variant="secondary">
                {mealPlan.dietary_preferences[0]}
                {mealPlan.dietary_preferences.length > 1 &&
                  ` +${mealPlan.dietary_preferences.length - 1}`}
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Date Range */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>
              {format(new Date(mealPlan.start_date), 'MMM d')} -{' '}
              {format(new Date(mealPlan.end_date), 'MMM d, yyyy')}
            </span>
            <span className="ml-auto font-medium text-foreground">
              {mealPlan.total_days} days
            </span>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 rounded-lg bg-muted/50 p-3">
            <div>
              <p className="text-xs text-muted-foreground">Total Meals</p>
              <p className="text-lg font-semibold">{totalMeals}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Daily Calories</p>
              <p className="text-lg font-semibold">
                {mealPlan.target_calories || '~2000'}
              </p>
            </div>
          </div>

          {/* Sample Recipes Preview */}
          {mealPlan.items && mealPlan.items.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-medium text-muted-foreground">
                Sample Recipes:
              </p>
              <div className="flex flex-wrap gap-1">
                {mealPlan.items.slice(0, 3).map((item) => (
                  <Badge key={item.id} variant="outline" className="text-xs">
                    {item.recipe?.name || `Recipe ${item.id}`}
                  </Badge>
                ))}
                {mealPlan.items.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{mealPlan.items.length - 3} more
                  </Badge>
                )}
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="border-t bg-muted/30">
          <Link href={`/meal-plans/${mealPlan.id}`} className="w-full">
            <Button variant="outline" className="w-full">
              <Eye className="mr-2 h-4 w-4" />
              View Plan
            </Button>
          </Link>
        </CardFooter>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Meal Plan</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{mealPlan.name}"? This action
              cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteMealPlan.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
