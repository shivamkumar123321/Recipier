/**
 * GeneratePlanForm Component
 *
 * Multi-step form for meal plan generation
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { format, addDays } from 'date-fns';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Target,
  Leaf,
  Package,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useInventoryStats } from '@/lib/hooks/useInventory';
import { CreateMealPlanRequest } from '@/lib/api/meal-plans';

const formSchema = z.object({
  total_days: z.number().min(1).max(30),
  goal: z.enum(['weight_loss', 'maintenance', 'muscle_gain']),
  dietary_preferences: z.array(z.string()),
  servings: z.number().min(1).max(10),
  use_inventory: z.boolean(),
  cuisine_preferences: z.array(z.string()).optional(),
});

type FormValues = z.infer<typeof formSchema>;

interface GeneratePlanFormProps {
  onSubmit: (data: CreateMealPlanRequest) => void;
  onCancel?: () => void;
}

const DIETARY_OPTIONS = [
  { value: 'vegetarian', label: 'Vegetarian', icon: '🥗' },
  { value: 'vegan', label: 'Vegan', icon: '🌱' },
  { value: 'pescatarian', label: 'Pescatarian', icon: '🐟' },
  { value: 'gluten_free', label: 'Gluten-Free', icon: '🌾' },
  { value: 'dairy_free', label: 'Dairy-Free', icon: '🥛' },
  { value: 'keto', label: 'Keto', icon: '🥑' },
  { value: 'paleo', label: 'Paleo', icon: '🥩' },
  { value: 'low_carb', label: 'Low Carb', icon: '🥦' },
];

const CUISINE_OPTIONS = [
  { value: 'italian', label: 'Italian', icon: '🍝' },
  { value: 'mexican', label: 'Mexican', icon: '🌮' },
  { value: 'asian', label: 'Asian', icon: '🍜' },
  { value: 'mediterranean', label: 'Mediterranean', icon: '🫒' },
  { value: 'american', label: 'American', icon: '🍔' },
  { value: 'indian', label: 'Indian', icon: '🍛' },
];

export function GeneratePlanForm({
  onSubmit,
  onCancel,
}: GeneratePlanFormProps) {
  const [step, setStep] = useState(1);
  const { data: inventoryStats } = useInventoryStats();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      total_days: 7,
      goal: 'maintenance',
      dietary_preferences: [],
      servings: 2,
      use_inventory: true,
      cuisine_preferences: [],
    },
  });

  const handleSubmit = (values: FormValues) => {
    const startDate = new Date();
    const endDate = addDays(startDate, values.total_days);

    const request: CreateMealPlanRequest = {
      name: `${values.total_days}-Day ${values.goal.replace('_', ' ')} Plan`,
      start_date: format(startDate, 'yyyy-MM-dd'),
      end_date: format(endDate, 'yyyy-MM-dd'),
      total_days: values.total_days,
      goal: values.goal,
      dietary_preferences: values.dietary_preferences,
      servings: values.servings,
      cuisine_preferences: values.cuisine_preferences,
      use_inventory: values.use_inventory,
    };

    onSubmit(request);
  };

  const nextStep = () => {
    if (step < 4) setStep(step + 1);
  };

  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  const canProceed = () => {
    if (step === 1) return form.watch('total_days') > 0;
    if (step === 2) return true; // Dietary preferences optional
    if (step === 3) return form.watch('goal') !== undefined;
    return true;
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        {/* Progress Indicator */}
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
                  s === step
                    ? 'border-primary bg-primary text-primary-foreground'
                    : s < step
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-muted-foreground/20 text-muted-foreground'
                }`}
              >
                {s}
              </div>
              {s < 4 && (
                <div
                  className={`mx-2 h-0.5 w-12 ${
                    s < step ? 'bg-primary' : 'bg-muted-foreground/20'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Duration */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Choose Duration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FormField
                control={form.control}
                name="total_days"
                render={({ field }) => (
                  <FormItem className="space-y-3">
                    <FormLabel>How many days?</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={(value) =>
                          field.onChange(parseInt(value))
                        }
                        value={field.value.toString()}
                        className="grid gap-4 sm:grid-cols-2"
                      >
                        <div>
                          <RadioGroupItem
                            value="3"
                            id="3-days"
                            className="peer sr-only"
                          />
                          <label
                            htmlFor="3-days"
                            className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-muted p-6 hover:border-primary peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                          >
                            <span className="text-2xl font-bold">3 Days</span>
                            <span className="text-sm text-muted-foreground">
                              Quick start
                            </span>
                          </label>
                        </div>

                        <div>
                          <RadioGroupItem
                            value="7"
                            id="7-days"
                            className="peer sr-only"
                          />
                          <label
                            htmlFor="7-days"
                            className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-muted p-6 hover:border-primary peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                          >
                            <span className="text-2xl font-bold">7 Days</span>
                            <span className="text-sm text-muted-foreground">
                              Full week
                            </span>
                            <Badge variant="secondary" className="mt-2">
                              Recommended
                            </Badge>
                          </label>
                        </div>
                      </RadioGroup>
                    </FormControl>
                    <FormDescription>
                      Choose the duration for your meal plan
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="servings"
                render={({ field }) => (
                  <FormItem className="mt-6">
                    <FormLabel>Servings per meal</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={(value) =>
                          field.onChange(parseInt(value))
                        }
                        value={field.value.toString()}
                        className="flex gap-2"
                      >
                        {[1, 2, 4].map((num) => (
                          <div key={num}>
                            <RadioGroupItem
                              value={num.toString()}
                              id={`servings-${num}`}
                              className="peer sr-only"
                            />
                            <label
                              htmlFor={`servings-${num}`}
                              className="flex cursor-pointer items-center justify-center rounded-md border-2 border-muted px-6 py-3 hover:border-primary peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                            >
                              {num}
                            </label>
                          </div>
                        ))}
                      </RadioGroup>
                    </FormControl>
                    <FormDescription>
                      Number of people you're cooking for
                    </FormDescription>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        )}

        {/* Step 2: Dietary Preferences */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Leaf className="h-5 w-5" />
                Dietary Preferences
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FormField
                control={form.control}
                name="dietary_preferences"
                render={() => (
                  <FormItem>
                    <div className="mb-4">
                      <FormLabel>Select all that apply</FormLabel>
                      <FormDescription>
                        We'll customize your meal plan based on these
                        preferences
                      </FormDescription>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-2">
                      {DIETARY_OPTIONS.map((option) => (
                        <FormField
                          key={option.value}
                          control={form.control}
                          name="dietary_preferences"
                          render={({ field }) => (
                            <FormItem className="flex items-start space-x-3 space-y-0">
                              <FormControl>
                                <Checkbox
                                  checked={field.value?.includes(option.value)}
                                  onCheckedChange={(checked) => {
                                    return checked
                                      ? field.onChange([
                                          ...field.value,
                                          option.value,
                                        ])
                                      : field.onChange(
                                          field.value?.filter(
                                            (value) => value !== option.value
                                          )
                                        );
                                  }}
                                />
                              </FormControl>
                              <FormLabel className="cursor-pointer font-normal">
                                <span className="mr-2">{option.icon}</span>
                                {option.label}
                              </FormLabel>
                            </FormItem>
                          )}
                        />
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="cuisine_preferences"
                render={() => (
                  <FormItem className="mt-6">
                    <FormLabel>Favorite Cuisines (Optional)</FormLabel>
                    <FormDescription>
                      Select cuisines you'd like to explore
                    </FormDescription>
                    <div className="mt-2 grid gap-3 sm:grid-cols-3">
                      {CUISINE_OPTIONS.map((option) => (
                        <FormField
                          key={option.value}
                          control={form.control}
                          name="cuisine_preferences"
                          render={({ field }) => (
                            <FormItem className="flex items-start space-x-3 space-y-0">
                              <FormControl>
                                <Checkbox
                                  checked={field.value?.includes(option.value)}
                                  onCheckedChange={(checked) => {
                                    return checked
                                      ? field.onChange([
                                          ...(field.value || []),
                                          option.value,
                                        ])
                                      : field.onChange(
                                          field.value?.filter(
                                            (value) => value !== option.value
                                          )
                                        );
                                  }}
                                />
                              </FormControl>
                              <FormLabel className="cursor-pointer font-normal">
                                <span className="mr-2">{option.icon}</span>
                                {option.label}
                              </FormLabel>
                            </FormItem>
                          )}
                        />
                      ))}
                    </div>
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        )}

        {/* Step 3: Goals */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Set Your Goal
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FormField
                control={form.control}
                name="goal"
                render={({ field }) => (
                  <FormItem className="space-y-3">
                    <FormLabel>What's your primary goal?</FormLabel>
                    <FormControl>
                      <RadioGroup
                        onValueChange={field.onChange}
                        value={field.value}
                        className="grid gap-4"
                      >
                        <div>
                          <RadioGroupItem
                            value="weight_loss"
                            id="weight-loss"
                            className="peer sr-only"
                          />
                          <label
                            htmlFor="weight-loss"
                            className="flex cursor-pointer items-start gap-4 rounded-lg border-2 border-muted p-4 hover:border-primary peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                          >
                            <div className="flex-1">
                              <p className="font-semibold">Weight Loss</p>
                              <p className="text-sm text-muted-foreground">
                                Lower calorie meals to help you lose weight
                                sustainably
                              </p>
                            </div>
                          </label>
                        </div>

                        <div>
                          <RadioGroupItem
                            value="maintenance"
                            id="maintenance"
                            className="peer sr-only"
                          />
                          <label
                            htmlFor="maintenance"
                            className="flex cursor-pointer items-start gap-4 rounded-lg border-2 border-muted p-4 hover:border-primary peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                          >
                            <div className="flex-1">
                              <p className="font-semibold">Maintenance</p>
                              <p className="text-sm text-muted-foreground">
                                Balanced meals to maintain your current weight
                              </p>
                            </div>
                          </label>
                        </div>

                        <div>
                          <RadioGroupItem
                            value="muscle_gain"
                            id="muscle-gain"
                            className="peer sr-only"
                          />
                          <label
                            htmlFor="muscle-gain"
                            className="flex cursor-pointer items-start gap-4 rounded-lg border-2 border-muted p-4 hover:border-primary peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
                          >
                            <div className="flex-1">
                              <p className="font-semibold">Muscle Gain</p>
                              <p className="text-sm text-muted-foreground">
                                Higher protein, higher calorie meals for muscle
                                building
                              </p>
                            </div>
                          </label>
                        </div>
                      </RadioGroup>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>
        )}

        {/* Step 4: Review Inventory */}
        {step === 4 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Use Your Inventory
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <FormField
                control={form.control}
                name="use_inventory"
                render={({ field }) => (
                  <FormItem className="flex items-start space-x-3 space-y-0 rounded-lg border p-4">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="flex-1">
                      <FormLabel className="font-semibold">
                        Use items from my inventory
                      </FormLabel>
                      <FormDescription>
                        We'll prioritize recipes that use ingredients you already
                        have
                      </FormDescription>
                    </div>
                  </FormItem>
                )}
              />

              {inventoryStats && (
                <div className="rounded-lg bg-muted/50 p-4">
                  <h4 className="mb-3 font-medium">Your Current Inventory</h4>
                  <div className="grid gap-3 sm:grid-cols-3">
                    <div className="text-center">
                      <p className="text-2xl font-bold">
                        {inventoryStats.total_items}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Total Items
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold">
                        {inventoryStats.categories_count}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Categories
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-orange-600">
                        {inventoryStats.expiring_soon}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Expiring Soon
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Summary */}
              <div className="rounded-lg border-2 border-primary/20 bg-primary/5 p-4">
                <h4 className="mb-3 flex items-center gap-2 font-semibold">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Ready to Generate
                </h4>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-medium">Duration:</span>{' '}
                    {form.watch('total_days')} days
                  </p>
                  <p>
                    <span className="font-medium">Goal:</span>{' '}
                    {form.watch('goal')?.replace('_', ' ')}
                  </p>
                  <p>
                    <span className="font-medium">Servings:</span>{' '}
                    {form.watch('servings')} per meal
                  </p>
                  {form.watch('dietary_preferences').length > 0 && (
                    <p>
                      <span className="font-medium">Dietary:</span>{' '}
                      {form.watch('dietary_preferences').join(', ')}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <div>
            {step > 1 && (
              <Button type="button" variant="outline" onClick={prevStep}>
                <ChevronLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
            )}
            {step === 1 && onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            {step < 4 ? (
              <Button
                type="button"
                onClick={nextStep}
                disabled={!canProceed()}
              >
                Next
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button type="submit" disabled={!canProceed()}>
                <Sparkles className="mr-2 h-4 w-4" />
                Generate Meal Plan
              </Button>
            )}
          </div>
        </div>
      </form>
    </Form>
  );
}
