# Page Structure Plan

## 1. Landing / Auth Pages
- **Route**: `/` (Landing), `/login`, `/register`
- **Purpose**: Introduction to app and user authentication.
- **Components**: Hero Section, Feature List, LoginForm, RegisterForm.
- **Data**: None (static) / User credentials.
- **Interactions**: Login, Sign up, OAuth (Google/GitHub).

## 2. Onboarding
- **Route**: `/onboarding`
- **Purpose**: Collect user goals, dietary restrictions, and initial stats.
- **Components**: Multi-step Form (Wizard), GoalSelector, DietSelector.
- **Data**: User Profile update.
- **Interactions**: Form submission, Next/Back navigation.

## 3. Dashboard (Home)
- **Route**: `/dashboard`
- **Purpose**: Overview of daily progress, upcoming meals, and quick actions.
- **Components**: NutritionSummary (Chart), DailyMealList, QuickAddButton (Voice/Camera).
- **Data**: Daily logs, User goals.
- **Interactions**: View details, Log meal, Navigate to other sections.

## 4. Meal Planner
- **Route**: `/planner`
- **Purpose**: View and generate meal plans.
- **Components**: Calendar/WeeklyView, MealSlot, GeneratePlanButton.
- **Data**: Weekly meal plan, Inventory (for suggestions).
- **Interactions**: Drag & drop meals, Regenerate plan, Lock meals.

## 5. Inventory Management
- **Route**: `/inventory`
- **Purpose**: Manage pantry and fridge items.
- **Components**: InventoryList, AddItemForm (Manual/Voice/Scan).
- **Data**: User inventory.
- **Interactions**: Add item, Remove item, Update quantity.

## 6. Cooking Mode
- **Route**: `/cooking/[recipeId]`
- **Purpose**: Step-by-step cooking assistance.
- **Components**: RecipeHeader, StepCarousel, VoiceAssistantControl.
- **Data**: Recipe details.
- **Interactions**: Voice commands ("Next step", "Repeat"), Timer toggle.

## 7. Shopping List
- **Route**: `/shopping-list`
- **Purpose**: List of ingredients needed for the meal plan.
- **Components**: ShoppingList, CheckboxItem.
- **Data**: Generated from Meal Plan - Inventory.
- **Interactions**: Check off items, Add manual items.

## 8. Profile / Settings
- **Route**: `/settings`
- **Purpose**: Update user preferences and goals.
- **Components**: ProfileForm, GoalSettings, NotificationSettings.
- **Data**: User Profile.
- **Interactions**: Save changes, Logout.
