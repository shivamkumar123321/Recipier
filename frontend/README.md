# Weight Coach Frontend

AI-powered nutrition coaching web application built with Next.js 14, TypeScript, and Tailwind CSS.

## Features Implemented

### ✅ Dashboard Page (`/dashboard`)
- Welcome message with user name
- Quick stats cards (total items, expiring soon, recipes saved, categories)
- Expiring items alert banner
- Recent activity feed
- Quick actions (Add item, Generate meal plan, Browse recipes, Shopping list)

### ✅ Inventory Page (`/inventory`)
- Inventory list with search and filters
- Category tabs for filtering
- Sort options (name, expiration date, quantity, created date)
- Empty state with call-to-action
- Edit/delete actions on items
- Color-coded expiration badges

### ✅ Inventory Components
- **InventoryItem**: Individual item card with image, quantity, category, expiration badge
- **ExpirationBadge**: Color-coded badge (red for expired, orange for expiring soon, yellow/blue/green for fresh)
- **InventoryFilters**: Search bar, sort dropdown, category tabs
- **AddItemDialog**: Modal with three input methods

### ✅ Add Item Methods

#### 1. Manual Entry
- Form with fields: name, quantity, unit, category, expiration date, purchase date, location, notes
- Form validation with Zod
- Common units dropdown with custom unit option
- Category selector

#### 2. Voice Input
- Record audio button using Web Audio API
- Recording status indicator with animation
- Send audio to backend for transcription and parsing
- Display transcription
- Show parsed items in editable list
- Confirm and bulk add to inventory

#### 3. Camera Scan
- Take photo or upload image
- Image preview
- Send to backend for AI identification
- Display identified items
- Edit items before adding
- Bulk add to inventory

### ✅ API Integration
- Complete API client with Axios
- Authentication with JWT tokens
- Token refresh on 401 errors
- React Query hooks for all operations
- Optimistic updates
- Toast notifications

### ✅ UI Components (shadcn/ui)
- Alert & AlertDialog
- Badge
- Button
- Card
- Dialog
- Dropdown Menu
- Form (React Hook Form integration)
- Input & Textarea
- Label
- Select
- Skeleton
- Tabs

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS 3.4
- **UI Components**: shadcn/ui (Radix UI)
- **State Management**: React Query (TanStack Query)
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Notifications**: Sonner
- **Date Handling**: date-fns

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm or yarn
- Backend API running (see backend README)

### Installation

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open browser**:
   Navigate to http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── (dashboard)/          # Dashboard layout group
│   │   ├── dashboard/        # Dashboard page
│   │   ├── inventory/        # Inventory page
│   │   └── layout.tsx        # Dashboard layout
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── features/             # Feature-specific components
│   │   └── inventory/
│   │       ├── AddItemDialog.tsx
│   │       ├── CameraScanTab.tsx
│   │       ├── ExpirationBadge.tsx
│   │       ├── InventoryFilters.tsx
│   │       ├── InventoryItem.tsx
│   │       ├── ManualEntryForm.tsx
│   │       ├── ParsedItemsList.tsx
│   │       └── VoiceInputTab.tsx
│   ├── ui/                   # shadcn/ui components
│   │   ├── alert.tsx
│   │   ├── alert-dialog.tsx
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── select.tsx
│   │   ├── skeleton.tsx
│   │   ├── tabs.tsx
│   │   └── textarea.tsx
│   └── providers.tsx         # React Query provider
├── lib/
│   ├── api/
│   │   ├── client.ts         # Axios client with auth
│   │   └── inventory.ts      # Inventory API functions
│   ├── hooks/
│   │   └── useInventory.ts   # React Query hooks
│   └── utils.ts              # Utility functions
├── styles/
│   └── design-tokens.ts      # Design system tokens
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## API Integration

### Authentication

The API client automatically handles JWT authentication:

```typescript
// Token stored in localStorage
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refreshToken);

// Automatically added to all requests
Authorization: Bearer <token>

// Auto-refreshes on 401 errors
```

### React Query Hooks

```typescript
// Fetch inventory items
const { data, isLoading } = useInventoryItems({
  category_id: 1,
  search: 'milk',
  sort_by: 'expiration_date',
});

// Create item
const createItem = useCreateInventoryItem();
await createItem.mutateAsync(itemData);

// Update item
const updateItem = useUpdateInventoryItem();
await updateItem.mutateAsync({ id, data });

// Delete item
const deleteItem = useDeleteInventoryItem();
await deleteItem.mutateAsync(id);

// Parse voice input
const parseVoice = useParseVoiceInput();
const result = await parseVoice.mutateAsync(audioBlob);

// Parse image
const parseImage = useParseImageInput();
const result = await parseImage.mutateAsync(imageFile);
```

## Voice Input

Uses Web Audio API for recording:

```typescript
// Request microphone permission
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

// Create MediaRecorder
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm',
});

// Record audio
mediaRecorder.start();

// Stop recording
mediaRecorder.stop();

// Send to backend
const audioBlob = new Blob(chunks, { type: 'audio/webm' });
await parseVoiceInput(audioBlob);
```

## Camera Scan

Supports both camera capture and file upload:

```typescript
// File input with camera capture
<input
  type="file"
  accept="image/*"
  capture="environment"  // Use rear camera on mobile
  onChange={handleFileSelect}
/>

// Send to backend
const formData = new FormData();
formData.append('image', imageFile);
await parseImageInput(imageFile);
```

## Styling

### Tailwind CSS

Uses custom design tokens from `styles/design-tokens.ts`:

```typescript
// Colors
colors.primary[500]     // #00b098
colors.secondary[500]   // #ff8f00
colors.success[500]     // #4caf50

// Typography
typography.fontSize.lg  // 1.125rem
typography.fontWeight.semibold  // 600

// Spacing
spacing[4]              // 1rem (16px)
```

### CSS Variables

Defined in `app/globals.css`:

```css
--primary: 174 100% 35%;
--secondary: 33 100% 50%;
--destructive: 0 84.2% 60.2%;
```

## Development Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Lint code
npm run type-check       # TypeScript type checking
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

### Feature Requirements

- **Voice Input**: Requires `getUserMedia` API
- **Camera Scan**: Requires File API and camera access
- **Modern JavaScript**: ES2020+ features

## Performance

- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Next.js Image component
- **React Query Caching**: 5-minute stale time for inventory
- **Optimistic Updates**: Immediate UI updates before server response

## Accessibility

- **ARIA Labels**: All interactive elements
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Semantic HTML and ARIA attributes
- **Focus Management**: Visible focus indicators

## Next Steps

- [ ] Implement authentication pages (login, signup)
- [ ] Add meals page
- [ ] Add recipes page
- [ ] Add meal planning page
- [ ] Add shopping list page
- [ ] Add user profile page
- [ ] Add dark mode support
- [ ] Add offline support (PWA)
- [ ] Add unit tests
- [ ] Add E2E tests with Playwright

## Troubleshooting

### API Connection Issues

```bash
# Check API is running
curl http://localhost:8000/health

# Check CORS settings in backend
# Ensure frontend URL is in CORS_ORIGINS
```

### Voice Input Not Working

- Check browser permissions for microphone
- Ensure HTTPS (required for getUserMedia on production)
- Check console for errors

### Camera Not Working

- Check browser permissions for camera
- Ensure HTTPS (required for camera access on production)
- Check console for errors

## License

Private - Hackathon Project
