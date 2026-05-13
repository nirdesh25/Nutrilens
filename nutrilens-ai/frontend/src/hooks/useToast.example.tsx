/**
 * Example usage of the useToast hook
 * 
 * This file demonstrates how to use the useToast hook in your components.
 * DO NOT import this file in production code - it's for reference only.
 */

'use client';

import { useToast } from './useToast';

// Example 1: Basic usage in a component
export function ExampleComponent() {
  const { showToast } = useToast();

  const handleSuccess = () => {
    showToast({
      type: 'success',
      message: 'Operation completed successfully!',
    });
  };

  const handleError = () => {
    showToast({
      type: 'error',
      message: 'Something went wrong. Please try again.',
    });
  };

  const handleInfo = () => {
    showToast({
      type: 'info',
      message: 'Here is some helpful information.',
    });
  };

  const handleWarning = () => {
    showToast({
      type: 'warning',
      message: 'Please be careful with this action.',
    });
  };

  return (
    <div>
      <button onClick={handleSuccess}>Show Success Toast</button>
      <button onClick={handleError}>Show Error Toast</button>
      <button onClick={handleInfo}>Show Info Toast</button>
      <button onClick={handleWarning}>Show Warning Toast</button>
    </div>
  );
}

// Example 2: Usage in an API call
export function ProfileUpdateExample() {
  const { showToast } = useToast();

  const updateProfile = async (data: any) => {
    try {
      // Simulate API call
      await fetch('/api/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      });

      showToast({
        type: 'success',
        message: 'Profile updated successfully!',
      });
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Failed to update profile. Please try again.',
      });
    }
  };

  return <div>{/* Your form component */}</div>;
}

// Example 3: Multiple toasts (queue management)
export function MultipleToastsExample() {
  const { showToast } = useToast();

  const showMultipleToasts = () => {
    // All three toasts will be displayed simultaneously
    showToast({ type: 'info', message: 'Processing request...' });
    showToast({ type: 'success', message: 'Step 1 completed' });
    showToast({ type: 'success', message: 'Step 2 completed' });
  };

  return <button onClick={showMultipleToasts}>Show Multiple Toasts</button>;
}

// Example 4: Setup in root layout
/**
 * In your app/layout.tsx, wrap your application with ToastProvider:
 * 
 * import { ToastProvider } from '@/hooks/useToast';
 * 
 * export default function RootLayout({ children }) {
 *   return (
 *     <html>
 *       <body>
 *         <ToastProvider>
 *           {children}
 *         </ToastProvider>
 *       </body>
 *     </html>
 *   );
 * }
 */
