# Component Inventory

## Layout Components

### `AppShell`
- **Purpose**: Main layout wrapper for the application.
- **Props**: `children`, `showSidebar` (boolean), `showHeader` (boolean)
- **Usage**: Wraps all pages.

### `Header`
- **Purpose**: Top navigation bar.
- **Props**: `user` (object), `onMenuClick` (function)
- **Components**: Logo, Navigation Links, User Avatar/Menu.

### `Sidebar`
- **Purpose**: Side navigation for desktop/mobile drawer.
- **Props**: `isOpen` (boolean), `onClose` (function)
- **Items**: Dashboard, Meal Plan, Inventory, Shopping List, Settings.

### `Container`
- **Purpose**: Constrains content width.
- **Variants**: `sm`, `md`, `lg`, `xl`, `fluid`
- **Props**: `className`

---

## Forms

### `Input`
- **Purpose**: Text input field.
- **Variants**: `default`, `error`, `success`
- **Props**: `label`, `placeholder`, `type`, `error` (string)
- **States**: Focus, Disabled, Error.

### `Button`
- **Purpose**: Trigger actions.
- **Variants**: `primary`, `secondary`, `outline`, `ghost`, `destructive`
- **Sizes**: `sm`, `md`, `lg`
- **Props**: `isLoading` (boolean), `icon` (ReactNode)
- **States**: Hover, Active, Disabled, Loading.

### `VoiceInput`
- **Purpose**: Button to trigger voice recording.
- **Props**: `onRecordingComplete` (function), `isListening` (boolean)
- **States**: Idle, Listening (animated), Processing.

### `CameraCapture`
- **Purpose**: Interface for taking/uploading food photos.
- **Props**: `onCapture` (function)
- **States**: Idle, Camera Active, Preview.

### `Select`
- **Purpose**: Dropdown selection.
- **Props**: `options` (array), `value`, `onChange`

---

## Data Display

### `NutritionCard`
- **Purpose**: Display nutritional info (calories, macros).
- **Props**: `calories`, `protein`, `carbs`, `fat`
- **Variants**: `summary` (small), `detailed` (large)

### `MealCard`
- **Purpose**: Display a single meal item.
- **Props**: `meal` (object), `onEdit`, `onDelete`
- **Content**: Image, Title, Calories, Time.

### `InventoryItem`
- **Purpose**: Display an item in the pantry/fridge.
- **Props**: `item` (object), `expiryDate`
- **States**: Normal, Expiring Soon (warning color), Expired (error color).

### `Chart`
- **Purpose**: Visualize progress (weight, calories).
- **Props**: `data` (array), `type` (line, bar)

---

## Feedback

### `Toast`
- **Purpose**: Temporary notifications.
- **Variants**: `success`, `error`, `info`
- **Props**: `message`, `duration`

### `Modal`
- **Purpose**: Dialog overlays.
- **Props**: `isOpen`, `onClose`, `title`, `children`

### `LoadingSpinner`
- **Purpose**: Indicate loading state.
- **Sizes**: `sm`, `md`, `lg`

---

## Navigation

### `Tabs`
- **Purpose**: Switch between views (e.g., Daily/Weekly view).
- **Props**: `items` (array), `activeTab`, `onChange`

### `Breadcrumbs`
- **Purpose**: Show current location hierarchy.
- **Props**: `items` (array of links)
