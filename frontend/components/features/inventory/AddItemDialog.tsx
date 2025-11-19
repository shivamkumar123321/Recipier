/**
 * AddItemDialog Component
 *
 * Modal dialog for adding inventory items with three input methods:
 * 1. Manual entry
 * 2. Voice input
 * 3. Camera scan
 */

'use client';

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ManualEntryForm } from './ManualEntryForm';
import { VoiceInputTab } from './VoiceInputTab';
import { CameraScanTab } from './CameraScanTab';

interface AddItemDialogProps {
  trigger?: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function AddItemDialog({
  trigger,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
}: AddItemDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('manual');

  // Use controlled or internal state
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen =
    controlledOnOpenChange !== undefined
      ? controlledOnOpenChange
      : setInternalOpen;

  const handleSuccess = () => {
    setOpen(false);
    setActiveTab('manual'); // Reset to manual tab
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Item
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add to Inventory</DialogTitle>
          <DialogDescription>
            Add items manually, by voice, or by scanning with your camera
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="manual">✍️ Manual</TabsTrigger>
            <TabsTrigger value="voice">🎤 Voice</TabsTrigger>
            <TabsTrigger value="camera">📷 Camera</TabsTrigger>
          </TabsList>

          <TabsContent value="manual" className="mt-6">
            <ManualEntryForm onSuccess={handleSuccess} />
          </TabsContent>

          <TabsContent value="voice" className="mt-6">
            <VoiceInputTab onSuccess={handleSuccess} />
          </TabsContent>

          <TabsContent value="camera" className="mt-6">
            <CameraScanTab onSuccess={handleSuccess} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
