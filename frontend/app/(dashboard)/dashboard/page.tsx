/**
 * Dashboard Page
 *
 * Main landing page with overview, quick stats, and quick actions
 */

'use client';

import { useState } from 'react';
import { Plus, Package, AlertTriangle, Calendar, ChefHat } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { useInventoryStats, useInventoryItems } from '@/lib/hooks/useInventory';
import { AddItemDialog } from '@/components/features/inventory/AddItemDialog';
import { getExpirationStatus } from '@/components/features/inventory/ExpirationBadge';
import { format } from 'date-fns';

export default function DashboardPage() {
  const [isAddItemOpen, setIsAddItemOpen] = useState(false);

  // Fetch stats
  const { data: stats, isLoading: statsLoading } = useInventoryStats();

  // Fetch expiring items
  const { data: expiringItems = [], isLoading: expiringLoading } =
    useInventoryItems({
      expiring_soon: true,
      limit: 5,
    });

  // Mock user data (replace with actual auth)
  const userName = 'Chef'; // TODO: Get from auth context

  // Mock recent activity (TODO: fetch from API)
  const recentActivity = [
    {
      id: 1,
      type: 'inventory',
      message: 'Added 3 items to inventory',
      timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
    },
    {
      id: 2,
      type: 'meal_plan',
      message: 'Generated weekly meal plan',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    },
    {
      id: 3,
      type: 'recipe',
      message: 'Saved "Grilled Chicken Salad"',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    },
  ];

  // Count expiring items by status
  const criticalItems = expiringItems.filter((item) => {
    const status = getExpirationStatus(item.expiration_date);
    return status.daysUntilExpiration !== null && status.daysUntilExpiration <= 1;
  });

  return (
    <div className="container mx-auto space-y-8 py-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight">
          Welcome back, {userName}! 👋
        </h1>
        <p className="mt-2 text-lg text-muted-foreground">
          Here's what's happening with your inventory today
        </p>
      </div>

      {/* Critical Expiring Items Alert */}
      {criticalItems.length > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Urgent: {criticalItems.length} item(s) expiring soon!</AlertTitle>
          <AlertDescription>
            {criticalItems.map((item) => item.name).join(', ')} will expire within 24 hours.
            <Link href="/inventory" className="ml-2 underline">
              View inventory
            </Link>
          </AlertDescription>
        </Alert>
      )}

      {/* Quick Stats Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Items */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-3xl font-bold">{stats?.total_items || 0}</div>
                <p className="mt-1 text-xs text-muted-foreground">
                  In your inventory
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Expiring Soon */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-3xl font-bold text-orange-600">
                  {stats?.expiring_soon || 0}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  Next 7 days
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Recipes Saved */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Recipes Saved</CardTitle>
            <ChefHat className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">12</div>
            <p className="mt-1 text-xs text-muted-foreground">
              Your collection
            </p>
          </CardContent>
        </Card>

        {/* Categories */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Categories</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {statsLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-3xl font-bold">
                  {stats?.categories_count || 0}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  Food categories
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Expiring Items */}
        <Card>
          <CardHeader>
            <CardTitle>Items Expiring Soon</CardTitle>
          </CardHeader>
          <CardContent>
            {expiringLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : expiringItems.length > 0 ? (
              <div className="space-y-3">
                {expiringItems.map((item) => {
                  const status = getExpirationStatus(item.expiration_date);
                  return (
                    <div
                      key={item.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {item.quantity} {item.unit}
                          {item.location && ` • ${item.location}`}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-orange-600">
                          {status.daysUntilExpiration === 0
                            ? 'Today'
                            : status.daysUntilExpiration === 1
                            ? 'Tomorrow'
                            : `${status.daysUntilExpiration}d left`}
                        </p>
                        {item.expiration_date && (
                          <p className="text-xs text-muted-foreground">
                            {format(new Date(item.expiration_date), 'MMM d')}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
                <Link href="/inventory">
                  <Button variant="outline" className="w-full">
                    View All Items
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No items expiring soon. Great job! 🎉
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                    {activity.type === 'inventory' && (
                      <Package className="h-4 w-4 text-primary" />
                    )}
                    {activity.type === 'meal_plan' && (
                      <Calendar className="h-4 w-4 text-primary" />
                    )}
                    {activity.type === 'recipe' && (
                      <ChefHat className="h-4 w-4 text-primary" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">
                      {format(activity.timestamp, 'PPp')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Button
              variant="outline"
              className="h-auto flex-col gap-2 py-6"
              onClick={() => setIsAddItemOpen(true)}
            >
              <Plus className="h-6 w-6" />
              <span>Add Item</span>
            </Button>

            <Link href="/meal-plans">
              <Button
                variant="outline"
                className="h-auto w-full flex-col gap-2 py-6"
              >
                <Calendar className="h-6 w-6" />
                <span>Generate Meal Plan</span>
              </Button>
            </Link>

            <Link href="/recipes">
              <Button
                variant="outline"
                className="h-auto w-full flex-col gap-2 py-6"
              >
                <ChefHat className="h-6 w-6" />
                <span>Browse Recipes</span>
              </Button>
            </Link>

            <Link href="/shopping">
              <Button
                variant="outline"
                className="h-auto w-full flex-col gap-2 py-6"
              >
                <Package className="h-6 w-6" />
                <span>Shopping List</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Add Item Dialog */}
      <AddItemDialog open={isAddItemOpen} onOpenChange={setIsAddItemOpen} />
    </div>
  );
}
