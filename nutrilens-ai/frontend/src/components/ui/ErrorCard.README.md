# ErrorCard Component

A card-based error display component that shows error messages with a retry button in a card layout.

## Features

- Displays error messages in a card layout with white background, rounded corners, and shadow
- Shows an error icon (AlertCircle) with red color scheme
- Includes a retry button that calls the failed operation again
- Red border for clear error indication
- Centered content with consistent spacing
- Fully accessible with keyboard support

## Props

```typescript
interface ErrorCardProps {
  message: string;      // The error message to display
  onRetry: () => void;  // Callback function to retry the failed operation
}
```

## Usage

```tsx
import { ErrorCard } from '@/components/ui/ErrorCard';

function MyComponent() {
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setError(null);
      const response = await api.getData();
      // Handle success
    } catch (err) {
      setError('Failed to load data. Please try again.');
    }
  };

  if (error) {
    return <ErrorCard message={error} onRetry={fetchData} />;
  }

  return <div>Content...</div>;
}
```

## Examples

### Basic Error Card

```tsx
<ErrorCard 
  message="Failed to load data" 
  onRetry={() => fetchData()} 
/>
```

### Network Error

```tsx
<ErrorCard 
  message="Unable to connect to server. Please check your connection and try again." 
  onRetry={handleRetry} 
/>
```

### API Error

```tsx
<ErrorCard 
  message="Something went wrong on our end. Please try again later." 
  onRetry={retryApiCall} 
/>
```

## Styling

The component uses:
- Card layout with white background (`bg-white`)
- Rounded corners (`rounded-xl`)
- Shadow for depth (`shadow-md`)
- Red border for error indication (`border-2 border-red-200`)
- Red icon color (`text-red-500`)
- Red text color (`text-red-700`)
- Danger variant button (red background)

## Accessibility

- Retry button is keyboard accessible
- Proper focus management
- Semantic HTML structure
- Clear visual hierarchy

## Requirements

Validates:
- **Requirement 8.5**: Create ErrorCard component at src/components/ui/ErrorCard.tsx
- **Requirement 8.6**: Display error message in card layout
- **Requirement 8.7**: Include retry button that calls failed operation

## Related Components

- `ErrorMessage`: Inline error display without card layout
- `Card`: Base card component used for layout
- `Button`: Button component with danger variant for retry action
