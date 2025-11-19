# Page Structure Plan - Weight Coach

> **Complete routing and page structure for the Weight Coach application**
> Last Updated: 2025-11-18

## Table of Contents
1. [Route Structure](#route-structure)
2. [Public Pages](#public-pages)
3. [Authenticated Pages](#authenticated-pages)
4. [API Routes](#api-routes)

---

## Route Structure

```
/                           # Landing/Home page (public)
/auth
  /login                    # Login page
  /signup                   # Registration page
  /forgot-password          # Password reset request
  /reset-password           # Password reset form

/dashboard                  # Main dashboard (authenticated)
/inventory                  # Inventory management
/meals                      # Meal logging and history
/recipes                    # Recipe browser and saved recipes
/meal-plans                 # Meal planning
/shopping                   # Shopping lists
/profile                    # User profile and settings
/goals                      # Health goals management
```

---

## Public Pages

### Landing Page (`/`)

**Purpose:** Marketing page to showcase features and drive sign-ups

**Key Components:**
- Hero section with value proposition
- Feature highlights (Voice input, AI coaching, meal planning)
- Screenshot showcase
- CTA buttons (Sign up, Learn more)
- Footer with links

**Data Needs:**
- None (static content)

**User Interactions:**
- Click "Sign Up" → Navigate to `/auth/signup`
- Click "Login" → Navigate to `/auth/login`
- Scroll to view features

---

### Login Page (`/auth/login`)

**Purpose:** User authentication

**Key Components:**
- Login form (email, password)
- "Remember me" checkbox
- "Forgot password?" link
- Social login buttons (optional)
- Link to sign up

**Data Needs:**
- None (form submission only)

**User Interactions:**
- Submit credentials → API call → Redirect to `/dashboard`
- Click "Forgot password" → Navigate to `/auth/forgot-password`
- Click "Sign up" → Navigate to `/auth/signup`

---

### Sign Up Page (`/auth/signup`)

**Purpose:** New user registration

**Key Components:**
- Registration form (name, email, password, confirm password)
- Terms acceptance checkbox
- Social sign-up buttons (optional)
- Link to login

**Data Needs:**
- None (form submission only)

**User Interactions:**
- Submit form → API call → Navigate to onboarding or `/dashboard`
- Click "Login" → Navigate to `/auth/login`

---

### Forgot Password Page (`/auth/forgot-password`)

**Purpose:** Request password reset email

**Key Components:**
- Email input form
- Submit button
- Back to login link

**Data Needs:**
- None (form submission only)

**User Interactions:**
- Submit email → API call → Show success message
- Click "Back to login" → Navigate to `/auth/login`

---

### Reset Password Page (`/auth/reset-password?token=xxx`)

**Purpose:** Set new password via email token

**Key Components:**
- New password form
- Password strength indicator
- Submit button

**Data Needs:**
- Token from URL query params

**User Interactions:**
- Submit new password → API call → Navigate to `/auth/login`

---

## Authenticated Pages

### Dashboard Page (`/dashboard`)

**Purpose:** Main landing page showing overview and quick actions

**Key Components:**
- Welcome message with user name
- Quick stats cards:
  - Total inventory items
  - Items expiring soon (< 3 days)
  - Recipes saved
  - Meals logged this week
- Expiring items alert banner (if any)
- Recent activity feed:
  - Recent meals logged
  - Recent recipes saved
  - Inventory updates
- Quick action buttons:
  - Add inventory item
  - Log meal
  - Generate meal plan
  - Browse recipes

**Data Needs:**
- User profile (name)
- Inventory summary stats
- Recent activity (last 10 items)
- Expiring items (next 3 days)

**User Interactions:**
- Click stat card → Navigate to relevant page
- Click "Add item" → Open add inventory modal
- Click "Log meal" → Navigate to `/meals` with modal open
- Click "Generate meal plan" → Navigate to `/meal-plans`
- Click activity item → Navigate to detail page

**API Calls:**
```typescript
// GET /api/v1/users/me
// GET /api/v1/inventory/stats
// GET /api/v1/inventory?expiring_soon=true&limit=5
// GET /api/v1/activity-logs?limit=10
```

---

### Inventory Page (`/inventory`)

**Purpose:** Manage pantry and fridge items

**Key Components:**
- Page header with search bar
- Category tabs (All, Vegetables, Fruits, Proteins, Grains, Dairy, Other)
- Sort dropdown (Name, Expiration date, Quantity, Recently added)
- Filter button (Show expired, Show low stock)
- Inventory item cards/list:
  - Item name
  - Quantity with unit
  - Expiration date badge (color-coded)
  - Category badge
  - Edit/Delete actions
- Add item button (floating action button)
- Empty state with CTA

**Data Needs:**
- Inventory items (paginated)
- Food categories
- Filter/sort state

**User Interactions:**
- Search input → Filter items
- Click category tab → Filter by category
- Change sort → Re-order items
- Toggle filter → Update list
- Click item → Open detail/edit modal
- Click delete → Confirm and delete
- Click add button → Open AddItemDialog with tabs (Manual, Voice, Camera)

**API Calls:**
```typescript
// GET /api/v1/inventory?category={cat}&sort={sort}&search={query}
// GET /api/v1/food-categories
// POST /api/v1/inventory
// PATCH /api/v1/inventory/{id}
// DELETE /api/v1/inventory/{id}
// POST /api/v1/inventory/parse-voice (audio blob)
// POST /api/v1/inventory/parse-image (image file)
```

---

### Meals Page (`/meals`)

**Purpose:** Log meals and view meal history

**Key Components:**
- Date range picker
- Meal type filter (All, Breakfast, Lunch, Dinner, Snack)
- Meal cards grouped by date:
  - Meal name
  - Meal type badge
  - Calories and macros (P/C/F)
  - Timestamp
  - Image (if available)
  - AI insights badge (if analyzed)
  - Edit/Delete actions
- Daily summary cards (calories, macros)
- Add meal button (floating)
- Empty state

**Data Needs:**
- Meals (date range filtered)
- Daily nutritional summaries
- User goals for comparison

**User Interactions:**
- Select date range → Fetch meals
- Filter by meal type → Update list
- Click meal → Open detail modal with full nutrition
- Click delete → Confirm and delete
- Click add → Open AddMealDialog with tabs (Text, Voice, Camera)

**API Calls:**
```typescript
// GET /api/v1/meals?start_date={date}&end_date={date}&meal_type={type}
// GET /api/v1/meals/{id}
// POST /api/v1/meals
// PATCH /api/v1/meals/{id}
// DELETE /api/v1/meals/{id}
// POST /api/v1/meals/analyze-text
// POST /api/v1/meals/analyze-voice
// POST /api/v1/meals/analyze-image
```

---

### Recipes Page (`/recipes`)

**Purpose:** Browse, search, and save recipes

**Key Components:**
- Search bar with filters:
  - Dietary preferences (vegetarian, vegan, gluten-free)
  - Difficulty (easy, medium, hard)
  - Cook time (< 30 min, 30-60 min, > 60 min)
  - Calories range
- Recipe grid/list view toggle
- Recipe cards:
  - Image
  - Recipe name
  - Cook time, servings
  - Difficulty badge
  - Calories per serving
  - Save/unsave button
- Tabs: All Recipes, Saved Recipes, My Recipes
- Pagination
- Empty state

**Data Needs:**
- Recipes (paginated, filtered)
- User's saved recipes
- User's custom recipes

**User Interactions:**
- Search/filter → Update recipe list
- Click recipe card → Navigate to `/recipes/{id}`
- Click save button → Save/unsave recipe
- Switch tabs → Show different recipe sets
- Click "Create recipe" → Navigate to recipe creation form

**API Calls:**
```typescript
// GET /api/v1/recipes?search={query}&difficulty={diff}&max_cook_time={min}
// GET /api/v1/user-recipes?type=saved
// GET /api/v1/user-recipes?type=custom
// POST /api/v1/user-recipes (save recipe)
// DELETE /api/v1/user-recipes/{id} (unsave)
```

---

### Recipe Detail Page (`/recipes/{id}`)

**Purpose:** View full recipe details

**Key Components:**
- Recipe header:
  - Recipe name
  - Image
  - Save button
  - Share button
  - Cook time, servings, difficulty
- Nutrition facts card
- Ingredients list with checkboxes
- Step-by-step instructions
- "Add to meal plan" button
- "Start cooking" button (opens voice assistant)
- Related recipes section

**Data Needs:**
- Recipe details
- Ingredients
- Instructions
- Nutrition information

**User Interactions:**
- Click save → Save/unsave recipe
- Click checkbox → Mark ingredient as checked
- Click "Add to meal plan" → Open meal plan selector
- Click "Start cooking" → Navigate to `/cooking/{id}` (voice assistant)
- Click related recipe → Navigate to that recipe

**API Calls:**
```typescript
// GET /api/v1/recipes/{id}
// POST /api/v1/user-recipes (save)
// DELETE /api/v1/user-recipes/{id} (unsave)
```

---

### Meal Planning Page (`/meal-plans`)

**Purpose:** Generate and manage weekly meal plans

**Key Components:**
- Week selector (previous/next week)
- Generate plan button
- Calendar grid (7 days × 4 meal types):
  - Each cell shows planned recipe or empty state
  - Click to add/edit meal
- Plan generation modal:
  - Dietary preferences
  - Calorie target
  - Number of servings
  - Cuisine preferences
  - Generate button
- Streaming progress indicator (during generation)
- "Create shopping list" button
- Nutrition summary for the week

**Data Needs:**
- Current meal plan (by week)
- User preferences
- Inventory (for recipe suggestions)

**User Interactions:**
- Click generate → Open generation modal → Submit → WebSocket streaming → Display results
- Click meal cell → Add/replace meal
- Drag and drop meals to rearrange
- Click "Create shopping list" → Generate shopping list from plan
- Navigate weeks → Fetch different week's plan

**API Calls:**
```typescript
// GET /api/v1/meal-plans?week_start={date}
// POST /api/v1/meal-plans (create plan)
// WebSocket /ws/meal-plan-generation (streaming)
// PATCH /api/v1/meal-plan-items/{id}
// DELETE /api/v1/meal-plan-items/{id}
// POST /api/v1/grocery-lists/from-meal-plan
```

---

### Cooking Assistant Page (`/cooking/{recipeId}`)

**Purpose:** Voice-guided cooking experience

**Key Components:**
- Recipe header (minimized)
- Active step highlight
- Timer displays (multiple timers)
- Voice recording button (push-to-talk)
- Transcription display
- AI response display (text + audio)
- Ingredient substitution suggestions
- Unit conversion helper
- "Exit cooking mode" button

**Data Needs:**
- Recipe details
- Active timers
- Conversation context

**User Interactions:**
- Hold/click mic button → Record voice → Send to backend → Receive response (text + audio)
- View timer → Pause/resume/cancel
- Click ingredient → Ask for substitution
- Click measurement → Ask for conversion
- Navigate between steps

**API Calls:**
```typescript
// GET /api/v1/recipes/{id}
// WebSocket /ws/cooking-assistant (bidirectional voice + text)
```

---

### Shopping Lists Page (`/shopping`)

**Purpose:** Manage grocery shopping lists

**Key Components:**
- List selector dropdown (if multiple lists)
- Create new list button
- Shopping list items:
  - Checkbox (checked/unchecked)
  - Item name
  - Quantity + unit
  - Category badge
  - Edit/Delete actions
- Group by category toggle
- "Clear checked items" button
- Add item input (quick add)
- Share list button
- Empty state

**Data Needs:**
- Shopping lists
- List items (grouped by category optionally)

**User Interactions:**
- Check item → Mark as purchased
- Click item → Edit quantity/name
- Delete item → Remove from list
- Quick add → Add item to list
- Toggle grouping → Reorder by category
- Click share → Generate shareable link
- Clear checked → Remove all checked items

**API Calls:**
```typescript
// GET /api/v1/grocery-lists
// GET /api/v1/grocery-lists/{id}
// POST /api/v1/grocery-lists
// POST /api/v1/grocery-list-items
// PATCH /api/v1/grocery-list-items/{id}
// DELETE /api/v1/grocery-list-items/{id}
```

---

### Profile Page (`/profile`)

**Purpose:** User profile and account settings

**Key Components:**
- Profile section:
  - Avatar upload
  - Name
  - Email
  - Change password
- Preferences section:
  - Dietary restrictions (multi-select)
  - Cuisine preferences
  - Measurement units (metric/imperial)
  - Language
- Notifications settings:
  - Email notifications
  - Push notifications
  - Expiration alerts
- Account actions:
  - Export data
  - Delete account

**Data Needs:**
- User profile
- User preferences
- Notification settings

**User Interactions:**
- Upload avatar → Update profile image
- Edit fields → Save changes
- Change password → Verify old password, set new
- Toggle notifications → Update settings
- Click export → Download data
- Click delete → Confirm and delete account

**API Calls:**
```typescript
// GET /api/v1/users/me
// PATCH /api/v1/users/me
// POST /api/v1/users/me/avatar
// POST /api/v1/users/me/change-password
// GET /api/v1/user-profiles/me
// PATCH /api/v1/user-profiles/me
// GET /api/v1/users/me/export
// DELETE /api/v1/users/me
```

---

### Goals Page (`/goals`)

**Purpose:** Set and track health goals

**Key Components:**
- Current goals summary:
  - Weight goal (current → target)
  - Daily calorie target
  - Macro targets (P/C/F percentages)
  - Weekly activity level
- Goal setting forms:
  - Weight goal (lose/maintain/gain)
  - Target weight and timeline
  - Activity level selector
  - Macro distribution (auto or custom)
- Progress visualization:
  - Weight progress chart
  - Calorie adherence chart
  - Weekly summary
- Goal history timeline

**Data Needs:**
- User goals (current and historical)
- Weight history
- Calorie intake history

**User Interactions:**
- Set/update goal → Calculate recommendations → Save
- View progress charts → Zoom in on date ranges
- Edit macro targets → Update targets
- Log weight → Add to progress tracking

**API Calls:**
```typescript
// GET /api/v1/user-goals?status=active
// GET /api/v1/user-goals/history
// POST /api/v1/user-goals
// PATCH /api/v1/user-goals/{id}
// GET /api/v1/users/me/weight-history
// POST /api/v1/users/me/weight-log
```

---

## API Routes

### REST API Routes

All REST API routes are prefixed with `/api/v1/`

**Authentication:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password

**Users:**
- `GET /users/me` - Get current user
- `PATCH /users/me` - Update user
- `POST /users/me/avatar` - Upload avatar
- `POST /users/me/change-password` - Change password
- `GET /users/me/export` - Export user data
- `DELETE /users/me` - Delete account

**Inventory:**
- `GET /inventory` - List items (with filters)
- `GET /inventory/stats` - Get summary stats
- `GET /inventory/{id}` - Get item details
- `POST /inventory` - Create item
- `POST /inventory/parse-voice` - Parse voice input
- `POST /inventory/parse-image` - Parse image
- `PATCH /inventory/{id}` - Update item
- `DELETE /inventory/{id}` - Delete item

**Meals:**
- `GET /meals` - List meals (with filters)
- `GET /meals/{id}` - Get meal details
- `POST /meals` - Create meal
- `POST /meals/analyze-text` - Analyze text description
- `POST /meals/analyze-voice` - Analyze voice input
- `POST /meals/analyze-image` - Analyze food image
- `PATCH /meals/{id}` - Update meal
- `DELETE /meals/{id}` - Delete meal

**Recipes:**
- `GET /recipes` - Search/list recipes
- `GET /recipes/{id}` - Get recipe details
- `POST /recipes` - Create custom recipe
- `GET /user-recipes` - Get saved/custom recipes
- `POST /user-recipes` - Save recipe
- `DELETE /user-recipes/{id}` - Unsave recipe

**Meal Plans:**
- `GET /meal-plans` - Get meal plans
- `POST /meal-plans` - Create meal plan
- `PATCH /meal-plan-items/{id}` - Update plan item
- `DELETE /meal-plan-items/{id}` - Delete plan item

**Shopping Lists:**
- `GET /grocery-lists` - Get shopping lists
- `GET /grocery-lists/{id}` - Get list details
- `POST /grocery-lists` - Create list
- `POST /grocery-lists/from-meal-plan` - Generate from meal plan
- `DELETE /grocery-lists/{id}` - Delete list
- `POST /grocery-list-items` - Add item
- `PATCH /grocery-list-items/{id}` - Update item
- `DELETE /grocery-list-items/{id}` - Delete item

**Goals:**
- `GET /user-goals` - Get goals
- `POST /user-goals` - Create goal
- `PATCH /user-goals/{id}` - Update goal

**Activity:**
- `GET /activity-logs` - Get activity feed

### WebSocket Routes

**Meal Plan Generation:**
- `WS /ws/meal-plan-generation`
- Sends: User preferences, inventory
- Receives: Streaming meal plan generation progress

**Cooking Assistant:**
- `WS /ws/cooking-assistant`
- Sends: Audio blobs, text messages, recipe context
- Receives: Transcriptions, AI responses, audio responses, timer updates

---

## Layout Structure

### Root Layout (`app/layout.tsx`)
- Global providers (React Query, Theme, Auth)
- Global styles
- Toast container
- Font imports

### Dashboard Layout (`app/(dashboard)/layout.tsx`)
- Header with navigation
- Sidebar (optional, collapsible)
- Main content area
- Protected route wrapper (requires auth)

### Auth Layout (`app/auth/layout.tsx`)
- Centered form layout
- No header/sidebar
- Background image/gradient
- Redirect if already authenticated

---

## Notes

- All authenticated pages require JWT token in Authorization header
- Use React Query for data fetching with automatic caching
- Implement optimistic updates for better UX
- Use Suspense boundaries for loading states
- Implement error boundaries for graceful error handling
- All forms should have client-side validation with Zod
- Use Next.js App Router with server components where possible
- Implement progressive enhancement for voice/camera features
