/**
 * IngredientList Component
 *
 * Display recipe ingredients with inventory match indicators
 */

'use client';

import { Check, X, Package } from 'lucide-react';
import { RecipeIngredient } from '@/lib/api/recipes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface IngredientListProps {
  ingredients: RecipeIngredient[];
  inventoryMatch?: {
    matched_ingredients: string[];
    missing_ingredients: string[];
    match_percentage: number;
  };
  className?: string;
}

export function IngredientList({
  ingredients,
  inventoryMatch,
  className,
}: IngredientListProps) {
  const isIngredientInInventory = (ingredientName: string): boolean => {
    if (!inventoryMatch) return false;
    return inventoryMatch.matched_ingredients.some((matched) =>
      ingredientName.toLowerCase().includes(matched.toLowerCase())
    );
  };

  const sortedIngredients = [...ingredients].sort(
    (a, b) => a.order_index - b.order_index
  );

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Ingredients
          </CardTitle>
          {inventoryMatch && (
            <Badge variant="outline" className="text-sm">
              {inventoryMatch.match_percentage}% in inventory
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {sortedIngredients.map((ingredient) => {
            const inInventory = isIngredientInInventory(ingredient.name);

            return (
              <div
                key={ingredient.id}
                className={cn(
                  'flex items-start gap-3 rounded-lg border p-3 transition-colors',
                  inInventory
                    ? 'border-green-200 bg-green-50'
                    : 'border-muted bg-muted/30'
                )}
              >
                {/* Inventory Indicator */}
                <div
                  className={cn(
                    'mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full',
                    inInventory
                      ? 'bg-green-500 text-white'
                      : 'bg-muted-foreground/20 text-muted-foreground'
                  )}
                >
                  {inInventory ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <X className="h-3 w-3" />
                  )}
                </div>

                {/* Ingredient Details */}
                <div className="flex-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-medium">
                      {ingredient.quantity} {ingredient.unit}
                    </span>
                    <span className={cn(inInventory && 'text-green-900')}>
                      {ingredient.name}
                    </span>
                  </div>
                  {ingredient.notes && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      {ingredient.notes}
                    </p>
                  )}
                </div>

                {/* Status Label */}
                {inInventory && (
                  <Badge variant="outline" className="bg-green-100 text-green-800 border-green-200">
                    In Stock
                  </Badge>
                )}
              </div>
            );
          })}
        </div>

        {/* Shopping List Helper */}
        {inventoryMatch && inventoryMatch.missing_ingredients.length > 0 && (
          <div className="mt-6 rounded-lg border border-orange-200 bg-orange-50 p-4">
            <h4 className="mb-2 font-medium text-orange-900">
              Missing Ingredients
            </h4>
            <p className="text-sm text-orange-800">
              You need {inventoryMatch.missing_ingredients.length} item(s) to make
              this recipe. Add them to your shopping list?
            </p>
          </div>
        )}

        {/* Summary */}
        <div className="mt-4 flex items-center justify-between rounded-lg bg-muted p-3 text-sm">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              <div className="h-3 w-3 rounded-full bg-green-500" />
              <span>{inventoryMatch?.matched_ingredients.length || 0} in stock</span>
            </div>
            <span className="text-muted-foreground">•</span>
            <div className="flex items-center gap-1">
              <div className="h-3 w-3 rounded-full bg-muted-foreground/20" />
              <span>{inventoryMatch?.missing_ingredients.length || ingredients.length} to buy</span>
            </div>
          </div>
          <span className="font-medium">
            Total: {ingredients.length} items
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
