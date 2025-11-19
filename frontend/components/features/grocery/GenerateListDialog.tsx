/**
 * GenerateListDialog Component
 *
 * Dialog to generate grocery list from meal plan
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Calendar, ShoppingCart, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useMealPlans } from '@/lib/hooks/useMealPlans';
import { useGenerateGroceryList } from '@/lib/hooks/useGroceryLists';
import { Badge } from '@/components/ui/badge';

interface GenerateListDialogProps {
  trigger?: React.ReactNode;
  onSuccess?: (listId: number) => void;
}

export function GenerateListDialog({ trigger, onSuccess }: GenerateListDialogProps) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedMealPlanId, setSelectedMealPlanId] = useState<string>('');
  const [listName, setListName] = useState('');
  const [excludeInventory, setExcludeInventory] = useState(true);

  // Fetch active meal plans
  const { data: mealPlans = [], isLoading: isMealPlansLoading } = useMealPlans({
    is_active: true,
  });

  // Generate mutation
  const generateList = useGenerateGroceryList();

  const handleGenerate = async () => {
    if (!selectedMealPlanId) return;

    try {
      const result = await generateList.mutateAsync({
        meal_plan_id: parseInt(selectedMealPlanId),
        name: listName || undefined,
        exclude_inventory: excludeInventory,
      });

      setIsOpen(false);

      // Navigate to the new list or call success callback
      if (onSuccess) {
        onSuccess(result.id);
      } else {
        router.push(`/grocery-list/${result.id}`);
      }

      // Reset form
      setSelectedMealPlanId('');
      setListName('');
      setExcludeInventory(true);
    } catch (error) {
      console.error('Failed to generate grocery list:', error);
    }
  };

  const selectedPlan = mealPlans.find(
    (plan) => plan.id === parseInt(selectedMealPlanId)
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button size="lg">
            <Sparkles className="mr-2 h-5 w-5" />
            Generate from Meal Plan
          </Button>
        )}
      </DialogTrigger>

      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" />
            Generate Grocery List
          </DialogTitle>
          <DialogDescription>
            Automatically create a grocery list from your meal plan
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Meal Plan Selection */}
          <div className="space-y-2">
            <Label htmlFor="meal-plan">Select Meal Plan</Label>
            {isMealPlansLoading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading meal plans...
              </div>
            ) : mealPlans.length === 0 ? (
              <div className="rounded-lg border border-dashed p-4 text-center">
                <Calendar className="mx-auto h-8 w-8 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">
                  No active meal plans found
                </p>
                <Button
                  variant="link"
                  size="sm"
                  className="mt-1"
                  onClick={() => router.push('/meal-plans/generate')}
                >
                  Create a meal plan first
                </Button>
              </div>
            ) : (
              <Select value={selectedMealPlanId} onValueChange={setSelectedMealPlanId}>
                <SelectTrigger id="meal-plan">
                  <SelectValue placeholder="Choose a meal plan" />
                </SelectTrigger>
                <SelectContent>
                  {mealPlans.map((plan) => (
                    <SelectItem key={plan.id} value={plan.id.toString()}>
                      <div className="flex items-center gap-2">
                        <span>{plan.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {plan.total_days} days
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          {/* Selected Plan Preview */}
          {selectedPlan && (
            <div className="rounded-lg border bg-muted/50 p-3">
              <h4 className="text-sm font-medium">{selectedPlan.name}</h4>
              <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                <div>
                  <span className="font-medium">Duration:</span> {selectedPlan.total_days}{' '}
                  days
                </div>
                <div>
                  <span className="font-medium">Meals:</span>{' '}
                  {selectedPlan.items?.length || 0}
                </div>
                <div>
                  <span className="font-medium">Goal:</span>{' '}
                  {selectedPlan.goal.replace('_', ' ')}
                </div>
                <div>
                  <span className="font-medium">Calories:</span>{' '}
                  {selectedPlan.target_calories || '~2000'}/day
                </div>
              </div>
            </div>
          )}

          {/* List Name */}
          <div className="space-y-2">
            <Label htmlFor="list-name">List Name (optional)</Label>
            <Input
              id="list-name"
              placeholder={
                selectedPlan
                  ? `Groceries for ${selectedPlan.name}`
                  : 'My Grocery List'
              }
              value={listName}
              onChange={(e) => setListName(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Auto-generated if left blank
            </p>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <div className="flex items-start space-x-2">
              <Checkbox
                id="exclude-inventory"
                checked={excludeInventory}
                onCheckedChange={(checked) =>
                  setExcludeInventory(checked as boolean)
                }
              />
              <div className="grid gap-1.5 leading-none">
                <label
                  htmlFor="exclude-inventory"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Exclude items already in inventory
                </label>
                <p className="text-xs text-muted-foreground">
                  Only add ingredients you don't already have
                </p>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleGenerate}
            disabled={!selectedMealPlanId || generateList.isPending}
          >
            {generateList.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Generate List
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
