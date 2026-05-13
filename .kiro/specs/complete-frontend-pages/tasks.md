# Implementation Plan: Complete Frontend Pages

## Overview

This implementation plan covers the development of 4 new pages (Waste Tracker, Scan History, Profile, Settings), 12 shared UI components, 2 layout components (Sidebar, DashboardLayout), and a toast notification system. The implementation follows an incremental approach: shared components first, then layout components, then pages, with testing integrated throughout.

## Tasks

- [x] 1. Set up shared UI components foundation
  - [x] 1.1 Create Button component with variants and states
    - Implement Button component at src/components/ui/Button.tsx
    - Support variants: primary, secondary, danger, ghost
    - Support sizes: sm, md, lg
    - Support disabled and loading states with spinner
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 1.2 Write property test for Button variant styling
    - **Property 6: Button Variant Styling**
    - **Validates: Requirements 5.2**

  - [ ]* 1.3 Write property test for Button size styling
    - **Property 7: Button Size Styling**
    - **Validates: Requirements 5.3**

  - [ ]* 1.4 Write unit tests for Button component
    - Test click handlers, disabled state, loading state
    - Test children rendering
    - _Requirements: 5.1, 5.4, 5.5_

- [x] 2. Create Card and Badge components
  - [x] 2.1 Create Card component with flexible props
    - Implement Card component at src/components/ui/Card.tsx
    - Support title, children, footer, and className props
    - Apply consistent styling: bg-white, rounded-xl, shadow-md, p-6
    - _Requirements: 5.6, 5.7, 5.8_

  - [ ]* 2.2 Write property test for Card props rendering
    - **Property 9: Card Props Rendering**
    - **Validates: Requirements 5.8**

  - [x] 2.3 Create Badge component with color variants
    - Implement Badge component at src/components/ui/Badge.tsx
    - Support variants: green, orange, red, blue, gray, brown
    - Apply rounded-full styling with appropriate colors
    - _Requirements: 5.13, 5.14, 5.15_

  - [ ]* 2.4 Write property test for Badge variant styling
    - **Property 8: Badge Variant Styling**
    - **Validates: Requirements 5.14**

- [x] 3. Create Input and Modal components
  - [x] 3.1 Create Input component with validation support
    - Implement Input component at src/components/ui/Input.tsx
    - Support types: text, number, email, password
    - Support label, placeholder, and error props
    - Display error state with red border and error message
    - _Requirements: 5.16, 5.17, 5.18, 5.19_

  - [ ]* 3.2 Write property test for Input type attribute
    - **Property 10: Input Type Attribute**
    - **Validates: Requirements 5.17**

  - [ ]* 3.3 Write property test for Input props rendering
    - **Property 11: Input Props Rendering**
    - **Validates: Requirements 5.19**

  - [x] 3.4 Create Modal component with overlay and close handling
    - Implement Modal component at src/components/ui/Modal.tsx
    - Display centered overlay with backdrop
    - Include close button and onClose callback
    - Prevent body scroll when open using useEffect
    - Support click outside to close
    - _Requirements: 5.9, 5.10, 5.11, 5.12_

  - [ ]* 3.5 Write unit tests for Modal component
    - Test open/close behavior, backdrop click, body scroll prevention
    - _Requirements: 5.10, 5.11, 5.12_

- [x] 4. Create loading state components
  - [x] 4.1 Create Spinner component with size and color variants
    - Implement Spinner component at src/components/ui/Spinner.tsx
    - Support sizes: sm, md, lg (w-4 h-4, w-8 h-8, w-12 h-12)
    - Support color prop for border color
    - Use animate-spin with border-2 and border-t-transparent
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 4.2 Write property test for Spinner size styling
    - **Property 14: Spinner Size Styling**
    - **Validates: Requirements 7.3**

  - [ ]* 4.3 Write property test for Spinner color styling
    - **Property 15: Spinner Color Styling**
    - **Validates: Requirements 7.4**

  - [x] 4.4 Create LoadingCard component with skeleton animation
    - Implement LoadingCard component at src/components/ui/LoadingCard.tsx
    - Use Card wrapper with animate-pulse skeleton elements
    - _Requirements: 7.5, 7.6_

  - [x] 4.5 Create LoadingPage component with centered spinner
    - Implement LoadingPage component at src/components/ui/LoadingPage.tsx
    - Display centered Spinner with loading message
    - Use flex layout with min-h-screen
    - _Requirements: 7.7, 7.8_

- [x] 5. Create error state components
  - [x] 5.1 Create ErrorMessage component with retry option
    - Implement ErrorMessage component at src/components/ui/ErrorMessage.tsx
    - Display error icon and error text
    - Support optional retry button with onRetry callback
    - Use red color scheme
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 5.2 Create ErrorCard component with card layout
    - Implement ErrorCard component at src/components/ui/ErrorCard.tsx
    - Display error message in card layout
    - Include retry button that calls failed operation
    - _Requirements: 8.5, 8.6, 8.7_

  - [ ]* 5.3 Write property test for error message transformation
    - **Property 16: Error Message Transformation**
    - **Validates: Requirements 8.9**

- [x] 6. Checkpoint - Verify shared UI components
  - Ensure all shared UI components render correctly
  - Verify component props and variants work as expected
  - Ask the user if questions arise

- [x] 7. Create toast notification system
  - [x] 7.1 Create Toast component with auto-dismiss
    - Implement Toast component at src/components/ui/Toast.tsx
    - Support types: success, error, info, warning
    - Use color-coded backgrounds with appropriate icons
    - Auto-dismiss after 3 seconds using useEffect with setTimeout
    - Include manual close button
    - Add slide-in animation from right
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [ ]* 7.2 Write property test for Toast type styling
    - **Property 17: Toast Type Styling**
    - **Validates: Requirements 9.3**

  - [x] 7.3 Create ToastContainer component for stacked layout
    - Implement ToastContainer component at src/components/ui/ToastContainer.tsx
    - Render all active toasts in fixed top-right position
    - Use stacked layout with space-y-2
    - _Requirements: 9.11, 9.12_

  - [ ]* 7.4 Write property test for ToastContainer rendering
    - **Property 19: Toast Container Rendering**
    - **Validates: Requirements 9.12**

  - [x] 7.5 Create useToast hook with toast queue management
    - Implement useToast hook at src/hooks/useToast.ts
    - Create ToastContext with toasts array and showToast function
    - Implement ToastProvider with state management
    - Generate unique IDs for each toast
    - Provide removeToast function for dismissal
    - _Requirements: 9.8, 9.9, 9.10_

  - [ ]* 7.6 Write property test for toast queue management
    - **Property 18: Toast Queue Management**
    - **Validates: Requirements 9.10**

  - [x] 7.7 Integrate ToastProvider in root layout
    - Wrap app content with ToastProvider in app/layout.tsx
    - Include ToastContainer in the provider
    - _Requirements: 9.13_

  - [ ]* 7.8 Write unit tests for useToast hook
    - Test showToast function, toast queue, removeToast
    - _Requirements: 9.9, 9.10_

- [x] 8. Create navigation sidebar component
  - [x] 8.1 Create Sidebar component with navigation items
    - Implement Sidebar component at src/components/layout/Sidebar.tsx
    - Display NutriLens AI logo and name at top
    - Include navigation links for all 11 dashboard pages
    - Use lucide-react icons for each navigation item
    - Implement active link highlighting using usePathname()
    - Include logout button at bottom
    - Support isOpen and onClose props for mobile drawer
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

  - [ ]* 8.2 Write property test for navigation items completeness
    - **Property 12: Navigation Items Completeness**
    - **Validates: Requirements 6.3, 6.5**

  - [ ]* 8.3 Write property test for active link highlighting
    - **Property 13: Active Link Highlighting**
    - **Validates: Requirements 6.4**

  - [x] 8.4 Implement responsive sidebar behavior
    - Fixed positioning on desktop (w-64)
    - Slide-in drawer on mobile with backdrop
    - _Requirements: 6.7, 6.13_

  - [ ]* 8.5 Write unit tests for Sidebar component
    - Test navigation, active link, mobile toggle, logout
    - _Requirements: 6.3, 6.4, 6.6, 6.7_

- [x] 9. Create dashboard layout wrapper
  - [x] 9.1 Create DashboardLayout component with authentication
    - Implement DashboardLayout component at src/components/layout/DashboardLayout.tsx
    - Check for JWT token on mount, redirect to login if missing
    - Manage sidebar state for mobile toggle
    - Render Sidebar and main content in flex layout
    - Include header with hamburger menu for mobile
    - _Requirements: 6.9, 6.10, 6.11, 6.12_

  - [x] 9.2 Apply DashboardLayout to dashboard pages
    - Update app/dashboard/layout.tsx to use DashboardLayout
    - Ensure all dashboard pages are wrapped
    - _Requirements: 6.11_

  - [ ]* 9.3 Write unit tests for DashboardLayout component
    - Test auth check, redirect, sidebar integration
    - _Requirements: 6.12_

- [x] 10. Checkpoint - Verify layout and navigation
  - Ensure sidebar navigation works correctly
  - Verify authentication check redirects properly
  - Test responsive behavior on mobile and desktop
  - Ask the user if questions arise

- [x] 11. Create Waste Tracker page
  - [x] 11.1 Implement Waste Tracker page with data fetching
    - Create page at app/dashboard/waste/page.tsx
    - Fetch waste logs using wasteAPI.getLogs()
    - Fetch analytics using wasteAPI.getAnalytics()
    - Implement loading, error, and empty states
    - Display summary cards for total CO2 saved and total actions
    - Display waste logs list with action badges and timestamps
    - Sort logs by timestamp descending
    - Use color-coded badges for action types
    - Include back button to dashboard
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13_

  - [ ]* 11.2 Write property test for waste log field completeness
    - **Property 1: Waste Log Field Completeness**
    - **Validates: Requirements 1.6**

  - [ ]* 11.3 Write property test for descending date sort
    - **Property 3: Descending Date Sort**
    - **Validates: Requirements 1.8**

  - [ ]* 11.4 Write unit tests for Waste Tracker page
    - Test loading state, data display, empty state, error state, retry
    - _Requirements: 1.9, 1.10, 1.11_

- [x] 12. Create Scan History page
  - [x] 12.1 Implement Scan History page with filtering
    - Create page at app/dashboard/history/page.tsx
    - Fetch scan history using scanAPI.getHistory()
    - Display scans in responsive grid layout (1/2/3 columns)
    - Show image thumbnails, food name, status badge, risk score, date
    - Implement filter dropdown for freshness status
    - Filter scans based on selected status
    - Sort scans by date descending
    - Implement click to expand for full details
    - Implement loading, error, and empty states
    - Include back button to dashboard
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14_

  - [ ]* 12.2 Write property test for scan result field completeness
    - **Property 2: Scan Result Field Completeness**
    - **Validates: Requirements 2.4**

  - [ ]* 12.3 Write property test for freshness filter correctness
    - **Property 4: Freshness Filter Correctness**
    - **Validates: Requirements 2.7**

  - [ ]* 12.4 Write unit tests for Scan History page
    - Test loading, data display, filtering, sorting, expand/collapse, empty state
    - _Requirements: 2.7, 2.9, 2.10, 2.11, 2.12_

- [x] 13. Create User Profile page
  - [x] 13.1 Implement User Profile page with edit functionality
    - Create page at app/dashboard/profile/page.tsx
    - Retrieve user data from JWT token in localStorage
    - Display read-only fields: name, email, created_at
    - Display editable field: age (in edit mode)
    - Implement edit mode toggle
    - Implement save button that updates profile via API
    - Implement cancel button that discards changes
    - Display account statistics (total scans, groceries, waste actions)
    - Show success/error toast notifications on save
    - Include back button to dashboard
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14, 3.15, 3.16_

  - [ ]* 13.2 Write unit tests for User Profile page
    - Test data display, edit mode, save/cancel, toast notifications
    - _Requirements: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13_

- [x] 14. Create Settings page
  - [x] 14.1 Implement Settings page with preferences management
    - Create page at app/dashboard/settings/page.tsx
    - Organize settings in sections: Preferences, Notifications, Account
    - Implement theme preference toggle (Light, Dark, System)
    - Implement language preference dropdown (English, Spanish, French)
    - Implement notification toggles (Email, Push)
    - Implement logout button that removes token and redirects
    - Implement delete account button with confirmation modal
    - Save preference changes to localStorage immediately
    - Load current settings from localStorage on mount
    - Include back button to dashboard
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14_

  - [ ]* 14.2 Write property test for settings persistence
    - **Property 5: Settings Persistence**
    - **Validates: Requirements 4.11**

  - [ ]* 14.3 Write unit tests for Settings page
    - Test setting toggles, localStorage persistence, logout, delete modal
    - _Requirements: 4.6, 4.7, 4.8, 4.9, 4.10, 4.11_

- [x] 15. Checkpoint - Verify all pages functionality
  - Test all 4 new pages for correct data display
  - Verify loading and error states work properly
  - Test navigation between pages
  - Ensure responsive design works on mobile and desktop
  - Ask the user if questions arise

- [x] 16. Implement responsive design enhancements
  - [x] 16.1 Apply responsive breakpoints across all pages
    - Use Tailwind CSS breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
    - Implement single-column layouts on mobile (< 768px)
    - Implement multi-column layouts on tablet/desktop (>= 768px)
    - Use responsive font sizes (text-sm mobile, text-base desktop)
    - Use responsive padding/margins (px-4 mobile, px-8 desktop)
    - _Requirements: 10.1, 10.2, 10.3, 10.5, 10.9_

  - [x] 16.2 Ensure touch-friendly interactive elements
    - Verify all buttons, links, inputs have minimum 44x44px touch targets
    - Test all interactive elements on touch devices
    - _Requirements: 10.6, 10.10_

  - [ ]* 16.3 Write property test for touch target minimum size
    - **Property 20: Touch Target Minimum Size**
    - **Validates: Requirements 10.6**

  - [x] 16.4 Implement responsive image handling
    - Ensure images scale appropriately without overflow
    - Use object-fit and max-width constraints
    - _Requirements: 10.8_

  - [ ]* 16.5 Write property test for image container constraint
    - **Property 21: Image Container Constraint**
    - **Validates: Requirements 10.8**

  - [x] 16.6 Test responsive design on multiple viewports
    - Test on mobile (375px), tablet (768px), desktop (1280px)
    - Verify sidebar collapses to hamburger menu on mobile
    - _Requirements: 10.4, 10.7_

- [ ] 17. Integrate with existing pages
  - [x] 17.1 Apply consistent styling across all pages
    - Use same color scheme (green primary, gray secondary)
    - Use same typography (font-sans, consistent heading sizes)
    - Use same spacing patterns (p-6 for cards, gap-6 for grids)
    - Use same shadow styles (shadow-md for cards)
    - Use same border radius (rounded-xl for cards)
    - Use same button styles (rounded-lg, hover transitions)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.7_

  - [x] 17.2 Ensure consistent API patterns
    - Use same API client patterns (try-catch, loading states)
    - Use same authentication check (useEffect with token check)
    - _Requirements: 11.8, 11.9_

  - [x] 17.3 Add new pages to dashboard module cards
    - Update main dashboard page to include links to new pages
    - Add Waste Tracker, History, Profile, Settings cards
    - _Requirements: 11.10_

- [ ] 18. Final integration and polish
  - [ ] 18.1 Verify code quality and organization
    - Ensure clear directory structure (components/ui, components/layout, hooks)
    - Verify TypeScript types for all components
    - Check for meaningful variable and function names
    - Add JSDoc comments for complex functions
    - Verify no code duplication
    - Check consistent formatting (2-space indentation, single quotes)
    - Ensure all error cases handled
    - Verify React best practices (key props, dependency arrays)
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10_

  - [ ] 18.2 Test complete user flows
    - Test authentication flow (login → dashboard → pages)
    - Test navigation flow (dashboard → pages → back)
    - Test error handling (401 redirects, network errors)
    - Test toast notifications across different actions
    - _Requirements: 8.10, 9.14, 9.15_

- [ ] 19. Final checkpoint - Complete feature verification
  - Run all tests and ensure they pass
  - Verify all 4 pages are functional and accessible
  - Verify all 12 UI components work correctly
  - Verify layout components and navigation work properly
  - Verify toast notification system works across the app
  - Verify responsive design on all viewport sizes
  - Ensure integration with existing pages is seamless
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples, edge cases, and integration points
- The implementation follows a bottom-up approach: shared components → layout → pages
- All components use TypeScript with proper type definitions
- All components use Tailwind CSS for styling consistency
- The toast notification system is integrated early to support user feedback in later pages
