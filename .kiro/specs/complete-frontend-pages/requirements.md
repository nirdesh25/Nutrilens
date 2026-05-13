# Requirements Document

## Introduction

This specification defines the requirements for completing the remaining frontend pages and shared components for the NutriLens AI application. The application is a production-ready full-stack platform for food freshness analysis and waste reduction. The backend with 40+ endpoints, complete database schema, and JWT authentication is fully implemented. The frontend has landing, auth, dashboard, and 7 feature pages (scanner, groceries, health, smart-box, ph-analysis, analytics, waste). This feature will complete the remaining pages: waste tracker, scan history, user profile, settings, and implement shared components including navigation, loading states, error handling, and toast notifications.

## Glossary

- **Frontend_Application**: The Next.js 14 client-side application built with React and TypeScript
- **Waste_Tracker_Page**: A page displaying waste action logs with CO2 impact metrics
- **Scan_History_Page**: A page showing all past food scan results with filtering capabilities
- **Profile_Page**: A page for viewing and editing user account information
- **Settings_Page**: A page for managing application preferences and account settings
- **Shared_Components**: Reusable UI components used across multiple pages
- **Navigation_Component**: A sidebar navigation menu for the dashboard layout
- **Toast_System**: A notification system for displaying success and error messages
- **Loading_State**: Visual feedback indicating data is being fetched or processed
- **Error_State**: Visual feedback when an error occurs or data cannot be loaded
- **API_Client**: The axios-based HTTP client in lib/api.ts for backend communication
- **Dashboard_Layout**: The authenticated area of the application containing all feature pages
- **Existing_Pages**: The currently implemented pages (landing, auth, dashboard, scanner, groceries, health, smart-box, ph-analysis, analytics)
- **Backend_API**: The FastAPI server with 40+ endpoints providing data and functionality
- **User_Session**: The authenticated state managed via JWT tokens in localStorage

## Requirements

### Requirement 1: Waste Tracker Page

**User Story:** As a user, I want to view my waste action history and environmental impact, so that I can track my food waste reduction progress over time.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a waste tracker page at /dashboard/waste
2. WHEN the Waste_Tracker_Page loads, THE Frontend_Application SHALL fetch waste logs from the Backend_API using wasteAPI.getLogs()
3. WHEN the Waste_Tracker_Page loads, THE Frontend_Application SHALL fetch analytics data from the Backend_API using wasteAPI.getAnalytics()
4. THE Waste_Tracker_Page SHALL display a summary card showing total CO2 saved in kilograms
5. THE Waste_Tracker_Page SHALL display a summary card showing total waste actions logged
6. THE Waste_Tracker_Page SHALL display a list of waste action logs with food name, action type, CO2 saved, and timestamp
7. THE Waste_Tracker_Page SHALL use color-coded badges for action types (store_properly: green, eat_immediately: orange, repurpose: blue, compost: brown, discard: red)
8. THE Waste_Tracker_Page SHALL sort waste logs by timestamp in descending order
9. WHEN no waste logs exist, THE Waste_Tracker_Page SHALL display an empty state message with a call-to-action to scan food
10. THE Waste_Tracker_Page SHALL display a Loading_State while fetching data
11. IF the Backend_API returns an error, THEN THE Waste_Tracker_Page SHALL display an Error_State with retry option
12. THE Waste_Tracker_Page SHALL include a back button to return to the dashboard
13. THE Waste_Tracker_Page SHALL use the same header and styling patterns as Existing_Pages

### Requirement 2: Scan History Page

**User Story:** As a user, I want to view all my past food scans with filtering options, so that I can review previous freshness analyses and track patterns.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a scan history page at /dashboard/history
2. WHEN the Scan_History_Page loads, THE Frontend_Application SHALL fetch scan history from the Backend_API using scanAPI.getHistory()
3. THE Scan_History_Page SHALL display scan results in a grid layout with image thumbnails
4. THE Scan_History_Page SHALL display food name, freshness status, risk score, and scan date for each result
5. THE Scan_History_Page SHALL use color-coded status badges (fresh: green, slightly_aged: orange, rotten: red)
6. THE Scan_History_Page SHALL include a filter dropdown for freshness status (All, Fresh, Slightly Aged, Rotten)
7. WHEN a filter is selected, THE Scan_History_Page SHALL display only matching scan results
8. THE Scan_History_Page SHALL sort scans by date in descending order
9. WHEN a scan card is clicked, THE Scan_History_Page SHALL expand to show full details including confidence and recommendation
10. WHEN no scans exist, THE Scan_History_Page SHALL display an empty state with a call-to-action to scan food
11. THE Scan_History_Page SHALL display a Loading_State while fetching data
12. IF the Backend_API returns an error, THEN THE Scan_History_Page SHALL display an Error_State with retry option
13. THE Scan_History_Page SHALL include a back button to return to the dashboard
14. THE Scan_History_Page SHALL use responsive grid layout (1 column mobile, 2 columns tablet, 3 columns desktop)

### Requirement 3: User Profile Page

**User Story:** As a user, I want to view and edit my account information, so that I can keep my profile up to date.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a profile page at /dashboard/profile
2. WHEN the Profile_Page loads, THE Frontend_Application SHALL retrieve user data from the JWT token stored in localStorage
3. THE Profile_Page SHALL display user name in a read-only field
4. THE Profile_Page SHALL display user email in a read-only field
5. THE Profile_Page SHALL display user age in an editable number input field
6. THE Profile_Page SHALL display account creation date in a read-only field
7. THE Profile_Page SHALL include an edit mode toggle button
8. WHEN edit mode is enabled, THE Profile_Page SHALL make the age field editable
9. THE Profile_Page SHALL include a save button that is only enabled in edit mode
10. WHEN the save button is clicked, THE Frontend_Application SHALL send updated data to the Backend_API
11. WHEN profile update succeeds, THE Profile_Page SHALL display a success Toast_System notification
12. IF profile update fails, THEN THE Profile_Page SHALL display an error Toast_System notification
13. THE Profile_Page SHALL include a cancel button that discards changes and exits edit mode
14. THE Profile_Page SHALL display account statistics (total scans, total groceries, total waste actions)
15. THE Profile_Page SHALL include a back button to return to the dashboard
16. THE Profile_Page SHALL use card-based layout consistent with Existing_Pages

### Requirement 4: Settings Page

**User Story:** As a user, I want to manage my application preferences and account settings, so that I can customize my experience.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a settings page at /dashboard/settings
2. THE Settings_Page SHALL display settings organized in sections (Preferences, Notifications, Account)
3. THE Settings_Page SHALL include a theme preference toggle (Light, Dark, System) in the Preferences section
4. THE Settings_Page SHALL include a language preference dropdown (English, Spanish, French) in the Preferences section
5. THE Settings_Page SHALL include notification toggles (Email Notifications, Push Notifications) in the Notifications section
6. THE Settings_Page SHALL include a logout button in the Account section
7. WHEN the logout button is clicked, THE Frontend_Application SHALL remove the JWT token from localStorage
8. WHEN the logout button is clicked, THE Frontend_Application SHALL redirect to the landing page
9. THE Settings_Page SHALL include a delete account button in the Account section with warning styling
10. WHEN the delete account button is clicked, THE Settings_Page SHALL display a confirmation modal
11. THE Settings_Page SHALL save preference changes to localStorage immediately when toggled
12. THE Settings_Page SHALL display current setting values on page load
13. THE Settings_Page SHALL include a back button to return to the dashboard
14. THE Settings_Page SHALL use card-based sections with clear visual separation

### Requirement 5: Shared UI Components

**User Story:** As a developer, I want reusable UI components, so that I can maintain consistency and reduce code duplication across pages.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a Button component at src/components/ui/Button.tsx
2. THE Button component SHALL support variants (primary, secondary, danger, ghost)
3. THE Button component SHALL support sizes (sm, md, lg)
4. THE Button component SHALL support disabled state with reduced opacity
5. THE Button component SHALL support loading state with spinner icon
6. THE Frontend_Application SHALL create a Card component at src/components/ui/Card.tsx
7. THE Card component SHALL render a white background with rounded corners and shadow
8. THE Card component SHALL accept title, children, and optional footer props
9. THE Frontend_Application SHALL create a Modal component at src/components/ui/Modal.tsx
10. THE Modal component SHALL display content in a centered overlay with backdrop
11. THE Modal component SHALL include close button and support onClose callback
12. THE Modal component SHALL prevent body scroll when open
13. THE Frontend_Application SHALL create a Badge component at src/components/ui/Badge.tsx
14. THE Badge component SHALL support color variants (green, orange, red, blue, gray)
15. THE Badge component SHALL render text with appropriate background and text colors
16. THE Frontend_Application SHALL create an Input component at src/components/ui/Input.tsx
17. THE Input component SHALL support text, number, email, and password types
18. THE Input component SHALL display error state with red border and error message
19. THE Input component SHALL support label and placeholder props

### Requirement 6: Navigation Component

**User Story:** As a user, I want a consistent navigation menu, so that I can easily access different sections of the application.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a Sidebar component at src/components/layout/Sidebar.tsx
2. THE Sidebar component SHALL display the NutriLens AI logo and name at the top
3. THE Sidebar component SHALL include navigation links for all dashboard pages (Dashboard, Scanner, Groceries, Health, Waste Tracker, History, pH Analysis, Smart Box, Analytics, Profile, Settings)
4. THE Sidebar component SHALL highlight the active page link based on current route
5. THE Sidebar component SHALL display icons from lucide-react for each navigation item
6. THE Sidebar component SHALL include a logout button at the bottom
7. THE Sidebar component SHALL be collapsible on mobile devices with a hamburger menu button
8. WHEN a navigation link is clicked, THE Frontend_Application SHALL navigate to the corresponding page
9. THE Frontend_Application SHALL create a DashboardLayout component at src/components/layout/DashboardLayout.tsx
10. THE DashboardLayout component SHALL render the Sidebar component and page content in a flex layout
11. THE DashboardLayout component SHALL wrap all Dashboard_Layout pages
12. THE DashboardLayout component SHALL check for User_Session on mount and redirect to login if not authenticated
13. THE Sidebar component SHALL use fixed positioning on desktop and slide-in drawer on mobile

### Requirement 7: Loading States

**User Story:** As a user, I want to see loading indicators, so that I know the application is processing my request.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a Spinner component at src/components/ui/Spinner.tsx
2. THE Spinner component SHALL render an animated circular spinner
3. THE Spinner component SHALL support sizes (sm, md, lg)
4. THE Spinner component SHALL support color variants matching the theme
5. THE Frontend_Application SHALL create a LoadingCard component at src/components/ui/LoadingCard.tsx
6. THE LoadingCard component SHALL display skeleton loading animation for card content
7. THE Frontend_Application SHALL create a LoadingPage component at src/components/ui/LoadingPage.tsx
8. THE LoadingPage component SHALL display a centered spinner with loading message
9. THE Frontend_Application SHALL display Loading_State components while API requests are pending
10. THE Frontend_Application SHALL replace Loading_State with actual content when data loads

### Requirement 8: Error States

**User Story:** As a user, I want clear error messages, so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create an ErrorMessage component at src/components/ui/ErrorMessage.tsx
2. THE ErrorMessage component SHALL display an error icon and error text
3. THE ErrorMessage component SHALL support optional retry button with onRetry callback
4. THE ErrorMessage component SHALL use red color scheme for error indication
5. THE Frontend_Application SHALL create an ErrorCard component at src/components/ui/ErrorCard.tsx
6. THE ErrorCard component SHALL display error message in a card layout
7. THE ErrorCard component SHALL include a retry button that calls the failed operation again
8. THE Frontend_Application SHALL display Error_State components when API requests fail
9. THE Frontend_Application SHALL display user-friendly error messages instead of technical error codes
10. IF the Backend_API returns a 401 error, THEN THE Frontend_Application SHALL redirect to the login page

### Requirement 9: Toast Notification System

**User Story:** As a user, I want to see temporary notifications for actions, so that I receive feedback without interrupting my workflow.

#### Acceptance Criteria

1. THE Frontend_Application SHALL create a Toast component at src/components/ui/Toast.tsx
2. THE Toast component SHALL display a message with icon in a fixed position (top-right corner)
3. THE Toast component SHALL support types (success, error, info, warning)
4. THE Toast component SHALL use color-coded backgrounds (success: green, error: red, info: blue, warning: orange)
5. THE Toast component SHALL automatically dismiss after 3 seconds
6. THE Toast component SHALL include a close button for manual dismissal
7. THE Toast component SHALL animate in from the right and fade out on dismissal
8. THE Frontend_Application SHALL create a useToast hook at src/hooks/useToast.ts
9. THE useToast hook SHALL provide showToast function to display notifications
10. THE useToast hook SHALL manage toast queue for multiple simultaneous notifications
11. THE Frontend_Application SHALL create a ToastContainer component at src/components/ui/ToastContainer.tsx
12. THE ToastContainer component SHALL render all active toasts in a stacked layout
13. THE Frontend_Application SHALL include ToastContainer in the root layout
14. THE Frontend_Application SHALL display success Toast_System when data operations succeed
15. THE Frontend_Application SHALL display error Toast_System when data operations fail

### Requirement 10: Responsive Design

**User Story:** As a user, I want the application to work on all devices, so that I can access it from my phone, tablet, or computer.

#### Acceptance Criteria

1. THE Frontend_Application SHALL use Tailwind CSS responsive breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
2. THE Frontend_Application SHALL display single-column layouts on mobile devices (width < 768px)
3. THE Frontend_Application SHALL display multi-column layouts on tablet and desktop devices (width >= 768px)
4. THE Navigation_Component SHALL collapse to a hamburger menu on mobile devices
5. THE Frontend_Application SHALL use responsive font sizes (text-sm on mobile, text-base on desktop)
6. THE Frontend_Application SHALL ensure touch targets are at least 44x44 pixels on mobile
7. THE Frontend_Application SHALL test all pages on mobile (375px), tablet (768px), and desktop (1280px) viewports
8. THE Frontend_Application SHALL ensure images scale appropriately without overflow
9. THE Frontend_Application SHALL use responsive padding and margins (px-4 on mobile, px-8 on desktop)
10. THE Frontend_Application SHALL ensure all interactive elements are accessible on touch devices

### Requirement 11: Integration with Existing Pages

**User Story:** As a developer, I want new pages to integrate seamlessly with existing pages, so that the application feels cohesive.

#### Acceptance Criteria

1. THE Frontend_Application SHALL use the same color scheme as Existing_Pages (green primary, gray secondary)
2. THE Frontend_Application SHALL use the same typography as Existing_Pages (font-sans, consistent heading sizes)
3. THE Frontend_Application SHALL use the same spacing patterns as Existing_Pages (p-6 for cards, gap-6 for grids)
4. THE Frontend_Application SHALL use the same shadow styles as Existing_Pages (shadow-md for cards)
5. THE Frontend_Application SHALL use the same border radius as Existing_Pages (rounded-xl for cards)
6. THE Frontend_Application SHALL use the same icon library as Existing_Pages (lucide-react)
7. THE Frontend_Application SHALL use the same button styles as Existing_Pages (rounded-lg, hover transitions)
8. THE Frontend_Application SHALL use the same API_Client patterns as Existing_Pages (try-catch, loading states)
9. THE Frontend_Application SHALL use the same authentication check as Existing_Pages (useEffect with token check)
10. THE Frontend_Application SHALL add new pages to the dashboard module cards on the main dashboard page

### Requirement 12: Code Quality and Organization

**User Story:** As a developer, I want well-organized and maintainable code, so that the codebase is easy to understand and extend.

#### Acceptance Criteria

1. THE Frontend_Application SHALL organize components in a clear directory structure (components/ui, components/layout, hooks)
2. THE Frontend_Application SHALL use TypeScript for all new components with proper type definitions
3. THE Frontend_Application SHALL use functional components with React hooks
4. THE Frontend_Application SHALL extract reusable logic into custom hooks
5. THE Frontend_Application SHALL use meaningful variable and function names
6. THE Frontend_Application SHALL include JSDoc comments for complex functions
7. THE Frontend_Application SHALL avoid code duplication by using Shared_Components
8. THE Frontend_Application SHALL use consistent formatting (2-space indentation, single quotes)
9. THE Frontend_Application SHALL handle all error cases with appropriate error messages
10. THE Frontend_Application SHALL use React best practices (key props in lists, proper dependency arrays)

