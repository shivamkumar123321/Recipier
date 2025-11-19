/**
 * Recipe Detail Page
 *
 * Complete recipe view with ingredients, instructions, and nutrition
 */

'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import {
  ArrowLeft,
  Heart,
  Clock,
  Users,
  ChefHat,
  Plus,
  PlayCircle,
  Share2,
  Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  useRecipe,
  useRecipeInventoryMatch,
  useSaveRecipe,
  useUnsaveRecipe,
} from '@/lib/hooks/useRecipes';
import { IngredientList } from '@/components/features/recipes/IngredientList';
import { CookingSteps } from '@/components/features/recipes/CookingSteps';
import { NutritionInfo } from '@/components/features/recipes/NutritionInfo';
import { cn } from '@/lib/utils';

export default function RecipeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const recipeId = Number(params.id);

  const [activeTab, setActiveTab] = useState<'ingredients' | 'instructions'>(
    'ingredients'
  );

  // Fetch recipe data
  const { data: recipe, isLoading } = useRecipe(recipeId);
  const { data: inventoryMatch } = useRecipeInventoryMatch(recipeId);

  // Mutations
  const saveRecipe = useSaveRecipe();
  const unsaveRecipe = useUnsaveRecipe();

  const [isFavorited, setIsFavorited] = useState(recipe?.is_favorited || false);

  const handleToggleFavorite = async () => {
    if (isFavorited) {
      await unsaveRecipe.mutateAsync(recipeId);
      setIsFavorited(false);
    } else {
      await saveRecipe.mutateAsync(recipeId);
      setIsFavorited(true);
    }
  };

  const handleStartCooking = () => {
    router.push(`/cooking/${recipeId}`);
  };

  const handleAddToMealPlan = () => {
    router.push(`/meal-plans/add-recipe/${recipeId}`);
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'bg-green-100 text-green-800 border-green-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      hard: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[difficulty as keyof typeof colors] || 'bg-gray-100';
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto max-w-6xl space-y-8 py-8">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-96 w-full rounded-lg" />
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-12 w-3/4" />
            <Skeleton className="h-64 w-full" />
          </div>
          <div className="space-y-4">
            <Skeleton className="h-96 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="container mx-auto max-w-6xl py-16 text-center">
        <ChefHat className="mx-auto h-16 w-16 text-muted-foreground" />
        <h2 className="mt-4 text-2xl font-bold">Recipe not found</h2>
        <p className="mt-2 text-muted-foreground">
          The recipe you're looking for doesn't exist or has been removed.
        </p>
        <Link href="/recipes">
          <Button className="mt-6">Browse Recipes</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-6xl space-y-8 py-8">
      {/* Back Button */}
      <div>
        <Link href="/recipes">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Recipes
          </Button>
        </Link>
      </div>

      {/* Hero Image */}
      <div className="relative h-96 overflow-hidden rounded-lg">
        {recipe.image_url ? (
          <Image
            src={recipe.image_url}
            alt={recipe.name}
            fill
            className="object-cover"
            priority
          />
        ) : (
          <div className="h-full w-full bg-gradient-to-br from-orange-400 via-red-400 to-pink-400" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />

        {/* Floating Action Buttons */}
        <div className="absolute right-4 top-4 flex gap-2">
          <Button
            variant="secondary"
            size="icon"
            className="h-10 w-10 rounded-full bg-white/90 backdrop-blur hover:bg-white"
          >
            <Share2 className="h-5 w-5" />
          </Button>
          <Button
            variant="secondary"
            size="icon"
            className={cn(
              'h-10 w-10 rounded-full backdrop-blur',
              isFavorited
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'bg-white/90 hover:bg-white'
            )}
            onClick={handleToggleFavorite}
            disabled={saveRecipe.isPending || unsaveRecipe.isPending}
          >
            <Heart
              className={cn('h-5 w-5', isFavorited && 'fill-current')}
            />
          </Button>
        </div>

        {/* Recipe Title Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
          <h1 className="text-4xl font-bold">{recipe.name}</h1>
          {recipe.description && (
            <p className="mt-2 text-lg text-white/90">{recipe.description}</p>
          )}
        </div>
      </div>

      {/* Recipe Meta & Actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className={getDifficultyColor(recipe.difficulty)}>
            <ChefHat className="mr-1 h-3 w-3" />
            {recipe.difficulty}
          </Badge>
          {recipe.cuisine && (
            <Badge variant="secondary">{recipe.cuisine}</Badge>
          )}
          {recipe.dietary_tags?.map((tag) => (
            <Badge key={tag} variant="outline">
              {tag}
            </Badge>
          ))}
        </div>

        <div className="flex gap-2">
          <Button onClick={handleAddToMealPlan} variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            Add to Meal Plan
          </Button>
          <Button onClick={handleStartCooking}>
            <PlayCircle className="mr-2 h-4 w-4" />
            Start Cooking
          </Button>
        </div>
      </div>

      {/* Recipe Stats */}
      <div className="grid grid-cols-3 gap-4 rounded-lg border bg-muted/30 p-4">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span className="text-sm">Total Time</span>
          </div>
          <p className="mt-1 text-2xl font-bold">{recipe.total_time} min</p>
          <p className="text-xs text-muted-foreground">
            Prep: {recipe.prep_time}m | Cook: {recipe.cook_time}m
          </p>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-muted-foreground">
            <Users className="h-4 w-4" />
            <span className="text-sm">Servings</span>
          </div>
          <p className="mt-1 text-2xl font-bold">{recipe.servings}</p>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 text-muted-foreground">
            <span className="text-sm">Calories</span>
          </div>
          <p className="mt-1 text-2xl font-bold">
            {recipe.calories_per_serving}
          </p>
          <p className="text-xs text-muted-foreground">per serving</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Left Column - Ingredients & Instructions */}
        <div className="lg:col-span-2">
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="ingredients">
                Ingredients ({recipe.ingredients?.length || 0})
              </TabsTrigger>
              <TabsTrigger value="instructions">
                Instructions ({recipe.instructions?.length || 0})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="ingredients" className="mt-6">
              {recipe.ingredients && recipe.ingredients.length > 0 ? (
                <IngredientList
                  ingredients={recipe.ingredients}
                  servings={recipe.servings}
                  inventoryMatch={inventoryMatch}
                />
              ) : (
                <div className="rounded-lg border border-dashed p-8 text-center">
                  <p className="text-muted-foreground">
                    No ingredients listed for this recipe
                  </p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="instructions" className="mt-6">
              {recipe.instructions && recipe.instructions.length > 0 ? (
                <CookingSteps
                  instructions={recipe.instructions}
                  interactive={false}
                />
              ) : (
                <div className="rounded-lg border border-dashed p-8 text-center">
                  <p className="text-muted-foreground">
                    No instructions available for this recipe
                  </p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Column - Nutrition */}
        <div>
          <NutritionInfo
            calories={recipe.calories_per_serving}
            protein={recipe.protein_per_serving}
            carbs={recipe.carbs_per_serving}
            fat={recipe.fat_per_serving}
            servings={recipe.servings}
          />
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="flex flex-col gap-4 rounded-lg border bg-muted/30 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="font-semibold">Ready to cook?</h3>
          <p className="text-sm text-muted-foreground">
            Start cooking mode for step-by-step guidance
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleAddToMealPlan} variant="outline">
            Add to Meal Plan
          </Button>
          <Button onClick={handleStartCooking} size="lg">
            <PlayCircle className="mr-2 h-5 w-5" />
            Start Cooking Mode
          </Button>
        </div>
      </div>
    </div>
  );
}
