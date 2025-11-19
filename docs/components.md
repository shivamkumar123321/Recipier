# Component Inventory - Weight Coach

> **Comprehensive list of all UI components needed for the Weight Coach application**
> Last Updated: 2025-11-18

## Table of Contents
1. [Layout Components](#layout-components)
2. [Form Components](#form-components)
3. [Data Display Components](#data-display-components)
4. [Feedback Components](#feedback-components)
5. [Navigation Components](#navigation-components)
6. [Feature-Specific Components](#feature-specific-components)
7. [Chart & Visualization Components](#chart--visualization-components)

---

## Layout Components

### Container
**Purpose:** Responsive container for page content with max-width constraints

**Variants:**
- `default` - Standard max-width container
- `fluid` - Full-width container
- `narrow` - Narrower container for forms/reading content

**Props:**
```typescript
interface ContainerProps {
  variant?: 'default' | 'fluid' | 'narrow';
  className?: string;
  children: React.ReactNode;
}
```

**States:**
- Default

**Usage Example:**
```tsx
<Container variant="default">
  <h1>Dashboard</h1>
  {/* Page content */}
</Container>
```

---

### Card
**Purpose:** Flexible container for grouping related content

**Variants:**
- `default` - Standard card with border
- `elevated` - Card with shadow elevation
- `outlined` - Card with emphasized border
- `ghost` - Borderless card

**Props:**
```typescript
interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined' | 'ghost';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
  children: React.ReactNode;
  onClick?: () => void;
}
```

**States:**
- Default
- Hover (if clickable)
- Focused (if clickable)

**Sub-components:**
- `CardHeader` - Header section with title/actions
- `CardContent` - Main content area
- `CardFooter` - Footer section with actions

**Usage Example:**
```tsx
<Card variant="elevated" padding="md">
  <CardHeader>
    <h3>Today's Summary</h3>
  </CardHeader>
  <CardContent>
    <p>1,850 / 2,000 calories</p>
  </CardContent>
</Card>
```

---

### Grid
**Purpose:** Responsive grid layout system

**Variants:**
- `default` - Auto-fit grid
- `fixed` - Fixed column count

**Props:**
```typescript
interface GridProps {
  cols?: 1 | 2 | 3 | 4 | 6 | 12;
  gap?: keyof typeof spacing;
  responsive?: {
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  className?: string;
  children: React.ReactNode;
}
```

**Usage Example:**
```tsx
<Grid cols={3} gap={4} responsive={{ sm: 1, md: 2, lg: 3 }}>
  <MealCard />
  <MealCard />
  <MealCard />
</Grid>
```

---

### Stack
**Purpose:** Vertical or horizontal stack layout with consistent spacing

**Variants:**
- `vertical` - Vertical stack (default)
- `horizontal` - Horizontal stack

**Props:**
```typescript
interface StackProps {
  direction?: 'vertical' | 'horizontal';
  gap?: keyof typeof spacing;
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between';
  className?: string;
  children: React.ReactNode;
}
```

**Usage Example:**
```tsx
<Stack direction="vertical" gap={4}>
  <Button>Save</Button>
  <Button variant="outline">Cancel</Button>
</Stack>
```

---

### Modal
**Purpose:** Dialog overlay for focused interactions

**Variants:**
- `default` - Standard modal
- `fullscreen` - Full-screen modal (mobile)
- `drawer` - Side drawer (mobile)

**Props:**
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  variant?: 'default' | 'fullscreen' | 'drawer';
  children: React.ReactNode;
}
```

**States:**
- Open
- Closed
- Opening (animation)
- Closing (animation)

**Usage Example:**
```tsx
<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Add Meal"
  size="md"
>
  <MealForm />
</Modal>
```

---

## Form Components

### Button
**Purpose:** Interactive button for user actions

**Variants:**
- `primary` - Primary action button
- `secondary` - Secondary action button
- `outline` - Outlined button
- `ghost` - Text-only button
- `danger` - Destructive action button

**Props:**
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  onClick?: () => void;
  children: React.ReactNode;
}
```

**States:**
- Default
- Hover
- Active (pressed)
- Focused
- Disabled
- Loading

**Usage Example:**
```tsx
<Button
  variant="primary"
  size="md"
  loading={isSubmitting}
  icon={<PlusIcon />}
  onClick={handleSubmit}
>
  Add Meal
</Button>
```

---

### Input
**Purpose:** Text input field

**Variants:**
- `default` - Standard text input
- `search` - Search input with icon
- `password` - Password input with toggle

**Props:**
```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  variant?: 'default' | 'search';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  placeholder?: string;
  value?: string;
  error?: string;
  helperText?: string;
  disabled?: boolean;
  required?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  onChange?: (value: string) => void;
}
```

**States:**
- Default
- Focused
- Error
- Disabled
- Filled

**Usage Example:**
```tsx
<Input
  type="email"
  label="Email Address"
  placeholder="you@example.com"
  value={email}
  onChange={setEmail}
  error={emailError}
  required
/>
```

---

### TextArea
**Purpose:** Multi-line text input

**Props:**
```typescript
interface TextAreaProps {
  label?: string;
  placeholder?: string;
  value?: string;
  rows?: number;
  maxLength?: number;
  error?: string;
  helperText?: string;
  disabled?: boolean;
  required?: boolean;
  onChange?: (value: string) => void;
}
```

**States:**
- Default
- Focused
- Error
- Disabled

**Usage Example:**
```tsx
<TextArea
  label="Meal Notes"
  placeholder="Add notes about your meal..."
  rows={4}
  value={notes}
  onChange={setNotes}
/>
```

---

### Select
**Purpose:** Dropdown selection field

**Variants:**
- `default` - Standard select
- `multi` - Multi-select

**Props:**
```typescript
interface SelectProps {
  label?: string;
  placeholder?: string;
  options: Array<{ value: string; label: string }>;
  value?: string | string[];
  error?: string;
  disabled?: boolean;
  required?: boolean;
  searchable?: boolean;
  multi?: boolean;
  onChange?: (value: string | string[]) => void;
}
```

**States:**
- Default
- Open
- Focused
- Error
- Disabled

**Usage Example:**
```tsx
<Select
  label="Meal Type"
  placeholder="Select meal type"
  options={[
    { value: 'breakfast', label: 'Breakfast' },
    { value: 'lunch', label: 'Lunch' },
    { value: 'dinner', label: 'Dinner' },
    { value: 'snack', label: 'Snack' },
  ]}
  value={mealType}
  onChange={setMealType}
/>
```

---

### Checkbox
**Purpose:** Binary choice input

**Props:**
```typescript
interface CheckboxProps {
  label?: string;
  checked?: boolean;
  indeterminate?: boolean;
  disabled?: boolean;
  error?: string;
  onChange?: (checked: boolean) => void;
}
```

**States:**
- Unchecked
- Checked
- Indeterminate
- Disabled
- Focused

**Usage Example:**
```tsx
<Checkbox
  label="Include in weekly meal plan"
  checked={includeInPlan}
  onChange={setIncludeInPlan}
/>
```

---

### Radio
**Purpose:** Single choice from multiple options

**Props:**
```typescript
interface RadioProps {
  label?: string;
  value: string;
  checked?: boolean;
  disabled?: boolean;
  onChange?: (value: string) => void;
}

interface RadioGroupProps {
  name: string;
  options: Array<{ value: string; label: string }>;
  value?: string;
  orientation?: 'horizontal' | 'vertical';
  onChange?: (value: string) => void;
}
```

**States:**
- Unchecked
- Checked
- Disabled
- Focused

**Usage Example:**
```tsx
<RadioGroup
  name="goal"
  options={[
    { value: 'lose', label: 'Lose Weight' },
    { value: 'maintain', label: 'Maintain Weight' },
    { value: 'gain', label: 'Gain Weight' },
  ]}
  value={goal}
  onChange={setGoal}
/>
```

---

### Toggle
**Purpose:** On/off switch for settings

**Variants:**
- `default` - Standard toggle
- `small` - Compact toggle

**Props:**
```typescript
interface ToggleProps {
  label?: string;
  checked?: boolean;
  disabled?: boolean;
  size?: 'sm' | 'md';
  onChange?: (checked: boolean) => void;
}
```

**States:**
- Off
- On
- Disabled
- Focused

**Usage Example:**
```tsx
<Toggle
  label="Enable voice commands"
  checked={voiceEnabled}
  onChange={setVoiceEnabled}
/>
```

---

### Slider
**Purpose:** Numeric value selection with visual feedback

**Props:**
```typescript
interface SliderProps {
  label?: string;
  min: number;
  max: number;
  step?: number;
  value?: number;
  unit?: string;
  showValue?: boolean;
  disabled?: boolean;
  onChange?: (value: number) => void;
}
```

**States:**
- Default
- Dragging
- Focused
- Disabled

**Usage Example:**
```tsx
<Slider
  label="Daily Calorie Goal"
  min={1200}
  max={3500}
  step={50}
  value={calorieGoal}
  unit="cal"
  showValue
  onChange={setCalorieGoal}
/>
```

---

### DatePicker
**Purpose:** Date selection input

**Variants:**
- `single` - Single date selection
- `range` - Date range selection

**Props:**
```typescript
interface DatePickerProps {
  label?: string;
  value?: Date;
  minDate?: Date;
  maxDate?: Date;
  error?: string;
  disabled?: boolean;
  variant?: 'single' | 'range';
  onChange?: (date: Date) => void;
}
```

**States:**
- Closed
- Open
- Error
- Disabled

**Usage Example:**
```tsx
<DatePicker
  label="Meal Date"
  value={mealDate}
  onChange={setMealDate}
/>
```

---

### FileUpload
**Purpose:** File selection and upload

**Variants:**
- `default` - Standard file picker
- `dropzone` - Drag-and-drop area
- `image` - Image-specific upload with preview

**Props:**
```typescript
interface FileUploadProps {
  label?: string;
  accept?: string;
  maxSize?: number;
  multiple?: boolean;
  variant?: 'default' | 'dropzone' | 'image';
  preview?: boolean;
  error?: string;
  onChange?: (files: File[]) => void;
}
```

**States:**
- Empty
- Dragging over (dropzone)
- Uploading
- Success
- Error

**Usage Example:**
```tsx
<FileUpload
  variant="image"
  accept="image/*"
  maxSize={5242880} // 5MB
  preview
  onChange={handleImageUpload}
/>
```

---

## Data Display Components

### Table
**Purpose:** Tabular data display with sorting and pagination

**Variants:**
- `default` - Standard table
- `striped` - Alternating row colors
- `bordered` - Bordered cells

**Props:**
```typescript
interface TableProps<T> {
  columns: Array<{
    key: string;
    label: string;
    sortable?: boolean;
    render?: (row: T) => React.ReactNode;
  }>;
  data: T[];
  variant?: 'default' | 'striped' | 'bordered';
  sortable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  onRowClick?: (row: T) => void;
}
```

**States:**
- Default
- Sorting
- Loading

**Usage Example:**
```tsx
<Table
  columns={[
    { key: 'name', label: 'Food', sortable: true },
    { key: 'calories', label: 'Calories', sortable: true },
    { key: 'protein', label: 'Protein' },
  ]}
  data={meals}
  variant="striped"
  pagination
  pageSize={10}
/>
```

---

### Badge
**Purpose:** Small label for status or category

**Variants:**
- `default` - Neutral badge
- `success` - Success state
- `warning` - Warning state
- `error` - Error state
- `info` - Info state

**Props:**
```typescript
interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}
```

**Usage Example:**
```tsx
<Badge variant="success">Complete</Badge>
<Badge variant="warning">Low Stock</Badge>
```

---

### Avatar
**Purpose:** User profile image or initials

**Variants:**
- `image` - Display user image
- `initials` - Display user initials
- `icon` - Display icon placeholder

**Props:**
```typescript
interface AvatarProps {
  src?: string;
  alt?: string;
  initials?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'circle' | 'square';
}
```

**States:**
- Loaded
- Loading
- Error (fallback to initials)

**Usage Example:**
```tsx
<Avatar
  src={user.profileImage}
  alt={user.name}
  initials={user.initials}
  size="md"
/>
```

---

### Tag
**Purpose:** Removable labels for filters or selections

**Props:**
```typescript
interface TagProps {
  label: string;
  onRemove?: () => void;
  variant?: 'default' | 'primary' | 'secondary';
  size?: 'sm' | 'md';
}
```

**States:**
- Default
- Hover

**Usage Example:**
```tsx
<Tag
  label="Gluten-free"
  onRemove={() => removeFilter('gluten-free')}
  variant="primary"
/>
```

---

### EmptyState
**Purpose:** Placeholder for empty data states

**Props:**
```typescript
interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
```

**Usage Example:**
```tsx
<EmptyState
  icon={<InboxIcon />}
  title="No meals logged yet"
  description="Start tracking your nutrition by adding your first meal"
  action={{
    label: 'Add Meal',
    onClick: () => openMealModal()
  }}
/>
```

---

### Accordion
**Purpose:** Collapsible content sections

**Props:**
```typescript
interface AccordionProps {
  items: Array<{
    id: string;
    title: string;
    content: React.ReactNode;
  }>;
  defaultOpen?: string[];
  allowMultiple?: boolean;
}
```

**States:**
- Collapsed
- Expanded
- Expanding (animation)
- Collapsing (animation)

**Usage Example:**
```tsx
<Accordion
  items={[
    {
      id: 'nutrition',
      title: 'Nutrition Facts',
      content: <NutritionTable />
    },
    {
      id: 'ingredients',
      title: 'Ingredients',
      content: <IngredientsList />
    }
  ]}
  defaultOpen={['nutrition']}
/>
```

---

### Tabs
**Purpose:** Content organization with multiple views

**Variants:**
- `default` - Standard tabs
- `pills` - Pill-style tabs
- `underline` - Underlined tabs

**Props:**
```typescript
interface TabsProps {
  tabs: Array<{
    id: string;
    label: string;
    content: React.ReactNode;
    icon?: React.ReactNode;
  }>;
  defaultTab?: string;
  variant?: 'default' | 'pills' | 'underline';
  onChange?: (tabId: string) => void;
}
```

**States:**
- Default
- Active
- Hover

**Usage Example:**
```tsx
<Tabs
  tabs={[
    { id: 'overview', label: 'Overview', content: <Overview /> },
    { id: 'meals', label: 'Meals', content: <MealsList /> },
    { id: 'progress', label: 'Progress', content: <ProgressCharts /> },
  ]}
  defaultTab="overview"
  variant="underline"
/>
```

---

### Tooltip
**Purpose:** Contextual information on hover

**Variants:**
- `default` - Standard tooltip
- `rich` - Rich content tooltip

**Props:**
```typescript
interface TooltipProps {
  content: React.ReactNode;
  placement?: 'top' | 'right' | 'bottom' | 'left';
  delay?: number;
  children: React.ReactNode;
}
```

**States:**
- Hidden
- Visible

**Usage Example:**
```tsx
<Tooltip content="Click to edit meal" placement="top">
  <IconButton icon={<EditIcon />} />
</Tooltip>
```

---

### Popover
**Purpose:** Floating content container

**Props:**
```typescript
interface PopoverProps {
  trigger: React.ReactNode;
  content: React.ReactNode;
  placement?: 'top' | 'right' | 'bottom' | 'left';
  closeOnClickOutside?: boolean;
}
```

**States:**
- Closed
- Open

**Usage Example:**
```tsx
<Popover
  trigger={<Button>Filter</Button>}
  content={<FilterForm />}
  placement="bottom"
/>
```

---

## Feedback Components

### Alert
**Purpose:** Important messages and notifications

**Variants:**
- `info` - Informational alert
- `success` - Success alert
- `warning` - Warning alert
- `error` - Error alert

**Props:**
```typescript
interface AlertProps {
  variant: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  dismissible?: boolean;
  icon?: React.ReactNode;
  onDismiss?: () => void;
}
```

**States:**
- Visible
- Dismissing

**Usage Example:**
```tsx
<Alert
  variant="success"
  title="Meal Saved"
  message="Your meal has been logged successfully"
  dismissible
  onDismiss={() => setShowAlert(false)}
/>
```

---

### Toast
**Purpose:** Temporary notification messages

**Variants:**
- `info` - Informational toast
- `success` - Success toast
- `warning` - Warning toast
- `error` - Error toast

**Props:**
```typescript
interface ToastProps {
  variant: 'info' | 'success' | 'warning' | 'error';
  message: string;
  duration?: number;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}
```

**States:**
- Entering
- Visible
- Exiting

**Usage Example:**
```tsx
// Via toast service
toast.success('Meal added successfully', {
  duration: 3000,
  position: 'top-right'
});
```

---

### ProgressBar
**Purpose:** Linear progress indicator

**Variants:**
- `default` - Standard progress bar
- `striped` - Striped animation
- `gradient` - Gradient fill

**Props:**
```typescript
interface ProgressBarProps {
  value: number;
  max?: number;
  variant?: 'default' | 'striped' | 'gradient';
  color?: string;
  label?: string;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

**Usage Example:**
```tsx
<ProgressBar
  value={1850}
  max={2000}
  label="Calories"
  showPercentage
  variant="gradient"
/>
```

---

### Skeleton
**Purpose:** Loading placeholder

**Variants:**
- `text` - Text skeleton
- `circle` - Circular skeleton
- `rectangle` - Rectangular skeleton

**Props:**
```typescript
interface SkeletonProps {
  variant?: 'text' | 'circle' | 'rectangle';
  width?: string | number;
  height?: string | number;
  count?: number;
}
```

**Usage Example:**
```tsx
<Skeleton variant="text" count={3} />
<Skeleton variant="circle" width={48} height={48} />
```

---

### Spinner
**Purpose:** Loading indicator

**Variants:**
- `default` - Standard spinner
- `dots` - Dot animation

**Props:**
```typescript
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'dots';
  color?: string;
}
```

**Usage Example:**
```tsx
<Spinner size="md" variant="default" />
```

---

## Navigation Components

### Header
**Purpose:** Main application header with branding and navigation

**Props:**
```typescript
interface HeaderProps {
  logo?: React.ReactNode;
  navigation?: Array<{
    label: string;
    href: string;
    icon?: React.ReactNode;
  }>;
  actions?: React.ReactNode;
  sticky?: boolean;
}
```

**Usage Example:**
```tsx
<Header
  logo={<Logo />}
  navigation={[
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Meals', href: '/meals' },
    { label: 'Recipes', href: '/recipes' },
  ]}
  actions={<UserMenu />}
  sticky
/>
```

---

### Sidebar
**Purpose:** Side navigation panel

**Variants:**
- `fixed` - Always visible
- `collapsible` - Can collapse to icons
- `overlay` - Overlay on mobile

**Props:**
```typescript
interface SidebarProps {
  items: Array<{
    label: string;
    href: string;
    icon: React.ReactNode;
    badge?: string;
  }>;
  variant?: 'fixed' | 'collapsible' | 'overlay';
  collapsed?: boolean;
  onToggle?: () => void;
}
```

**States:**
- Expanded
- Collapsed
- Transitioning

**Usage Example:**
```tsx
<Sidebar
  items={[
    { label: 'Dashboard', href: '/dashboard', icon: <HomeIcon /> },
    { label: 'Meals', href: '/meals', icon: <ForkIcon />, badge: '3' },
  ]}
  variant="collapsible"
  collapsed={isCollapsed}
  onToggle={() => setIsCollapsed(!isCollapsed)}
/>
```

---

### Breadcrumbs
**Purpose:** Navigation trail

**Props:**
```typescript
interface BreadcrumbsProps {
  items: Array<{
    label: string;
    href?: string;
  }>;
  separator?: React.ReactNode;
}
```

**Usage Example:**
```tsx
<Breadcrumbs
  items={[
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Meals', href: '/meals' },
    { label: 'Breakfast' },
  ]}
/>
```

---

### Pagination
**Purpose:** Page navigation for large data sets

**Props:**
```typescript
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  showFirstLast?: boolean;
  showPageNumbers?: boolean;
  pageSize?: number;
  onPageSizeChange?: (size: number) => void;
}
```

**Usage Example:**
```tsx
<Pagination
  currentPage={currentPage}
  totalPages={10}
  onPageChange={setCurrentPage}
  showPageNumbers
/>
```

---

### Menu
**Purpose:** Dropdown menu for actions

**Props:**
```typescript
interface MenuProps {
  trigger: React.ReactNode;
  items: Array<{
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    danger?: boolean;
    divider?: boolean;
  }>;
  placement?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
}
```

**States:**
- Closed
- Open

**Usage Example:**
```tsx
<Menu
  trigger={<IconButton icon={<DotsIcon />} />}
  items={[
    { label: 'Edit', icon: <EditIcon />, onClick: handleEdit },
    { label: 'Delete', icon: <TrashIcon />, onClick: handleDelete, danger: true },
  ]}
  placement="bottom-right"
/>
```

---

## Feature-Specific Components

### MealCard
**Purpose:** Display meal information in card format

**Variants:**
- `compact` - Minimal information
- `detailed` - Full information with macros

**Props:**
```typescript
interface MealCardProps {
  meal: {
    id: string;
    name: string;
    mealType: string;
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
    image?: string;
    timestamp: Date;
  };
  variant?: 'compact' | 'detailed';
  onEdit?: () => void;
  onDelete?: () => void;
}
```

**Usage Example:**
```tsx
<MealCard
  meal={mealData}
  variant="detailed"
  onEdit={handleEdit}
  onDelete={handleDelete}
/>
```

---

### NutritionRing
**Purpose:** Circular progress indicator for nutrition goals

**Props:**
```typescript
interface NutritionRingProps {
  label: string;
  value: number;
  max: number;
  color: string;
  size?: 'sm' | 'md' | 'lg';
  showPercentage?: boolean;
}
```

**Usage Example:**
```tsx
<NutritionRing
  label="Calories"
  value={1850}
  max={2000}
  color={colors.primary[500]}
  size="lg"
  showPercentage
/>
```

---

### MacroBar
**Purpose:** Stacked bar showing protein/carbs/fats distribution

**Props:**
```typescript
interface MacroBarProps {
  protein: number;
  carbs: number;
  fats: number;
  showLegend?: boolean;
  showValues?: boolean;
}
```

**Usage Example:**
```tsx
<MacroBar
  protein={120}
  carbs={200}
  fats={50}
  showLegend
  showValues
/>
```

---

### VoiceRecorder
**Purpose:** Voice input recording interface

**Props:**
```typescript
interface VoiceRecorderProps {
  onRecordingComplete: (audio: Blob) => void;
  maxDuration?: number;
  visualize?: boolean;
}
```

**States:**
- Idle
- Recording
- Processing
- Error

**Usage Example:**
```tsx
<VoiceRecorder
  onRecordingComplete={handleAudioSubmit}
  maxDuration={60}
  visualize
/>
```

---

### CameraCapture
**Purpose:** Food image capture interface

**Props:**
```typescript
interface CameraCaptureProps {
  onCapture: (image: Blob) => void;
  onCancel?: () => void;
  aspectRatio?: number;
  facingMode?: 'user' | 'environment';
}
```

**States:**
- Camera Active
- Preview
- Capturing

**Usage Example:**
```tsx
<CameraCapture
  onCapture={handleImageCapture}
  facingMode="environment"
  aspectRatio={4/3}
/>
```

---

### RecipeCard
**Purpose:** Display recipe information

**Variants:**
- `grid` - Grid layout card
- `list` - List layout card

**Props:**
```typescript
interface RecipeCardProps {
  recipe: {
    id: string;
    name: string;
    image: string;
    cookTime: number;
    servings: number;
    calories: number;
    difficulty: 'easy' | 'medium' | 'hard';
  };
  variant?: 'grid' | 'list';
  onView?: () => void;
  onSave?: () => void;
}
```

**Usage Example:**
```tsx
<RecipeCard
  recipe={recipeData}
  variant="grid"
  onView={handleView}
  onSave={handleSave}
/>
```

---

### InventoryItem
**Purpose:** Display inventory item with stock status

**Props:**
```typescript
interface InventoryItemProps {
  item: {
    id: string;
    name: string;
    quantity: number;
    unit: string;
    expiryDate?: Date;
    category: string;
  };
  onEdit?: () => void;
  onDelete?: () => void;
}
```

**States:**
- In Stock
- Low Stock
- Expired
- Expiring Soon

**Usage Example:**
```tsx
<InventoryItem
  item={inventoryData}
  onEdit={handleEdit}
  onDelete={handleDelete}
/>
```

---

### ShoppingListItem
**Purpose:** Grocery list item with check-off functionality

**Props:**
```typescript
interface ShoppingListItemProps {
  item: {
    id: string;
    name: string;
    quantity: number;
    unit: string;
    checked: boolean;
  };
  onToggle: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}
```

**States:**
- Unchecked
- Checked

**Usage Example:**
```tsx
<ShoppingListItem
  item={listItem}
  onToggle={handleToggle}
  onEdit={handleEdit}
/>
```

---

### TimerDisplay
**Purpose:** Cooking timer display and controls

**Props:**
```typescript
interface TimerDisplayProps {
  timer: {
    id: string;
    label: string;
    duration: number;
    remaining: number;
    status: 'running' | 'paused' | 'finished';
  };
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
}
```

**States:**
- Running
- Paused
- Finished

**Usage Example:**
```tsx
<TimerDisplay
  timer={activeTimer}
  onPause={handlePause}
  onResume={handleResume}
  onCancel={handleCancel}
/>
```

---

### MealPlanCalendar
**Purpose:** Weekly meal plan calendar view

**Props:**
```typescript
interface MealPlanCalendarProps {
  meals: Array<{
    date: Date;
    mealType: string;
    recipe: {
      name: string;
      image: string;
    };
  }>;
  startDate: Date;
  onMealClick?: (meal: any) => void;
  onAddMeal?: (date: Date, mealType: string) => void;
}
```

**Usage Example:**
```tsx
<MealPlanCalendar
  meals={plannedMeals}
  startDate={weekStart}
  onMealClick={handleMealClick}
  onAddMeal={handleAddMeal}
/>
```

---

## Chart & Visualization Components

### LineChart
**Purpose:** Line chart for trends over time

**Props:**
```typescript
interface LineChartProps {
  data: Array<{ date: Date; value: number }>;
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  color?: string;
  showGrid?: boolean;
  showPoints?: boolean;
}
```

**Usage Example:**
```tsx
<LineChart
  data={weightHistory}
  title="Weight Progress"
  xAxisLabel="Date"
  yAxisLabel="Weight (lbs)"
  color={colors.primary[500]}
  showPoints
/>
```

---

### BarChart
**Purpose:** Bar chart for comparisons

**Props:**
```typescript
interface BarChartProps {
  data: Array<{ label: string; value: number }>;
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  color?: string;
  horizontal?: boolean;
}
```

**Usage Example:**
```tsx
<BarChart
  data={macrosByDay}
  title="Weekly Macro Intake"
  yAxisLabel="Grams"
  color={colors.primary[500]}
/>
```

---

### PieChart
**Purpose:** Pie/donut chart for proportions

**Props:**
```typescript
interface PieChartProps {
  data: Array<{ label: string; value: number; color: string }>;
  title?: string;
  donut?: boolean;
  showLegend?: boolean;
  showValues?: boolean;
}
```

**Usage Example:**
```tsx
<PieChart
  data={[
    { label: 'Protein', value: 30, color: colors.nutrition.protein },
    { label: 'Carbs', value: 50, color: colors.nutrition.carbs },
    { label: 'Fats', value: 20, color: colors.nutrition.fats },
  ]}
  title="Macro Distribution"
  donut
  showLegend
/>
```

---

### StatCard
**Purpose:** Display key metrics and statistics

**Variants:**
- `default` - Standard stat card
- `trend` - Stat card with trend indicator

**Props:**
```typescript
interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'trend';
  trend?: {
    value: number;
    direction: 'up' | 'down';
    isPositive: boolean;
  };
  color?: string;
}
```

**Usage Example:**
```tsx
<StatCard
  label="Calories Today"
  value={1850}
  unit="kcal"
  icon={<FlameIcon />}
  variant="trend"
  trend={{ value: 12, direction: 'down', isPositive: true }}
  color={colors.primary[500]}
/>
```

---

## Implementation Priority

### Phase 1 - Core Components (MVP)
1. Layout: Container, Card, Grid, Stack, Modal
2. Forms: Button, Input, Select, FileUpload
3. Data Display: Table, Badge, EmptyState
4. Feedback: Alert, Toast, Spinner
5. Navigation: Header, Breadcrumbs

### Phase 2 - Feature Components
1. MealCard
2. NutritionRing
3. MacroBar
4. VoiceRecorder
5. CameraCapture
6. StatCard

### Phase 3 - Advanced Components
1. Charts (Line, Bar, Pie)
2. RecipeCard
3. InventoryItem
4. ShoppingListItem
5. TimerDisplay
6. MealPlanCalendar

### Phase 4 - Enhancement Components
1. Sidebar
2. Tabs
3. Accordion
4. Tooltip/Popover
5. Slider
6. DatePicker

---

## Notes

- All components should be built with **shadcn/ui** as the foundation where applicable
- Components must be **fully accessible** (ARIA labels, keyboard navigation, screen reader support)
- All components should support **dark mode** via CSS variables
- Use **TypeScript** with strict typing for all props and states
- Implement **responsive design** for all components (mobile-first approach)
- Add **Storybook** stories for component documentation and testing
- Follow **atomic design** principles where appropriate
