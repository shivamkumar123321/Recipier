/**
 * RecipeFilters Component
 *
 * Filter controls for recipe search
 */

'use client';

import { Search, SlidersHorizontal, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { RecipeSearchParams } from '@/lib/api/recipes';

interface RecipeFiltersProps {
  filters: RecipeSearchParams;
  onChange: (filters: RecipeSearchParams) => void;
  onReset: () => void;
}

const CUISINES = [
  'Italian',
  'Mexican',
  'Asian',
  'Mediterranean',
  'American',
  'Indian',
  'French',
  'Japanese',
  'Thai',
  'Chinese',
];

const DIETARY_TAGS = [
  'Vegetarian',
  'Vegan',
  'Gluten-Free',
  'Dairy-Free',
  'Keto',
  'Paleo',
  'Low-Carb',
  'High-Protein',
];

const DIFFICULTY_LEVELS = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

const COOK_TIME_OPTIONS = [
  { value: '15', label: 'Under 15 min' },
  { value: '30', label: 'Under 30 min' },
  { value: '45', label: 'Under 45 min' },
  { value: '60', label: 'Under 1 hour' },
];

export function RecipeFilters({
  filters,
  onChange,
  onReset,
}: RecipeFiltersProps) {
  const updateFilter = (key: keyof RecipeSearchParams, value: any) => {
    onChange({ ...filters, [key]: value });
  };

  const toggleDietaryTag = (tag: string) => {
    const currentTags = filters.dietary_tags || [];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter((t) => t !== tag)
      : [...currentTags, tag];
    updateFilter('dietary_tags', newTags);
  };

  const hasActiveFilters = () => {
    return (
      filters.cuisine ||
      filters.difficulty ||
      filters.max_cook_time ||
      (filters.dietary_tags && filters.dietary_tags.length > 0) ||
      filters.max_calories
    );
  };

  const activeFilterCount = () => {
    let count = 0;
    if (filters.cuisine) count++;
    if (filters.difficulty) count++;
    if (filters.max_cook_time) count++;
    if (filters.dietary_tags?.length) count += filters.dietary_tags.length;
    if (filters.max_calories) count++;
    return count;
  };

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search recipes..."
            value={filters.search || ''}
            onChange={(e) => updateFilter('search', e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Advanced Filters Popover */}
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" className="relative">
              <SlidersHorizontal className="mr-2 h-4 w-4" />
              Filters
              {activeFilterCount() > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -right-2 -top-2 h-5 w-5 rounded-full p-0 text-xs"
                >
                  {activeFilterCount()}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80" align="end">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Advanced Filters</h4>
                {hasActiveFilters() && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onReset}
                    className="h-auto p-0 text-xs text-muted-foreground hover:text-foreground"
                  >
                    Reset All
                  </Button>
                )}
              </div>

              {/* Cuisine */}
              <div className="space-y-2">
                <Label>Cuisine</Label>
                <Select
                  value={filters.cuisine || 'any'}
                  onValueChange={(value) =>
                    updateFilter('cuisine', value === 'any' ? undefined : value)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any cuisine" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any cuisine</SelectItem>
                    {CUISINES.map((cuisine) => (
                      <SelectItem key={cuisine} value={cuisine.toLowerCase()}>
                        {cuisine}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Difficulty */}
              <div className="space-y-2">
                <Label>Difficulty</Label>
                <Select
                  value={filters.difficulty || 'any'}
                  onValueChange={(value) =>
                    updateFilter('difficulty', value === 'any' ? undefined : value)
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any difficulty" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any difficulty</SelectItem>
                    {DIFFICULTY_LEVELS.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        {level.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Cook Time */}
              <div className="space-y-2">
                <Label>Cook Time</Label>
                <Select
                  value={filters.max_cook_time?.toString() || 'any'}
                  onValueChange={(value) =>
                    updateFilter(
                      'max_cook_time',
                      value === 'any' ? undefined : parseInt(value)
                    )
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any time" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any time</SelectItem>
                    {COOK_TIME_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Dietary Tags */}
              <div className="space-y-2">
                <Label>Dietary Preferences</Label>
                <div className="space-y-2">
                  {DIETARY_TAGS.map((tag) => (
                    <div key={tag} className="flex items-center space-x-2">
                      <Checkbox
                        id={tag}
                        checked={filters.dietary_tags?.includes(tag.toLowerCase())}
                        onCheckedChange={() => toggleDietaryTag(tag.toLowerCase())}
                      />
                      <label
                        htmlFor={tag}
                        className="text-sm font-normal leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        {tag}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Max Calories */}
              <div className="space-y-2">
                <Label>Max Calories per Serving</Label>
                <Input
                  type="number"
                  placeholder="e.g., 500"
                  value={filters.max_calories || ''}
                  onChange={(e) =>
                    updateFilter(
                      'max_calories',
                      e.target.value ? parseInt(e.target.value) : undefined
                    )
                  }
                />
              </div>
            </div>
          </PopoverContent>
        </Popover>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters() && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted-foreground">Active filters:</span>

          {filters.cuisine && (
            <Badge variant="secondary" className="gap-1">
              Cuisine: {filters.cuisine}
              <button
                onClick={() => updateFilter('cuisine', undefined)}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}

          {filters.difficulty && (
            <Badge variant="secondary" className="gap-1">
              {filters.difficulty}
              <button
                onClick={() => updateFilter('difficulty', undefined)}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}

          {filters.max_cook_time && (
            <Badge variant="secondary" className="gap-1">
              Under {filters.max_cook_time}min
              <button
                onClick={() => updateFilter('max_cook_time', undefined)}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}

          {filters.dietary_tags?.map((tag) => (
            <Badge key={tag} variant="secondary" className="gap-1">
              {tag}
              <button
                onClick={() => toggleDietaryTag(tag)}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}

          {filters.max_calories && (
            <Badge variant="secondary" className="gap-1">
              Max {filters.max_calories} cal
              <button
                onClick={() => updateFilter('max_calories', undefined)}
                className="ml-1 hover:text-destructive"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="h-7 text-xs"
          >
            Clear all
          </Button>
        </div>
      )}
    </div>
  );
}
