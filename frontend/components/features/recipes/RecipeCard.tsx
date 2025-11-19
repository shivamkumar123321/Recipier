/**
 * RecipeCard Component
 *
 * Display recipe summary in card format
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Clock, Users, Flame, Heart, ChefHat } from 'lucide-react';
import { Recipe } from '@/lib/api/recipes';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useSaveRecipe, useUnsaveRecipe } from '@/lib/hooks/useRecipes';
import { cn } from '@/lib/utils';

interface RecipeCardProps {
  recipe: Recipe;
  className?: string;
  showFavoriteButton?: boolean;
}

export function RecipeCard({
  recipe,
  className,
  showFavoriteButton = true,
}: RecipeCardProps) {
  const [isFavorited, setIsFavorited] = useState(recipe.is_favorited || false);
  const saveRecipe = useSaveRecipe();
  const unsaveRecipe = useUnsaveRecipe();

  const handleToggleFavorite = async (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent card link navigation
    e.stopPropagation();

    if (isFavorited) {
      // TODO: Need user_recipe_id to unsave
      // For now, just toggle optimistically
      setIsFavorited(false);
    } else {
      await saveRecipe.mutateAsync(recipe.id);
      setIsFavorited(true);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'bg-green-100 text-green-800 border-green-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      hard: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[difficulty as keyof typeof colors] || '';
  };

  return (
    <Link href={`/recipes/${recipe.id}`}>
      <Card
        className={cn(
          'group overflow-hidden transition-all hover:shadow-lg',
          className
        )}
      >
        {/* Recipe Image */}
        <div className="relative aspect-video overflow-hidden bg-muted">
          {recipe.image_url ? (
            <Image
              src={recipe.image_url}
              alt={recipe.name}
              fill
              className="object-cover transition-transform group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full items-center justify-center bg-gradient-to-br from-primary/10 to-secondary/10">
              <ChefHat className="h-16 w-16 text-muted-foreground/50" />
            </div>
          )}

          {/* Favorite Button */}
          {showFavoriteButton && (
            <button
              onClick={handleToggleFavorite}
              className={cn(
                'absolute right-2 top-2 rounded-full p-2 transition-colors',
                isFavorited
                  ? 'bg-red-500 text-white hover:bg-red-600'
                  : 'bg-white/90 text-muted-foreground hover:bg-white hover:text-red-500'
              )}
            >
              <Heart
                className={cn('h-5 w-5', isFavorited && 'fill-current')}
              />
            </button>
          )}

          {/* Difficulty Badge */}
          <div className="absolute bottom-2 left-2">
            <Badge variant="outline" className={getDifficultyColor(recipe.difficulty)}>
              {recipe.difficulty}
            </Badge>
          </div>
        </div>

        <CardContent className="p-4">
          {/* Recipe Name */}
          <h3 className="line-clamp-2 text-lg font-semibold group-hover:text-primary">
            {recipe.name}
          </h3>

          {/* Description */}
          {recipe.description && (
            <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
              {recipe.description}
            </p>
          )}

          {/* Tags */}
          {recipe.cuisine && (
            <div className="mt-2 flex flex-wrap gap-1">
              <Badge variant="secondary" className="text-xs">
                {recipe.cuisine}
              </Badge>
              {recipe.dietary_tags?.slice(0, 2).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}

          {/* Stats */}
          <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>{recipe.total_time || recipe.cook_time}min</span>
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <Users className="h-4 w-4" />
              <span>{recipe.servings}</span>
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <Flame className="h-4 w-4" />
              <span>{recipe.calories_per_serving}</span>
            </div>
          </div>
        </CardContent>

        <CardFooter className="border-t bg-muted/30 p-4">
          <div className="flex w-full items-center justify-between text-sm">
            <div>
              <span className="font-medium">{recipe.protein_per_serving}g</span>
              <span className="ml-1 text-muted-foreground">protein</span>
            </div>
            <div>
              <span className="font-medium">{recipe.carbs_per_serving}g</span>
              <span className="ml-1 text-muted-foreground">carbs</span>
            </div>
            <div>
              <span className="font-medium">{recipe.fat_per_serving}g</span>
              <span className="ml-1 text-muted-foreground">fat</span>
            </div>
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}
