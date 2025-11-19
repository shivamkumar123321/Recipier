/**
 * Recipes List Page
 *
 * Browse and search recipes with advanced filtering
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ChefHat, Heart, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { useRecipes, useSavedRecipes } from '@/lib/hooks/useRecipes';
import { RecipeCard } from '@/components/features/recipes/RecipeCard';
import { RecipeFilters } from '@/components/features/recipes/RecipeFilters';
import { RecipeSearchParams } from '@/lib/api/recipes';

export default function RecipesPage() {
  const [view, setView] = useState<'all' | 'favorites'>('all');
  const [filters, setFilters] = useState<RecipeSearchParams>({});

  // Fetch recipes based on current filters
  const { data: allRecipes = [], isLoading } = useRecipes(filters);
  const { data: savedRecipes = [], isLoading: isSavedLoading } =
    useSavedRecipes();

  const displayRecipes = view === 'favorites' ? savedRecipes : allRecipes;
  const isLoadingRecipes = view === 'favorites' ? isSavedLoading : isLoading;

  const handleResetFilters = () => {
    setFilters({});
  };

  return (
    <div className="container mx-auto space-y-8 py-8">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Recipes</h1>
          <p className="mt-2 text-muted-foreground">
            Discover delicious recipes tailored to your preferences
          </p>
        </div>
        <Link href="/recipes/create">
          <Button size="lg" variant="outline">
            <Sparkles className="mr-2 h-5 w-5" />
            Create Custom Recipe
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <RecipeFilters
        filters={filters}
        onChange={setFilters}
        onReset={handleResetFilters}
      />

      {/* Tabs for All/Favorites */}
      <Tabs value={view} onValueChange={(v) => setView(v as any)}>
        <TabsList>
          <TabsTrigger value="all">
            <ChefHat className="mr-2 h-4 w-4" />
            All Recipes ({allRecipes.length})
          </TabsTrigger>
          <TabsTrigger value="favorites">
            <Heart className="mr-2 h-4 w-4" />
            Favorites ({savedRecipes.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={view} className="mt-6">
          {/* Loading State */}
          {isLoadingRecipes && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="space-y-3">
                  <Skeleton className="h-48 w-full rounded-lg" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                  <Skeleton className="h-8 w-full" />
                </div>
              ))}
            </div>
          )}

          {/* Recipes Grid */}
          {!isLoadingRecipes && displayRecipes.length > 0 && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {displayRecipes.map((recipe) => (
                <RecipeCard
                  key={recipe.id}
                  recipe={recipe}
                  showInventoryMatch
                />
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoadingRecipes && displayRecipes.length === 0 && (
            <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-dashed">
              {view === 'favorites' ? (
                <>
                  <Heart className="h-16 w-16 text-muted-foreground/50" />
                  <h3 className="mt-4 text-lg font-semibold">
                    No favorite recipes yet
                  </h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Browse recipes and click the heart icon to save your
                    favorites
                  </p>
                  <Button
                    className="mt-4"
                    onClick={() => setView('all')}
                    variant="outline"
                  >
                    Browse Recipes
                  </Button>
                </>
              ) : (
                <>
                  <ChefHat className="h-16 w-16 text-muted-foreground/50" />
                  <h3 className="mt-4 text-lg font-semibold">
                    No recipes found
                  </h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Try adjusting your filters or search terms
                  </p>
                  <Button
                    className="mt-4"
                    onClick={handleResetFilters}
                    variant="outline"
                  >
                    Clear Filters
                  </Button>
                </>
              )}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Quick Tips */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Use Your Inventory
          </h4>
          <p className="mt-2 text-sm">
            Recipes show which ingredients you already have in your pantry and
            fridge
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Save Favorites
          </h4>
          <p className="mt-2 text-sm">
            Click the heart icon to save recipes you love for quick access
            later
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Add to Meal Plans
          </h4>
          <p className="mt-2 text-sm">
            Schedule recipes in your meal plan and generate shopping lists
            automatically
          </p>
        </div>
      </div>
    </div>
  );
}
