/**
 * CameraScanTab Component
 *
 * Camera scanning for adding inventory items
 * Supports both camera capture and file upload
 */

'use client';

import { useState, useRef } from 'react';
import { Camera, Upload, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  useParseImageInput,
  useBulkCreateInventoryItems,
  useFoodCategories,
} from '@/lib/hooks/useInventory';
import { ParsedInventoryItem } from '@/lib/api/inventory';
import { ParsedItemsList } from './ParsedItemsList';
import Image from 'next/image';

interface CameraScanTabProps {
  onSuccess?: () => void;
}

export function CameraScanTab({ onSuccess }: CameraScanTabProps) {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [parsedItems, setParsedItems] = useState<ParsedInventoryItem[]>([]);
  const [error, setError] = useState<string>('');

  const fileInputRef = useRef<HTMLInputElement>(null);

  const parseImage = useParseImageInput();
  const bulkCreate = useBulkCreateInventoryItems();
  const { data: categories = [] } = useFoodCategories();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Image size must be less than 10MB');
      return;
    }

    setError('');
    setSelectedImage(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Automatically process the image
    processImage(file);
  };

  const processImage = async (file: File) => {
    try {
      const result = await parseImage.mutateAsync(file);
      setParsedItems(result.items);
    } catch (err) {
      setError('Failed to process image. Please try again.');
    }
  };

  const handleAddItems = async () => {
    if (parsedItems.length === 0) return;

    try {
      // Map parsed items to create requests with category IDs
      const itemsToCreate = parsedItems.map((item) => {
        // Find category by name or use first category as default
        const category = categories.find(
          (cat) =>
            cat.name.toLowerCase() === item.category?.toLowerCase()
        ) || categories[0];

        return {
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          category_id: category?.id || 1,
          expiration_date: item.expiration_date,
        };
      });

      await bulkCreate.mutateAsync(itemsToCreate);

      // Reset state
      handleReset();

      onSuccess?.();
    } catch (err) {
      setError('Failed to add items. Please try again.');
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setImagePreview('');
    setParsedItems([]);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-6">
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
        capture="environment" // Use rear camera on mobile
      />

      {/* Instructions */}
      {!selectedImage && !parseImage.isPending && (
        <Alert>
          <AlertDescription>
            Take a photo of your food items or upload an image. Our AI will
            identify the items and quantities.
          </AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Image Upload Interface */}
      {!selectedImage ? (
        <div className="flex flex-col gap-3">
          <Button
            size="lg"
            className="h-24 w-full"
            onClick={triggerFileInput}
            disabled={parseImage.isPending}
          >
            <Camera className="mr-2 h-6 w-6" />
            Take Photo
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="h-24 w-full"
            onClick={triggerFileInput}
            disabled={parseImage.isPending}
          >
            <Upload className="mr-2 h-6 w-6" />
            Upload Image
          </Button>
        </div>
      ) : (
        <>
          {/* Image Preview */}
          <div className="relative overflow-hidden rounded-lg border">
            <div className="relative aspect-video w-full">
              <Image
                src={imagePreview}
                alt="Selected image"
                fill
                className="object-contain"
              />
            </div>
            <Button
              size="sm"
              variant="destructive"
              className="absolute right-2 top-2"
              onClick={handleReset}
            >
              <X className="mr-1 h-4 w-4" />
              Remove
            </Button>
          </div>
        </>
      )}

      {/* Processing State */}
      {parseImage.isPending && (
        <div className="flex items-center justify-center gap-2 py-8">
          <Loader2 className="h-5 w-5 animate-spin" />
          <p className="text-sm text-muted-foreground">
            Analyzing image...
          </p>
        </div>
      )}

      {/* Parsed Items */}
      {parsedItems.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-medium">Detected Items:</h4>
          <ParsedItemsList
            items={parsedItems}
            categories={categories}
            onUpdate={setParsedItems}
          />

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={handleReset}>
              Cancel
            </Button>
            <Button onClick={handleAddItems} disabled={bulkCreate.isPending}>
              {bulkCreate.isPending
                ? 'Adding...'
                : `Add ${parsedItems.length} Item(s)`}
            </Button>
          </div>
        </div>
      )}

      {/* No Items Detected */}
      {selectedImage && !parseImage.isPending && parsedItems.length === 0 && (
        <Alert>
          <AlertDescription>
            No food items detected in the image. Please try another image or add
            items manually.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
