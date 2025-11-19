/**
 * Settings Page
 *
 * User settings with tabs for profile, preferences, goals, notifications, and account
 */

'use client';

import { useState } from 'react';
import { User, Apple, Target, Bell, Shield } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProfileForm } from '@/components/features/settings/ProfileForm';
import { DietaryPreferencesForm } from '@/components/features/settings/DietaryPreferencesForm';
import { GoalsForm } from '@/components/features/settings/GoalsForm';
import { NotificationSettings } from '@/components/features/settings/NotificationSettings';
import { AccountSettings } from '@/components/features/settings/AccountSettings';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="container mx-auto max-w-5xl space-y-8 py-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            <span className="hidden sm:inline">Profile</span>
          </TabsTrigger>
          <TabsTrigger value="dietary" className="flex items-center gap-2">
            <Apple className="h-4 w-4" />
            <span className="hidden sm:inline">Dietary</span>
          </TabsTrigger>
          <TabsTrigger value="goals" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            <span className="hidden sm:inline">Goals</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            <span className="hidden sm:inline">Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="account" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            <span className="hidden sm:inline">Account</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <ProfileForm />
        </TabsContent>

        <TabsContent value="dietary">
          <DietaryPreferencesForm />
        </TabsContent>

        <TabsContent value="goals">
          <GoalsForm />
        </TabsContent>

        <TabsContent value="notifications">
          <NotificationSettings />
        </TabsContent>

        <TabsContent value="account">
          <AccountSettings />
        </TabsContent>
      </Tabs>
    </div>
  );
}
