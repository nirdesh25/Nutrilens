# DashboardLayout Component

## Overview

The `DashboardLayout` component is the main layout wrapper for all authenticated dashboard pages in the NutriLens AI application. It provides consistent navigation, authentication checks, and responsive layout structure.

## Features

### 1. Authentication Check
- Checks for JWT token in localStorage on component mount
- Redirects to `/auth/login` if no token is found
- Prevents rendering of content until authentication is verified

### 2. Sidebar Navigation
- Integrates the `Sidebar` component for navigation
- Manages sidebar state for mobile toggle functionality
- Sidebar is always visible on desktop (lg+ breakpoint)
- Sidebar slides in as a drawer on mobile devices

### 3. Responsive Header
- Mobile-only header with hamburger menu button
- Displays app name and menu toggle
- Hidden on desktop where sidebar is always visible
- Sticky positioning for easy access

### 4. Flex Layout
- Uses flexbox for responsive layout structure
- Sidebar on the left, main content on the right
- Main content area takes remaining space (flex-1)
- Background color: gray-50 for visual separation

## Usage

### In Next.js App Router

The component is used as a layout wrapper in `/app/dashboard/layout.tsx`:

```tsx
import DashboardLayout from '@/components/layout/DashboardLayout';

export default function Layout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
```

This automatically wraps all pages under `/dashboard/*` with the layout.

### Direct Usage (if needed)

```tsx
import DashboardLayout from '@/components/layout/DashboardLayout';

export default function MyPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <h1>My Page Content</h1>
        {/* Your page content here */}
      </div>
    </DashboardLayout>
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| children | React.ReactNode | Yes | The page content to render inside the layout |

## Implementation Details

### Authentication Flow

1. Component mounts
2. `useEffect` checks for token in localStorage
3. If no token: redirects to `/auth/login`
4. If token exists: sets `isAuthenticated` to true
5. Content renders only after authentication check

### Sidebar State Management

- `sidebarOpen` state controls sidebar visibility on mobile
- Hamburger menu button sets `sidebarOpen` to true
- Sidebar's `onClose` callback sets `sidebarOpen` to false
- Desktop: sidebar is always visible (CSS handles this)

### Responsive Behavior

**Desktop (lg+):**
- Sidebar is fixed and always visible
- No header (hamburger menu hidden)
- Sidebar takes 256px width (w-64)
- Main content fills remaining space

**Mobile (<lg):**
- Sidebar hidden by default
- Header visible with hamburger menu
- Clicking hamburger opens sidebar as drawer
- Backdrop overlay when sidebar is open
- Clicking backdrop or close button closes sidebar

## Styling

### Layout Structure
```
<div className="flex min-h-screen bg-gray-50">
  <Sidebar /> {/* Fixed on desktop, drawer on mobile */}
  <div className="flex-1 flex flex-col">
    <header /> {/* Mobile only */}
    <main>{children}</main>
  </div>
</div>
```

### Key Classes
- `flex min-h-screen`: Full height flex container
- `bg-gray-50`: Light gray background
- `flex-1`: Main content takes remaining space
- `lg:hidden`: Header hidden on desktop
- `sticky top-0 z-30`: Header sticks to top on mobile

## Requirements Validation

This component satisfies the following requirements:

- **Requirement 6.9**: DashboardLayout component created at correct path
- **Requirement 6.10**: Renders Sidebar and page content in flex layout
- **Requirement 6.11**: Wraps all dashboard pages via Next.js layout
- **Requirement 6.12**: Checks for user session on mount, redirects if not authenticated

## Related Components

- **Sidebar**: Navigation component with links and logout button
- **Dashboard Pages**: All pages under `/dashboard/*` use this layout

## Notes

- The component uses `'use client'` directive for client-side rendering
- Authentication check happens on every mount (page navigation)
- No loading state shown during auth check (returns null)
- Sidebar component handles its own responsive behavior
- Layout is minimal and delegates most functionality to Sidebar

## Testing

See `__tests__/components/layout/DashboardLayout.test.tsx` for unit tests covering:
- Authentication redirect behavior
- Sidebar state management
- Layout structure rendering
- Mobile menu toggle functionality
