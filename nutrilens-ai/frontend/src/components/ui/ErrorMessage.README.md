# ErrorMessage Component

## Overview

The `ErrorMessage` component is a reusable UI component for displaying error messages with an optional retry action. It provides consistent error feedback across the NutriLens AI application.

## Location

`src/components/ui/ErrorMessage.tsx`

## Requirements

This component satisfies the following requirements from the complete-frontend-pages specification:

- **Requirement 8.1**: Create ErrorMessage component at src/components/ui/ErrorMessage.tsx
- **Requirement 8.2**: Display error icon and error text
- **Requirement 8.3**: Support optional retry button with onRetry callback
- **Requirement 8.4**: Use red color scheme for error indication

## Props

```typescript
interface ErrorMessageProps {
  message: string;      // The error message to display
  onRetry?: () => void; // Optional callback function for retry action
}
```

### Prop Details

- **message** (required): The error message text to display to the user. Should be user-friendly and actionable.
- **onRetry** (optional): Callback function that will be called when the user clicks the retry button. If not provided, the retry button will not be rendered.

## Features

- **Error Icon**: Displays a red AlertCircle icon from lucide-react
- **Error Message**: Shows the error text in red with medium font weight
- **Optional Retry Button**: Conditionally renders a retry button with danger variant styling
- **Centered Layout**: Content is centered both horizontally and vertically
- **Red Color Scheme**: Uses red colors (text-red-500, text-red-700, bg-red-600) for error indication
- **Responsive**: Works well on all screen sizes

## Usage

### Basic Error (No Retry)

```tsx
import { ErrorMessage } from '@/components/ui/ErrorMessage';

function MyComponent() {
  return (
    <ErrorMessage message="Unable to load data. Please try again later." />
  );
}
```

### Error with Retry Button

```tsx
import { ErrorMessage } from '@/components/ui/ErrorMessage';

function MyComponent() {
  const handleRetry = () => {
    // Retry logic here
    fetchData();
  };

  return (
    <ErrorMessage 
      message="Failed to connect to server. Please check your connection."
      onRetry={handleRetry}
    />
  );
}
```

### In a Page with Error State

```tsx
import { useState, useEffect } from 'react';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { LoadingPage } from '@/components/ui/LoadingPage';

function WastePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getData();
      setData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRetry = () => {
    fetchData();
  };

  if (loading) return <LoadingPage />;
  if (error) return <ErrorMessage message={error} onRetry={handleRetry} />;

  return <div>{/* Render data */}</div>;
}
```

## Styling

The component uses Tailwind CSS classes for styling:

- **Container**: `flex flex-col items-center justify-center p-6 text-center`
- **Icon**: `w-12 h-12 text-red-500 mb-4`
- **Message**: `text-red-700 text-lg font-medium mb-4`
- **Button**: Uses the `Button` component with `variant="danger"`

## Accessibility

- The error message is displayed as a paragraph (`<p>`) for proper semantic HTML
- The retry button is a proper `<button>` element with accessible text
- The icon provides visual reinforcement of the error state
- Text is large enough (text-lg) for readability
- High contrast red colors ensure visibility

## Design Patterns

### User-Friendly Error Messages

Always provide clear, actionable error messages:

✅ Good:
- "Unable to connect to server. Please check your connection and try again."
- "Your session has expired. Please log in again."
- "Failed to load waste tracker data. Please try again."

❌ Bad:
- "Error 500"
- "Network error"
- "Something went wrong"

### When to Show Retry Button

Show the retry button when:
- The error is temporary (network issues, server timeouts)
- The user can take action to resolve it
- Retrying the operation makes sense

Don't show the retry button when:
- The error is permanent (404 Not Found, 403 Forbidden)
- The user needs to take a different action (e.g., log in again)
- Retrying won't help

## Related Components

- **ErrorCard**: A card-based error display component (wraps ErrorMessage in a Card)
- **Button**: The button component used for the retry action
- **LoadingPage**: Used to show loading state before error state
- **Toast**: Used for temporary error notifications

## Testing

The component includes comprehensive unit tests in `__tests__/components/ui/ErrorMessage.test.tsx` covering:

- Basic rendering of message and icon
- Conditional rendering of retry button
- Click handler functionality
- Red color scheme validation
- Accessibility features
- Edge cases (empty messages, long messages, special characters)

Run tests with:
```bash
npm test ErrorMessage.test.tsx
```

## Examples

See `ErrorMessage.example.tsx` for visual examples of the component in various contexts.

## Browser Support

Works in all modern browsers that support:
- CSS Flexbox
- ES6+ JavaScript
- React 18+

## Version History

- **v1.0.0** (2024): Initial implementation for complete-frontend-pages feature
