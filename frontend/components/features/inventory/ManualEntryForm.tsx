/**
 * ManualEntryForm Component
 *
 * Form for manually entering inventory items
 */

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
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
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import {
  useCreateInventoryItem,
  useFoodCategories,
} from '@/lib/hooks/useInventory';

const formSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  quantity: z.coerce.number().positive('Quantity must be greater than 0'),
  unit: z.string().min(1, 'Unit is required'),
  category_id: z.coerce.number().positive('Category is required'),
  expiration_date: z.string().optional(),
  purchase_date: z.string().optional(),
  location: z.string().max(100).optional(),
  notes: z.string().max(500).optional(),
});

type FormValues = z.infer<typeof formSchema>;

interface ManualEntryFormProps {
  onSuccess?: () => void;
}

const COMMON_UNITS = [
  'piece',
  'pieces',
  'lb',
  'lbs',
  'oz',
  'kg',
  'g',
  'cup',
  'cups',
  'tbsp',
  'tsp',
  'ml',
  'L',
  'gallon',
  'quart',
  'pint',
  'can',
  'jar',
  'box',
  'bag',
  'package',
];

export function ManualEntryForm({ onSuccess }: ManualEntryFormProps) {
  const [customUnit, setCustomUnit] = useState(false);
  const { data: categories = [], isLoading: categoriesLoading } =
    useFoodCategories();
  const createItem = useCreateInventoryItem();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      quantity: 1,
      unit: 'piece',
      location: '',
      notes: '',
    },
  });

  const onSubmit = async (values: FormValues) => {
    try {
      await createItem.mutateAsync({
        ...values,
        expiration_date: values.expiration_date || undefined,
        purchase_date: values.purchase_date || undefined,
      });
      form.reset();
      onSuccess?.();
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Name */}
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Item Name *</FormLabel>
              <FormControl>
                <Input placeholder="e.g., Organic Milk" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Quantity and Unit */}
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="quantity"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Quantity *</FormLabel>
                <FormControl>
                  <Input type="number" step="0.01" min="0" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="unit"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Unit *</FormLabel>
                <FormControl>
                  {customUnit ? (
                    <div className="flex gap-2">
                      <Input placeholder="Custom unit" {...field} />
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setCustomUnit(false);
                          field.onChange('piece');
                        }}
                      >
                        ←
                      </Button>
                    </div>
                  ) : (
                    <Select value={field.value} onValueChange={field.onChange}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {COMMON_UNITS.map((unit) => (
                          <SelectItem key={unit} value={unit}>
                            {unit}
                          </SelectItem>
                        ))}
                        <SelectItem
                          value="custom"
                          onSelect={() => setCustomUnit(true)}
                        >
                          + Custom unit
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Category */}
        <FormField
          control={form.control}
          name="category_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Category *</FormLabel>
              <FormControl>
                <Select
                  value={field.value?.toString()}
                  onValueChange={(value) => field.onChange(parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem
                        key={category.id}
                        value={category.id.toString()}
                      >
                        {category.icon && `${category.icon} `}
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Dates */}
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="expiration_date"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Expiration Date</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormDescription>Optional</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="purchase_date"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Purchase Date</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormDescription>Optional</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Location */}
        <FormField
          control={form.control}
          name="location"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Location</FormLabel>
              <FormControl>
                <Input
                  placeholder="e.g., Refrigerator, Pantry"
                  {...field}
                  value={field.value || ''}
                />
              </FormControl>
              <FormDescription>Where is this item stored?</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Notes */}
        <FormField
          control={form.control}
          name="notes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Notes</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Any additional notes..."
                  className="resize-none"
                  {...field}
                  value={field.value || ''}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Submit Button */}
        <div className="flex justify-end gap-2 pt-4">
          <Button
            type="submit"
            disabled={createItem.isPending || categoriesLoading}
          >
            {createItem.isPending ? 'Adding...' : 'Add Item'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
