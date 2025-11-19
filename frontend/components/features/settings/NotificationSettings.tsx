/**
 * NotificationSettings Component
 *
 * Manage email and push notification preferences
 */

'use client';

import { useState, useEffect } from 'react';
import { Loader2, Save, Mail, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useNotificationSettings, useUpdateNotificationSettings } from '@/lib/hooks/useUser';

export function NotificationSettings() {
  const { data: settings } = useNotificationSettings();
  const updateMutation = useUpdateNotificationSettings();

  const [emailMealReminders, setEmailMealReminders] = useState(false);
  const [emailGroceryLists, setEmailGroceryLists] = useState(false);
  const [emailWeeklySummary, setEmailWeeklySummary] = useState(false);
  const [emailRecipeSuggestions, setEmailRecipeSuggestions] = useState(false);
  const [pushMealReminders, setPushMealReminders] = useState(false);
  const [pushTimerAlerts, setPushTimerAlerts] = useState(false);
  const [pushGroceryReminders, setPushGroceryReminders] = useState(false);

  useEffect(() => {
    if (settings) {
      setEmailMealReminders(settings.email_meal_reminders);
      setEmailGroceryLists(settings.email_grocery_lists);
      setEmailWeeklySummary(settings.email_weekly_summary);
      setEmailRecipeSuggestions(settings.email_recipe_suggestions);
      setPushMealReminders(settings.push_meal_reminders);
      setPushTimerAlerts(settings.push_timer_alerts);
      setPushGroceryReminders(settings.push_grocery_reminders);
    }
  }, [settings]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await updateMutation.mutateAsync({
        email_meal_reminders: emailMealReminders,
        email_grocery_lists: emailGroceryLists,
        email_weekly_summary: emailWeeklySummary,
        email_recipe_suggestions: emailRecipeSuggestions,
        push_meal_reminders: pushMealReminders,
        push_timer_alerts: pushTimerAlerts,
        push_grocery_reminders: pushGroceryReminders,
      });

      alert('Notification settings updated successfully!');
    } catch (error) {
      console.error('Failed to update settings:', error);
      alert('Failed to update settings. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Email Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Email Notifications
          </CardTitle>
          <CardDescription>
            Choose which emails you'd like to receive
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Meal Reminders</Label>
              <p className="text-sm text-muted-foreground">
                Get reminded about upcoming meals
              </p>
            </div>
            <Switch
              checked={emailMealReminders}
              onCheckedChange={setEmailMealReminders}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Grocery Lists</Label>
              <p className="text-sm text-muted-foreground">
                Updates when grocery lists are generated
              </p>
            </div>
            <Switch
              checked={emailGroceryLists}
              onCheckedChange={setEmailGroceryLists}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Weekly Summary</Label>
              <p className="text-sm text-muted-foreground">
                Weekly nutrition and progress reports
              </p>
            </div>
            <Switch
              checked={emailWeeklySummary}
              onCheckedChange={setEmailWeeklySummary}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Recipe Suggestions</Label>
              <p className="text-sm text-muted-foreground">
                Personalized recipe recommendations
              </p>
            </div>
            <Switch
              checked={emailRecipeSuggestions}
              onCheckedChange={setEmailRecipeSuggestions}
            />
          </div>
        </CardContent>
      </Card>

      {/* Push Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Push Notifications
          </CardTitle>
          <CardDescription>
            Manage browser and mobile push notifications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Meal Reminders</Label>
              <p className="text-sm text-muted-foreground">
                Push notifications for meal times
              </p>
            </div>
            <Switch
              checked={pushMealReminders}
              onCheckedChange={setPushMealReminders}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Timer Alerts</Label>
              <p className="text-sm text-muted-foreground">
                Cooking timer completion alerts
              </p>
            </div>
            <Switch
              checked={pushTimerAlerts}
              onCheckedChange={setPushTimerAlerts}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Grocery Reminders</Label>
              <p className="text-sm text-muted-foreground">
                Reminders to complete grocery shopping
              </p>
            </div>
            <Switch
              checked={pushGroceryReminders}
              onCheckedChange={setPushGroceryReminders}
            />
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-end">
        <Button type="submit" size="lg" disabled={updateMutation.isPending}>
          {updateMutation.isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              Save Settings
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
