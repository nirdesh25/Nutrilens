# Design Document: Complete Frontend Pages

## Overview

This design document specifies the implementation of the remaining frontend pages and shared UI components for the NutriLens AI application. The feature completes the user-facing interface by adding four critical pages (Waste Tracker, Scan History, User Profile, Settings) and establishing a comprehensive component library for consistent UI/UX across the application.

### Goals

- Complete the frontend page coverage with waste tracking, scan history, profile, and settings pages
- Establish a reusable component library (Button, Card, Modal, Badge, Input, Spinner) for consistency
- Implement a navigation sidebar with responsive behavior for improved user experience
- Create robust loading and error state handling across all pages
- Build a toast notification system for user feedback
- Ensure responsive design across mobile, tablet, and desktop viewports
- Integrate seamlessly with existing pages and maintain design consistency

### Non-Goals

- Backend API modifications (all endpoints already exist)
- Authentication system changes (JWT auth is already implemented)
- ML model updates or training
- Real-time features or WebSocket connections
- Internationalization implementation (language dropdown will be UI-only)
- Dark mode implementation (theme toggle will be UI-only for now)

### Technical Context

The application uses:
- **Frontend**: Next.js 14 with App Router, React 18, TypeScript, Tailwind CSS
- **State Management**: React hooks (useState, useEffect) with local component state
- **API Communication**: Axios with interceptors for JWT token injection
- **Icons**: lucide-react library
- **Styling**: Tailwind CSS utility classes with consistent design tokens
- **Existing Patterns**: File-based routing, client components with 'use client', localStorage for token storage

## Architecture

### Component Hierarchy

```
app/
├── layout.tsx (root layout with ToastContainer)
├── page.tsx (landing page)
├── auth/
│   ├── login/page.tsx
│   └── register/page.tsx
└── dashboard/
    ├── layout.tsx (NEW: DashboardLayout wrapper)
    ├── page.tsx (dashboard home)
    ├── scanner/page.tsx
    ├── groceries/page.tsx
    ├── health/page.tsx
    ├── waste/page.tsx (NEW: Waste Tracker)
    ├── history/page.tsx (NEW: Scan History)
    ├── profile/page.tsx (NEW: User Profile)
    ├── settings/page.tsx (NEW: Settings)
    ├── ph-analysis/page.tsx
    ├── smart-box/page.tsx
    └── analytics/page.tsx

components/
├── ui/
│   ├── Button.tsx (NEW)
│   ├── Card.tsx (NEW)
│   ├── Modal.tsx (NEW)
│   ├── Badge.tsx (NEW)
│   ├── Input.tsx (NEW)
│   ├── Spinner.tsx (NEW)
│   ├── LoadingCard.tsx (NEW)
│   ├── LoadingPage.tsx (NEW)
│   ├── ErrorMessage.tsx (NEW)
│   ├── ErrorCard.tsx (NEW)
│   ├── Toast.tsx (NEW)
│   └── ToastContainer.tsx (NEW)
└── layout/
    ├── Sidebar.tsx (NEW)
    └── DashboardLayout.tsx (NEW)

hooks/
└── useToast.ts (NEW)

lib/
└── api.ts (existing, no changes needed)
```

### State Management Strategy

**Local Component State**: Each page manages its own state using React hooks
- Loading states: `const [loading, setLoading] = useState(false)`
- Data states: `const [data, setData] = useState<Type[]>([])`
- Error states: `const [error, setError] = useState<string | null>(null)`
- UI states: `const [isEditing, setIsEditing] = useState(false)`

**Global State**: Minimal global state via Context API
- Toast notifications: ToastContext provides showToast function
- User session: JWT token in localStorage, decoded on demand

**No Redux/Zustand**: The application complexity doesn't warrant a global state management library. Local state with prop drilling and context for cross-cutting concerns is sufficient.

### Routing and Navigation

**File-Based Routing**: Next.js App Router with nested layouts
- `/dashboard/*` routes wrapped in DashboardLayout
- DashboardLayout includes Sidebar and authentication check
- All dashboard pages are client components ('use client')

**Navigation Flow**:
1. User lands on `/` (landing page)
2. User authenticates at `/auth/login` or `/auth/register`
3. JWT token stored in localStorage
4. User redirected to `/dashboard`
5. Sidebar provides navigation to all feature pages
6. Unauthenticated access redirects to `/auth/login`

### Data Flow

**API Request Pattern**:
```
Component Mount → useEffect → API Call → Loading State → Success/Error State → Render
```

**Example Flow for Waste Tracker**:
1. WastePage component mounts
2. useEffect checks for token, redirects if missing
3. useEffect calls wasteAPI.getLogs() and wasteAPI.getAnalytics()
4. Loading state shows LoadingCard components
5. On success: data stored in state, UI renders with data
6. On error: error state shows ErrorCard with retry button

**Toast Notification Flow**:
1. User action triggers API call (e.g., profile update)
2. On success: `showToast({ type: 'success', message: 'Profile updated!' })`
3. On error: `showToast({ type: 'error', message: 'Update failed' })`
4. Toast appears in top-right corner, auto-dismisses after 3s

## Components and Interfaces

### Page Components

#### 1. Waste Tracker Page (`/dashboard/waste/page.tsx`)

**Purpose**: Display waste action logs and environmental impact metrics

**State**:
```typescript
const [logs, setLogs] = useState<WasteLog[]>([]);
const [analytics, setAnalytics] = useState<WasteAnalytics | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

**Layout**:
- Header with title and back button
- Summary cards row (2 cards: Total CO2 Saved, Total Actions)
- Waste logs list with action badges and timestamps
- Empty state when no logs exist
- Loading state with LoadingCard skeletons
- Error state with ErrorCard and retry

**Action Badge Colors**:
- store_properly: green (bg-green-100 text-green-700)
- eat_immediately: orange (bg-orange-100 text-orange-700)
- repurpose: blue (bg-blue-100 text-blue-700)
- compost: brown (bg-amber-100 text-amber-700)
- discard: red (bg-red-100 text-red-700)

#### 2. Scan History Page (`/dashboard/history/page.tsx`)

**Purpose**: Display all past food scans with filtering capabilities

**State**:
```typescript
const [scans, setScans] = useState<ScanResult[]>([]);
const [filteredScans, setFilteredScans] = useState<ScanResult[]>([]);
const [filter, setFilter] = useState<'all' | 'fresh' | 'slightly_aged' | 'rotten'>('all');
const [expandedId, setExpandedId] = useState<number | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

**Layout**:
- Header with title, back button, and filter dropdown
- Responsive grid (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
- Scan cards with image thumbnail, food name, status badge, risk score, date
- Click to expand card showing full details
- Empty state when no scans exist
- Loading state with LoadingCard grid
- Error state with ErrorCard and retry

**Status Badge Colors**:
- fresh: green (bg-green-100 text-green-700)
- slightly_aged: orange (bg-orange-100 text-orange-700)
- rotten: red (bg-red-100 text-red-700)

#### 3. User Profile Page (`/dashboard/profile/page.tsx`)

**Purpose**: View and edit user account information

**State**:
```typescript
const [user, setUser] = useState<User | null>(null);
const [isEditing, setIsEditing] = useState(false);
const [age, setAge] = useState<number>(0);
const [stats, setStats] = useState<UserStats | null>(null);
const [loading, setLoading] = useState(true);
const [saving, setSaving] = useState(false);
```

**Layout**:
- Header with title and back button
- Profile card with user information fields
- Edit mode toggle button
- Save and cancel buttons (visible in edit mode)
- Statistics card showing total scans, groceries, waste actions
- Loading state with LoadingPage
- Toast notifications for save success/error

**User Data Source**: JWT token decoded from localStorage
```typescript
const token = localStorage.getItem('token');
const decoded = JSON.parse(atob(token.split('.')[1]));
// decoded contains: { user_id, name, email, age, created_at }
```

#### 4. Settings Page (`/dashboard/settings/page.tsx`)

**Purpose**: Manage application preferences and account settings

**State**:
```typescript
const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
const [language, setLanguage] = useState<'en' | 'es' | 'fr'>('en');
const [emailNotifications, setEmailNotifications] = useState(true);
const [pushNotifications, setPushNotifications] = useState(false);
const [showDeleteModal, setShowDeleteModal] = useState(false);
```

**Layout**:
- Header with title and back button
- Settings sections in cards:
  - **Preferences**: Theme toggle, Language dropdown
  - **Notifications**: Email toggle, Push toggle
  - **Account**: Logout button, Delete account button
- Delete confirmation modal
- Settings saved to localStorage on change

**Settings Storage**:
```typescript
localStorage.setItem('theme', theme);
localStorage.setItem('language', language);
localStorage.setItem('emailNotifications', String(emailNotifications));
localStorage.setItem('pushNotifications', String(pushNotifications));
```

### Shared UI Components

#### 1. Button Component (`components/ui/Button.tsx`)

**Props**:
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}
```

**Variants**:
- primary: bg-green-600 hover:bg-green-700 text-white
- secondary: bg-gray-200 hover:bg-gray-300 text-gray-900
- danger: bg-red-600 hover:bg-red-700 text-white
- ghost: bg-transparent hover:bg-gray-100 text-gray-700

**Sizes**:
- sm: px-3 py-1.5 text-sm
- md: px-4 py-2 text-base
- lg: px-6 py-3 text-lg

**Loading State**: Shows Spinner component, disables button

#### 2. Card Component (`components/ui/Card.tsx`)

**Props**:
```typescript
interface CardProps {
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}
```

**Styling**: bg-white rounded-xl shadow-md p-6

#### 3. Modal Component (`components/ui/Modal.tsx`)

**Props**:
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}
```

**Features**:
- Fixed overlay with backdrop (bg-black/50)
- Centered content card
- Close button (X icon)
- Prevents body scroll when open (useEffect with document.body.style.overflow)
- Click outside to close

#### 4. Badge Component (`components/ui/Badge.tsx`)

**Props**:
```typescript
interface BadgeProps {
  children: React.ReactNode;
  variant: 'green' | 'orange' | 'red' | 'blue' | 'gray' | 'brown';
}
```

**Variants**:
- green: bg-green-100 text-green-700
- orange: bg-orange-100 text-orange-700
- red: bg-red-100 text-red-700
- blue: bg-blue-100 text-blue-700
- gray: bg-gray-100 text-gray-700
- brown: bg-amber-100 text-amber-700

**Styling**: px-3 py-1 rounded-full text-sm font-medium

#### 5. Input Component (`components/ui/Input.tsx`)

**Props**:
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}
```

**Features**:
- Label above input (optional)
- Error message below input (red text)
- Error state styling (border-red-500)
- Normal state styling (border-gray-300 focus:border-green-500)

#### 6. Spinner Component (`components/ui/Spinner.tsx`)

**Props**:
```typescript
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}
```

**Sizes**:
- sm: w-4 h-4
- md: w-8 h-8
- lg: w-12 h-12

**Animation**: animate-spin border-2 border-t-transparent rounded-full

#### 7. LoadingCard Component (`components/ui/LoadingCard.tsx`)

**Purpose**: Skeleton loading state for card content

**Implementation**: Card with animated pulse background
```typescript
<Card>
  <div className="animate-pulse space-y-4">
    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
  </div>
</Card>
```

#### 8. LoadingPage Component (`components/ui/LoadingPage.tsx`)

**Purpose**: Full-page loading state

**Implementation**: Centered Spinner with message
```typescript
<div className="flex flex-col items-center justify-center min-h-screen">
  <Spinner size="lg" />
  <p className="mt-4 text-gray-600">Loading...</p>
</div>
```

#### 9. ErrorMessage Component (`components/ui/ErrorMessage.tsx`)

**Props**:
```typescript
interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}
```

**Implementation**: Error icon + message + optional retry button

#### 10. ErrorCard Component (`components/ui/ErrorCard.tsx`)

**Props**:
```typescript
interface ErrorCardProps {
  message: string;
  onRetry: () => void;
}
```

**Implementation**: Card with error styling and retry button

#### 11. Toast Component (`components/ui/Toast.tsx`)

**Props**:
```typescript
interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  onClose: (id: string) => void;
}
```

**Type Colors**:
- success: bg-green-500 text-white
- error: bg-red-500 text-white
- info: bg-blue-500 text-white
- warning: bg-orange-500 text-white

**Features**:
- Auto-dismiss after 3 seconds (useEffect with setTimeout)
- Manual close button
- Slide-in animation from right
- Icons from lucide-react (CheckCircle, XCircle, Info, AlertTriangle)

#### 12. ToastContainer Component (`components/ui/ToastContainer.tsx`)

**Purpose**: Render all active toasts in a fixed position

**Implementation**:
```typescript
<div className="fixed top-4 right-4 z-50 space-y-2">
  {toasts.map(toast => <Toast key={toast.id} {...toast} />)}
</div>
```

### Layout Components

#### 1. Sidebar Component (`components/layout/Sidebar.tsx`)

**Props**:
```typescript
interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}
```

**Navigation Items**:
```typescript
const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/dashboard/scanner', icon: Scan, label: 'Scanner' },
  { href: '/dashboard/groceries', icon: Leaf, label: 'Groceries' },
  { href: '/dashboard/health', icon: Heart, label: 'Health' },
  { href: '/dashboard/waste', icon: Trash2, label: 'Waste Tracker' },
  { href: '/dashboard/history', icon: History, label: 'Scan History' },
  { href: '/dashboard/ph-analysis', icon: FlaskConical, label: 'pH Analysis' },
  { href: '/dashboard/smart-box', icon: Box, label: 'Smart Box' },
  { href: '/dashboard/analytics', icon: BarChart3, label: 'Analytics' },
  { href: '/dashboard/profile', icon: User, label: 'Profile' },
  { href: '/dashboard/settings', icon: Settings, label: 'Settings' },
];
```

**Responsive Behavior**:
- Desktop (lg+): Fixed sidebar, always visible (w-64)
- Mobile (<lg): Slide-in drawer, controlled by isOpen prop
- Hamburger menu button in header toggles sidebar on mobile

**Active Link Highlighting**: Use usePathname() to compare current route

#### 2. DashboardLayout Component (`components/layout/DashboardLayout.tsx`)

**Props**:
```typescript
interface DashboardLayoutProps {
  children: React.ReactNode;
}
```

**Features**:
- Authentication check on mount (redirect to /auth/login if no token)
- Sidebar state management (useState for mobile toggle)
- Flex layout: Sidebar + Main content area
- Header with logo, hamburger menu (mobile), logout button

**Implementation**:
```typescript
export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
    }
  }, [router]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1">
        {/* Header with hamburger menu */}
        <header className="bg-white shadow-sm lg:hidden">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu className="w-6 h-6" />
          </button>
        </header>
        {/* Main content */}
        <main>{children}</main>
      </div>
    </div>
  );
}
```

### Custom Hooks

#### useToast Hook (`hooks/useToast.ts`)

**Purpose**: Provide toast notification functionality

**Implementation**:
```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

const ToastContext = createContext<{
  toasts: Toast[];
  showToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
} | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { ...toast, id }]);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toasts, showToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used within ToastProvider');
  return context;
}
```

**Usage**:
```typescript
const { showToast } = useToast();
showToast({ type: 'success', message: 'Profile updated!' });
```

## Data Models

### TypeScript Interfaces

```typescript
// Waste Tracker
interface WasteLog {
  id: number;
  food_name: string;
  action: 'store_properly' | 'eat_immediately' | 'repurpose' | 'compost' | 'discard';
  co2_saved: number;
  created_at: string;
}

interface WasteAnalytics {
  total_co2_saved: number;
  total_actions: number;
  actions_by_type: Record<string, number>;
}

// Scan History
interface ScanResult {
  id: number;
  food_name: string;
  freshness_status: 'fresh' | 'slightly_aged' | 'rotten';
  risk_score: number;
  confidence: number;
  recommendation: string;
  image_url?: string;
  created_at: string;
}

// User Profile
interface User {
  id: number;
  name: string;
  email: string;
  age?: number;
  created_at: string;
}

interface UserStats {
  total_scans: number;
  total_groceries: number;
  total_waste_actions: number;
}

// Settings
interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  language: 'en' | 'es' | 'fr';
  emailNotifications: boolean;
  pushNotifications: boolean;
}

// Toast
interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}
```

### API Response Types

```typescript
// API responses match the interfaces above
// wasteAPI.getLogs() returns WasteLog[]
// wasteAPI.getAnalytics() returns WasteAnalytics
// scanAPI.getHistory() returns ScanResult[]
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Waste Log Field Completeness

*For any* list of waste logs, when rendered by the Waste Tracker page, each log item should display all required fields: food name, action type, CO2 saved, and timestamp.

**Validates: Requirements 1.6**

### Property 2: Scan Result Field Completeness

*For any* list of scan results, when rendered by the Scan History page, each scan item should display all required fields: food name, freshness status, risk score, and scan date.

**Validates: Requirements 2.4**

### Property 3: Descending Date Sort

*For any* list of items with timestamps (waste logs or scan results), when sorted by the application, the output list should be ordered with the most recent timestamp first and oldest timestamp last.

**Validates: Requirements 1.8, 2.8**

### Property 4: Freshness Filter Correctness

*For any* freshness status filter value (fresh, slightly_aged, rotten) and any list of scan results, the filtered output should contain only scan results matching the selected status, and should contain all scan results matching that status.

**Validates: Requirements 2.7**

### Property 5: Settings Persistence

*For any* settings change (theme, language, email notifications, push notifications), when the setting is toggled, the new value should be immediately persisted to localStorage and should be retrievable on subsequent page loads.

**Validates: Requirements 4.11**

### Property 6: Button Variant Styling

*For any* Button component variant value (primary, secondary, danger, ghost), the rendered button should have the CSS classes corresponding to that variant.

**Validates: Requirements 5.2**

### Property 7: Button Size Styling

*For any* Button component size value (sm, md, lg), the rendered button should have the CSS classes corresponding to that size.

**Validates: Requirements 5.3**

### Property 8: Badge Variant Styling

*For any* Badge component variant value (green, orange, red, blue, gray, brown), the rendered badge should have the CSS classes corresponding to that variant's background and text colors.

**Validates: Requirements 5.14**

### Property 9: Card Props Rendering

*For any* combination of Card component props (title, children, footer), all provided props should be rendered in the output, and optional props that are not provided should not cause rendering errors.

**Validates: Requirements 5.8**

### Property 10: Input Type Attribute

*For any* Input component type value (text, number, email, password), the rendered input element should have the type attribute set to that value.

**Validates: Requirements 5.17**

### Property 11: Input Props Rendering

*For any* Input component with label and placeholder props, both the label and placeholder should be present in the rendered output.

**Validates: Requirements 5.19**

### Property 12: Navigation Items Completeness

*For any* list of navigation items provided to the Sidebar component, all items should be rendered as clickable links with their corresponding labels and icons.

**Validates: Requirements 6.3, 6.5**

### Property 13: Active Link Highlighting

*For any* current route path, the Sidebar component should apply active styling to exactly one navigation link—the link whose href matches the current path.

**Validates: Requirements 6.4**

### Property 14: Spinner Size Styling

*For any* Spinner component size value (sm, md, lg), the rendered spinner should have the CSS classes corresponding to that size.

**Validates: Requirements 7.3**

### Property 15: Spinner Color Styling

*For any* Spinner component color value, the rendered spinner should have the border color CSS classes corresponding to that color.

**Validates: Requirements 7.4**

### Property 16: Error Message Transformation

*For any* API error response, the displayed error message should be user-friendly (not containing technical error codes or stack traces), and should provide actionable information when possible.

**Validates: Requirements 8.9**

### Property 17: Toast Type Styling

*For any* Toast component type value (success, error, info, warning), the rendered toast should have the background color and icon corresponding to that type.

**Validates: Requirements 9.3**

### Property 18: Toast Queue Management

*For any* sequence of showToast calls, all toasts should be added to the queue and displayed, with each toast receiving a unique ID and being independently dismissible.

**Validates: Requirements 9.10**

### Property 19: Toast Container Rendering

*For any* list of active toasts, the ToastContainer should render all toasts in a stacked layout without overlap or rendering errors.

**Validates: Requirements 9.12**

### Property 20: Touch Target Minimum Size

*For any* interactive element (button, link, input), the rendered element should have a minimum touch target size of 44x44 pixels on mobile viewports to ensure accessibility.

**Validates: Requirements 10.6**

### Property 21: Image Container Constraint

*For any* image element rendered in the application, the image should scale to fit within its container without causing horizontal overflow or breaking the layout.

**Validates: Requirements 10.8**

## Error Handling

### Error Categories

**1. Network Errors**
- API request failures (timeout, connection refused, DNS errors)
- Handling: Display ErrorCard with retry button, log error to console
- User message: "Unable to connect to server. Please check your connection and try again."

**2. Authentication Errors**
- 401 Unauthorized responses
- Handling: Remove token from localStorage, redirect to /auth/login
- User message: "Your session has expired. Please log in again."

**3. Authorization Errors**
- 403 Forbidden responses
- Handling: Display ErrorCard with message, no retry
- User message: "You don't have permission to access this resource."

**4. Validation Errors**
- 400 Bad Request with validation details
- Handling: Display field-level error messages in forms
- User message: Show specific validation error from API response

**5. Server Errors**
- 500 Internal Server Error
- Handling: Display ErrorCard with retry button
- User message: "Something went wrong on our end. Please try again later."

**6. Not Found Errors**
- 404 Not Found
- Handling: Display ErrorCard with back button
- User message: "The requested resource was not found."

**7. Client-Side Errors**
- Invalid JWT token format
- Missing required data
- Handling: Log error, redirect to appropriate page or show error state
- User message: Context-specific message

### Error Handling Patterns

**API Call Pattern**:
```typescript
const [data, setData] = useState<Type[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getData();
      setData(response.data);
    } catch (err: any) {
      console.error('Fetch failed:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        router.push('/auth/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to load data');
      }
    } finally {
      setLoading(false);
    }
  };
  
  fetchData();
}, []);
```

**Form Submission Pattern**:
```typescript
const handleSubmit = async () => {
  try {
    setSaving(true);
    await api.updateData(formData);
    showToast({ type: 'success', message: 'Saved successfully!' });
  } catch (err: any) {
    console.error('Save failed:', err);
    showToast({ 
      type: 'error', 
      message: err.response?.data?.detail || 'Failed to save changes' 
    });
  } finally {
    setSaving(false);
  }
};
```

**Retry Pattern**:
```typescript
const handleRetry = () => {
  setError(null);
  fetchData(); // Call the original fetch function again
};

// In render:
{error && <ErrorCard message={error} onRetry={handleRetry} />}
```

### Error Boundaries

While React Error Boundaries are not implemented in this feature (they require class components or a library), the error handling strategy ensures that:
- All async operations are wrapped in try-catch blocks
- Errors are caught at the component level and displayed appropriately
- The application never crashes due to unhandled promise rejections
- Console logging provides debugging information in development

### Graceful Degradation

**Empty States**: When no data is available (not an error, just empty), display helpful empty states with calls-to-action:
- Waste Tracker: "No waste actions logged yet. Start by scanning food items!"
- Scan History: "No scans yet. Upload your first food image to get started!"
- Profile: Show default values or placeholders

**Partial Data**: If some API calls succeed and others fail, display the successful data and show error messages for failed sections:
- Waste Tracker: If analytics fails but logs succeed, show logs and error message where analytics would be

**Offline Handling**: While offline detection is not implemented, the error messages for network failures guide users to check their connection.

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and integration points
- Specific user interactions (button clicks, form submissions)
- Edge cases (empty arrays, null values, boundary conditions)
- Component integration (Modal opening, Toast dismissal)
- Error scenarios (401 redirects, validation errors)

**Property-Based Tests**: Verify universal properties across all inputs
- Component rendering with random prop combinations
- Data transformation and filtering with generated datasets
- Sorting and ordering with random data
- CSS class mapping for all variant values

### Property-Based Testing Configuration

**Library**: fast-check (for TypeScript/JavaScript)
- Installation: `npm install --save-dev fast-check @types/fast-check`
- Minimum 100 iterations per property test
- Each test tagged with reference to design property

**Test Tag Format**:
```typescript
// Feature: complete-frontend-pages, Property 1: Waste Log Field Completeness
test('waste logs display all required fields', () => {
  fc.assert(
    fc.property(fc.array(wasteLogArbitrary), (logs) => {
      // Test implementation
    }),
    { numRuns: 100 }
  );
});
```

### Unit Testing Strategy

**Component Tests** (using React Testing Library):
- Button: Test variants, sizes, disabled state, loading state, click handlers
- Card: Test with/without title, with/without footer, children rendering
- Modal: Test open/close, backdrop click, body scroll prevention
- Badge: Test all color variants render correctly
- Input: Test types, label, placeholder, error state
- Spinner: Test sizes and colors
- Toast: Test auto-dismiss timing, manual close, animation classes
- Sidebar: Test navigation, active link, mobile toggle, logout
- DashboardLayout: Test auth check, redirect, sidebar integration

**Page Tests**:
- Waste Tracker: Test loading state, data display, empty state, error state, retry
- Scan History: Test loading, data display, filtering, sorting, expand/collapse, empty state
- Profile: Test data display, edit mode, save/cancel, toast notifications
- Settings: Test setting toggles, localStorage persistence, logout, delete modal

**Integration Tests**:
- Navigation flow: Dashboard → Page → Back to Dashboard
- Authentication: Unauthenticated access redirects to login
- Toast system: Multiple toasts display correctly
- Error handling: 401 errors trigger logout and redirect

### Test Organization

```
__tests__/
├── components/
│   ├── ui/
│   │   ├── Button.test.tsx
│   │   ├── Card.test.tsx
│   │   ├── Modal.test.tsx
│   │   ├── Badge.test.tsx
│   │   ├── Input.test.tsx
│   │   ├── Spinner.test.tsx
│   │   ├── Toast.test.tsx
│   │   └── ToastContainer.test.tsx
│   └── layout/
│       ├── Sidebar.test.tsx
│       └── DashboardLayout.test.tsx
├── pages/
│   ├── waste.test.tsx
│   ├── history.test.tsx
│   ├── profile.test.tsx
│   └── settings.test.tsx
├── hooks/
│   └── useToast.test.tsx
└── properties/
    ├── sorting.property.test.tsx
    ├── filtering.property.test.tsx
    ├── component-props.property.test.tsx
    ├── styling.property.test.tsx
    └── toast-queue.property.test.tsx
```

### Property Test Examples

**Property 1: Waste Log Field Completeness**
```typescript
// Feature: complete-frontend-pages, Property 1: Waste Log Field Completeness
import fc from 'fast-check';
import { render } from '@testing-library/react';

const wasteLogArbitrary = fc.record({
  id: fc.integer(),
  food_name: fc.string({ minLength: 1 }),
  action: fc.constantFrom('store_properly', 'eat_immediately', 'repurpose', 'compost', 'discard'),
  co2_saved: fc.float({ min: 0, max: 10 }),
  created_at: fc.date().map(d => d.toISOString()),
});

test('waste logs display all required fields', () => {
  fc.assert(
    fc.property(fc.array(wasteLogArbitrary), (logs) => {
      const { container } = render(<WasteLogList logs={logs} />);
      
      logs.forEach(log => {
        expect(container.textContent).toContain(log.food_name);
        expect(container.textContent).toContain(log.action);
        expect(container.textContent).toContain(String(log.co2_saved));
        // Timestamp should be formatted and displayed
        expect(container.textContent).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/);
      });
    }),
    { numRuns: 100 }
  );
});
```

**Property 3: Descending Date Sort**
```typescript
// Feature: complete-frontend-pages, Property 3: Descending Date Sort
test('items are sorted by date descending', () => {
  fc.assert(
    fc.property(
      fc.array(fc.record({
        id: fc.integer(),
        created_at: fc.date().map(d => d.toISOString()),
      })),
      (items) => {
        const sorted = sortByDateDescending(items);
        
        for (let i = 0; i < sorted.length - 1; i++) {
          const current = new Date(sorted[i].created_at);
          const next = new Date(sorted[i + 1].created_at);
          expect(current.getTime()).toBeGreaterThanOrEqual(next.getTime());
        }
      }
    ),
    { numRuns: 100 }
  );
});
```

**Property 6: Button Variant Styling**
```typescript
// Feature: complete-frontend-pages, Property 6: Button Variant Styling
test('button variants apply correct CSS classes', () => {
  fc.assert(
    fc.property(
      fc.constantFrom('primary', 'secondary', 'danger', 'ghost'),
      (variant) => {
        const { container } = render(<Button variant={variant}>Click</Button>);
        const button = container.querySelector('button');
        
        const expectedClasses = {
          primary: ['bg-green-600', 'text-white'],
          secondary: ['bg-gray-200', 'text-gray-900'],
          danger: ['bg-red-600', 'text-white'],
          ghost: ['bg-transparent', 'text-gray-700'],
        };
        
        expectedClasses[variant].forEach(cls => {
          expect(button?.className).toContain(cls);
        });
      }
    ),
    { numRuns: 100 }
  );
});
```

### Unit Test Examples

**Button Component**:
```typescript
describe('Button', () => {
  test('renders children', () => {
    const { getByText } = render(<Button>Click me</Button>);
    expect(getByText('Click me')).toBeInTheDocument();
  });

  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    const { getByText } = render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('shows spinner when loading', () => {
    const { container } = render(<Button loading>Click</Button>);
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  test('is disabled when disabled prop is true', () => {
    const { getByRole } = render(<Button disabled>Click</Button>);
    expect(getByRole('button')).toBeDisabled();
  });
});
```

**Waste Tracker Page**:
```typescript
describe('WastePage', () => {
  test('displays loading state initially', () => {
    render(<WastePage />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays waste logs after successful fetch', async () => {
    const mockLogs = [
      { id: 1, food_name: 'Apple', action: 'store_properly', co2_saved: 0.5, created_at: '2024-01-01' }
    ];
    jest.spyOn(wasteAPI, 'getLogs').mockResolvedValue({ data: mockLogs });
    
    render(<WastePage />);
    
    await waitFor(() => {
      expect(screen.getByText('Apple')).toBeInTheDocument();
    });
  });

  test('displays error state on fetch failure', async () => {
    jest.spyOn(wasteAPI, 'getLogs').mockRejectedValue(new Error('Network error'));
    
    render(<WastePage />);
    
    await waitFor(() => {
      expect(screen.getByText(/unable to connect/i)).toBeInTheDocument();
    });
  });

  test('displays empty state when no logs exist', async () => {
    jest.spyOn(wasteAPI, 'getLogs').mockResolvedValue({ data: [] });
    
    render(<WastePage />);
    
    await waitFor(() => {
      expect(screen.getByText(/no waste actions logged/i)).toBeInTheDocument();
    });
  });
});
```

### Testing Tools

- **React Testing Library**: Component rendering and interaction testing
- **Jest**: Test runner and assertion library
- **fast-check**: Property-based testing library
- **MSW (Mock Service Worker)**: API mocking for integration tests (optional)
- **@testing-library/user-event**: Realistic user interaction simulation

### Coverage Goals

- **Unit Test Coverage**: 80%+ line coverage for components and pages
- **Property Test Coverage**: All 21 correctness properties implemented as property tests
- **Integration Test Coverage**: Critical user flows (auth, navigation, data operations)

### Continuous Integration

Tests should run on every commit:
```bash
npm test -- --coverage --watchAll=false
```

Property tests with 100 iterations ensure robust validation across a wide range of inputs, catching edge cases that unit tests might miss.

