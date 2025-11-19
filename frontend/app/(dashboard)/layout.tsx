/**
 * Dashboard Layout
 *
 * Layout for authenticated pages with header and navigation
 */

import { ReactNode } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Package, Calendar, ChefHat, ShoppingCart, BarChart3, User } from 'lucide-react';

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <ChefHat className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">Weight Coach</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              href="/dashboard"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Dashboard
            </Link>
            <Link
              href="/inventory"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Inventory
            </Link>
            <Link
              href="/meals"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Meals
            </Link>
            <Link
              href="/recipes"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Recipes
            </Link>
            <Link
              href="/meal-plans"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Meal Plans
            </Link>
            <Link
              href="/shopping"
              className="text-sm font-medium transition-colors hover:text-primary"
            >
              Shopping
            </Link>
          </nav>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <Link href="/profile">
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">{children}</main>

      {/* Mobile Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background md:hidden">
        <div className="grid grid-cols-5 gap-1 p-2">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="h-auto flex-col gap-1 py-2">
              <BarChart3 className="h-5 w-5" />
              <span className="text-xs">Home</span>
            </Button>
          </Link>
          <Link href="/inventory">
            <Button variant="ghost" size="sm" className="h-auto flex-col gap-1 py-2">
              <Package className="h-5 w-5" />
              <span className="text-xs">Inventory</span>
            </Button>
          </Link>
          <Link href="/meal-plans">
            <Button variant="ghost" size="sm" className="h-auto flex-col gap-1 py-2">
              <Calendar className="h-5 w-5" />
              <span className="text-xs">Plans</span>
            </Button>
          </Link>
          <Link href="/recipes">
            <Button variant="ghost" size="sm" className="h-auto flex-col gap-1 py-2">
              <ChefHat className="h-5 w-5" />
              <span className="text-xs">Recipes</span>
            </Button>
          </Link>
          <Link href="/shopping">
            <Button variant="ghost" size="sm" className="h-auto flex-col gap-1 py-2">
              <ShoppingCart className="h-5 w-5" />
              <span className="text-xs">Shopping</span>
            </Button>
          </Link>
        </div>
      </nav>

      {/* Spacer for mobile navigation */}
      <div className="h-20 md:hidden" />
    </div>
  );
}
