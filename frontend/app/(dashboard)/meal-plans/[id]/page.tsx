/**
 * Meal Plan Detail Page
 *
 * View full meal plan with day-by-day breakdown, recipes, and actions
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
  ArrowLeft,
  Calendar,
  Target,
  ShoppingCart,
  ChefHat,
  Clock,
  Flame,
  Users,
  MoreVertical,
  Trash2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
import {
  useMealPlan,
  useMealPlanItems,
  useDeleteMealPlan,
  useCreateGroceryList,
} from '@/lib/hooks/useMealPlans';
import { MealPlanItem } from '@/lib/api/meal-plans';
import Image from 'next/image';

export default function MealPlanDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = parseInt(params.id as string);

  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const { data: mealPlan, isLoading: planLoading } = useMealPlan(id);
  const { data: items = [], isLoading: itemsLoading } = useMealPlanItems(id);
  const deleteMealPlan = useDeleteMealPlan();
  const createGroceryList = useCreateGroceryList();

  const handleDelete = async () => {
    await deleteMealPlan.mutateAsync(id);
    setShowDeleteDialog(false);
    router.push('/meal-plans');
  };

  const handleCreateGroceryList = async () => {
    await createGroceryList.mutateAsync(id);
    router.push('/shopping');
  };

  // Group meals by day
  const mealsByDay: Record<number, MealPlanItem[]> = {};
  items.forEach((item) => {
    if (!mealsByDay[item.day_number]) {
      mealsByDay[item.day_number] = [];
    }
    mealsByDay[item.day_number].push(item);
  });

  const getMealTypeIcon = (type: string) => {
    const icons = {
      breakfast: '🍳',
      lunch: '🥗',
      dinner: '🍽️',
      snack: '🍪',
    };
    return icons[type as keyof typeof icons] || '🍴';
  };

  const getMealTypeColor = (type: string) => {
    const colors = {
      breakfast: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      lunch: 'bg-green-100 text-green-800 border-green-200',
      dinner: 'bg-blue-100 text-blue-800 border-blue-200',
      snack: 'bg-purple-100 text-purple-800 border-purple-200',
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (planLoading || itemsLoading) {
    return (
      <div className="container mx-auto space-y-8 py-8">
        <Skeleton className="h-12 w-48" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!mealPlan) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold">Meal Plan Not Found</h1>
          <p className="mt-2 text-muted-foreground">
            The meal plan you're looking for doesn't exist.
          </p>
          <Link href="/meal-plans">
            <Button className="mt-4">Back to Meal Plans</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="container mx-auto space-y-8 py-8">
        {/* Back Button */}
        <div>
          <Link href="/meal-plans">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Meal Plans
            </Button>
          </Link>
        </div>

        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold tracking-tight">
              {mealPlan.name}
            </h1>
            {mealPlan.description && (
              <p className="mt-2 text-muted-foreground">
                {mealPlan.description}
              </p>
            )}

            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="outline" className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {format(new Date(mealPlan.start_date), 'MMM d')} -{' '}
                {format(new Date(mealPlan.end_date), 'MMM d, yyyy')}
              </Badge>
              <Badge variant="outline" className="flex items-center gap-1">
                <Target className="h-3 w-3" />
                {mealPlan.goal.replace('_', ' ')}
              </Badge>
              {mealPlan.is_active && <Badge>Active</Badge>}
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleCreateGroceryList}>
              <ShoppingCart className="mr-2 h-4 w-4" />
              Create Grocery List
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => setShowDeleteDialog(true)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete Plan
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 sm:grid-cols-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Total Days
                  </p>
                  <p className="text-2xl font-bold">{mealPlan.total_days}</p>
                </div>
                <Calendar className="h-8 w-8 text-muted-foreground/50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Total Meals
                  </p>
                  <p className="text-2xl font-bold">{items.length}</p>
                </div>
                <ChefHat className="h-8 w-8 text-muted-foreground/50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Daily Calories
                  </p>
                  <p className="text-2xl font-bold">
                    {mealPlan.target_calories || '~2000'}
                  </p>
                </div>
                <Flame className="h-8 w-8 text-muted-foreground/50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Servings
                  </p>
                  <p className="text-2xl font-bold">2</p>
                </div>
                <Users className="h-8 w-8 text-muted-foreground/50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Meals by Day */}
        <Card>
          <CardHeader>
            <CardTitle>Your Meal Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="1" className="w-full">
              <TabsList className="flex w-full flex-wrap justify-start">
                {Object.keys(mealsByDay).map((day) => (
                  <TabsTrigger key={day} value={day}>
                    Day {day}
                  </TabsTrigger>
                ))}
              </TabsList>

              {Object.entries(mealsByDay).map(([day, dayMeals]) => (
                <TabsContent key={day} value={day} className="mt-6 space-y-4">
                  {dayMeals
                    .sort((a, b) => {
                      const order = ['breakfast', 'lunch', 'dinner', 'snack'];
                      return (
                        order.indexOf(a.meal_type) - order.indexOf(b.meal_type)
                      );
                    })
                    .map((item) => (
                      <Card key={item.id} className="overflow-hidden">
                        <div className="flex flex-col md:flex-row">
                          {/* Recipe Image */}
                          {item.recipe?.image_url && (
                            <div className="relative h-48 w-full md:h-auto md:w-64">
                              <Image
                                src={item.recipe.image_url}
                                alt={item.recipe.name}
                                fill
                                className="object-cover"
                              />
                            </div>
                          )}

                          {/* Recipe Details */}
                          <div className="flex-1 p-6">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <Badge
                                  variant="outline"
                                  className={getMealTypeColor(item.meal_type)}
                                >
                                  {getMealTypeIcon(item.meal_type)}{' '}
                                  {item.meal_type}
                                </Badge>
                                <h3 className="mt-2 text-xl font-semibold">
                                  {item.recipe?.name || 'Recipe'}
                                </h3>
                                {item.recipe?.description && (
                                  <p className="mt-1 text-sm text-muted-foreground">
                                    {item.recipe.description}
                                  </p>
                                )}
                              </div>
                            </div>

                            {/* Recipe Info */}
                            {item.recipe && (
                              <div className="mt-4 grid gap-4 sm:grid-cols-4">
                                <div>
                                  <p className="text-xs text-muted-foreground">
                                    Prep Time
                                  </p>
                                  <p className="flex items-center gap-1 text-sm font-medium">
                                    <Clock className="h-3 w-3" />
                                    {item.recipe.prep_time} min
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">
                                    Calories
                                  </p>
                                  <p className="flex items-center gap-1 text-sm font-medium">
                                    <Flame className="h-3 w-3" />
                                    {item.recipe.calories_per_serving}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">
                                    Protein
                                  </p>
                                  <p className="text-sm font-medium">
                                    {item.recipe.protein_per_serving}g
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">
                                    Difficulty
                                  </p>
                                  <p className="text-sm font-medium capitalize">
                                    {item.recipe.difficulty}
                                  </p>
                                </div>
                              </div>
                            )}

                            {/* Actions */}
                            <div className="mt-4 flex gap-2">
                              {item.recipe && (
                                <Link
                                  href={`/cooking/${item.recipe.id}`}
                                  className="flex-1"
                                >
                                  <Button variant="default" className="w-full">
                                    <ChefHat className="mr-2 h-4 w-4" />
                                    Start Cooking
                                  </Button>
                                </Link>
                              )}
                              {item.recipe && (
                                <Link href={`/recipes/${item.recipe.id}`}>
                                  <Button variant="outline">View Recipe</Button>
                                </Link>
                              )}
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>

        {/* Dietary Preferences */}
        {mealPlan.dietary_preferences &&
          mealPlan.dietary_preferences.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Dietary Preferences</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {mealPlan.dietary_preferences.map((pref) => (
                    <Badge key={pref} variant="secondary">
                      {pref}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Meal Plan</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this meal plan? This action cannot
              be undone.
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
