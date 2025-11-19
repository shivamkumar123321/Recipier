/**
 * Meal Plans List Page
 *
 * View all saved meal plans with options to create new ones
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Plus, Calendar, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { useMealPlans } from '@/lib/hooks/useMealPlans';
import { MealPlanCard } from '@/components/features/meal-plans/MealPlanCard';

export default function MealPlansPage() {
  const [filter, setFilter] = useState<'all' | 'active'>('all');

  // Fetch meal plans
  const { data: allPlans = [], isLoading } = useMealPlans();
  const { data: activePlans = [] } = useMealPlans({ is_active: true });

  const filteredPlans = filter === 'active' ? activePlans : allPlans;

  return (
    <div className="container mx-auto space-y-8 py-8">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Meal Plans</h1>
          <p className="mt-2 text-muted-foreground">
            Plan your meals for the week with AI-powered suggestions
          </p>
        </div>
        <Link href="/meal-plans/generate">
          <Button size="lg">
            <Sparkles className="mr-2 h-5 w-5" />
            Generate New Plan
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Tabs value={filter} onValueChange={(v) => setFilter(v as any)}>
        <TabsList>
          <TabsTrigger value="all">
            All Plans ({allPlans.length})
          </TabsTrigger>
          <TabsTrigger value="active">
            Active ({activePlans.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-6">
          {/* Loading State */}
          {isLoading && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="space-y-3">
                  <Skeleton className="h-48 w-full rounded-lg" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              ))}
            </div>
          )}

          {/* Meal Plans Grid */}
          {!isLoading && filteredPlans.length > 0 && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filteredPlans.map((plan) => (
                <MealPlanCard key={plan.id} mealPlan={plan} />
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && filteredPlans.length === 0 && (
            <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg border border-dashed">
              <Calendar className="h-16 w-16 text-muted-foreground/50" />
              <h3 className="mt-4 text-lg font-semibold">
                {filter === 'active'
                  ? 'No active meal plans'
                  : 'No meal plans yet'}
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {filter === 'active'
                  ? 'Create a new meal plan to get started'
                  : 'Generate your first AI-powered meal plan'}
              </p>
              <Link href="/meal-plans/generate">
                <Button className="mt-4">
                  <Plus className="mr-2 h-4 w-4" />
                  Generate Meal Plan
                </Button>
              </Link>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Quick Info Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            How It Works
          </h4>
          <p className="mt-2 text-sm">
            Tell us your goals and preferences, and we'll create a personalized
            meal plan using AI
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Use Your Inventory
          </h4>
          <p className="mt-2 text-sm">
            We'll prioritize recipes that use ingredients you already have to
            minimize waste
          </p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <h4 className="text-sm font-medium text-muted-foreground">
            Flexible Plans
          </h4>
          <p className="mt-2 text-sm">
            Edit meals, swap recipes, and create grocery lists directly from
            your plan
          </p>
        </div>
      </div>
    </div>
  );
}
