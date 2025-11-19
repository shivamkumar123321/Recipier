/**
 * Generate Meal Plan Page
 *
 * Multi-step form for meal plan generation with real-time WebSocket updates
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { GeneratePlanForm } from '@/components/features/meal-plans/GeneratePlanForm';
import { MealPlanGenerator } from '@/components/features/meal-plans/MealPlanGenerator';
import { CreateMealPlanRequest } from '@/lib/api/meal-plans';

export default function GenerateMealPlanPage() {
  const router = useRouter();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationRequest, setGenerationRequest] =
    useState<CreateMealPlanRequest | null>(null);

  const handleFormSubmit = (request: CreateMealPlanRequest) => {
    setGenerationRequest(request);
    setIsGenerating(true);
  };

  const handleCancel = () => {
    if (isGenerating) {
      setIsGenerating(false);
      setGenerationRequest(null);
    } else {
      router.back();
    }
  };

  return (
    <div className="container mx-auto max-w-4xl space-y-8 py-8">
      {/* Back Button */}
      <div>
        <Link href="/meal-plans">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Meal Plans
          </Button>
        </Link>
      </div>

      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight">
          Generate Your Meal Plan
        </h1>
        <p className="mt-2 text-lg text-muted-foreground">
          {isGenerating
            ? 'Creating your personalized meal plan...'
            : 'Answer a few questions to create your personalized meal plan'}
        </p>
      </div>

      {/* Form or Generator */}
      {!isGenerating && (
        <GeneratePlanForm onSubmit={handleFormSubmit} onCancel={handleCancel} />
      )}

      {isGenerating && generationRequest && (
        <MealPlanGenerator
          request={generationRequest}
          onCancel={handleCancel}
        />
      )}
    </div>
  );
}
