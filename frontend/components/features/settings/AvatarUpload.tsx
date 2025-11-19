/**
 * AvatarUpload Component
 *
 * Avatar image upload with drag-and-drop, preview, and cropping
 */

'use client';

import { useState, useRef, DragEvent } from 'react';
import Image from 'next/image';
import { Upload, X, Loader2, User, Camera } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useUploadAvatar, useDeleteAvatar } from '@/lib/hooks/useUser';
import { cn } from '@/lib/utils';

interface AvatarUploadProps {
  currentAvatarUrl?: string;
  userName?: string;
  onUploadSuccess?: (url: string) => void;
}

export function AvatarUpload({
  currentAvatarUrl,
  userName,
  onUploadSuccess,
}: AvatarUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadMutation = useUploadAvatar();
  const deleteMutation = useDeleteAvatar();

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file: File) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size must be less than 5MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result as string);
      setSelectedFile(file);
      setIsPreviewOpen(true);
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      const result = await uploadMutation.mutateAsync(selectedFile);
      setIsPreviewOpen(false);
      setPreviewUrl(null);
      setSelectedFile(null);
      onUploadSuccess?.(result.avatar_url);
    } catch (error) {
      console.error('Failed to upload avatar:', error);
      alert('Failed to upload avatar. Please try again.');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to remove your avatar?')) return;

    try {
      await deleteMutation.mutateAsync();
    } catch (error) {
      console.error('Failed to delete avatar:', error);
      alert('Failed to delete avatar. Please try again.');
    }
  };

  const handleCancelPreview = () => {
    setIsPreviewOpen(false);
    setPreviewUrl(null);
    setSelectedFile(null);
  };

  return (
    <>
      <div className="flex items-center gap-6">
        {/* Current Avatar Display */}
        <div className="relative h-32 w-32 overflow-hidden rounded-full border-4 border-border bg-muted">
          {currentAvatarUrl ? (
            <Image
              src={currentAvatarUrl}
              alt={userName || 'User avatar'}
              fill
              className="object-cover"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center">
              <User className="h-16 w-16 text-muted-foreground" />
            </div>
          )}

          {/* Camera overlay button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity hover:opacity-100"
          >
            <Camera className="h-8 w-8 text-white" />
          </button>
        </div>

        {/* Upload Area */}
        <div className="flex-1">
          <Card
            className={cn(
              'border-2 border-dashed transition-colors',
              isDragging && 'border-primary bg-primary/5'
            )}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <CardContent className="p-6">
              <div className="flex flex-col items-center gap-4">
                <Upload
                  className={cn(
                    'h-8 w-8 text-muted-foreground',
                    isDragging && 'text-primary'
                  )}
                />

                <div className="text-center">
                  <p className="font-medium">
                    Drag and drop your photo here, or{' '}
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="text-primary hover:underline"
                    >
                      browse
                    </button>
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Supports: JPG, PNG, GIF (max 5MB)
                  </p>
                </div>

                {currentAvatarUrl && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDelete}
                    disabled={deleteMutation.isPending}
                  >
                    {deleteMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Removing...
                      </>
                    ) : (
                      <>
                        <X className="mr-2 h-4 w-4" />
                        Remove Avatar
                      </>
                    )}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileInputChange}
            className="hidden"
          />
        </div>
      </div>

      {/* Preview and Crop Dialog */}
      <Dialog open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Preview Avatar</DialogTitle>
            <DialogDescription>
              Review your new profile picture before uploading
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            {previewUrl && (
              <div className="flex flex-col items-center gap-4">
                {/* Large Preview */}
                <div className="relative h-64 w-64 overflow-hidden rounded-lg border">
                  <Image
                    src={previewUrl}
                    alt="Avatar preview"
                    fill
                    className="object-cover"
                  />
                </div>

                {/* Small Preview */}
                <div className="flex items-center gap-4">
                  <div>
                    <p className="mb-2 text-center text-xs text-muted-foreground">
                      How it will look:
                    </p>
                    <div className="relative h-16 w-16 overflow-hidden rounded-full border-2">
                      <Image
                        src={previewUrl}
                        alt="Small preview"
                        fill
                        className="object-cover"
                      />
                    </div>
                  </div>
                </div>

                {selectedFile && (
                  <div className="text-sm text-muted-foreground">
                    <p>
                      <strong>File:</strong> {selectedFile.name}
                    </p>
                    <p>
                      <strong>Size:</strong>{' '}
                      {(selectedFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={handleCancelPreview}>
              Cancel
            </Button>
            <Button onClick={handleUpload} disabled={uploadMutation.isPending}>
              {uploadMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                'Upload Avatar'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
