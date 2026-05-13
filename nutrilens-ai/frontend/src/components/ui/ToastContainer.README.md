# ToastContainer Component

## Overview

The `ToastContainer` component renders all active toast notifications in a fixed position at the top-right corner of the screen. It manages the display of multiple toasts in a stacked layout with proper spacing.

## Features

- Fixed positioning in top-right corner (top-4 right-4)
- Stacked layout with vertical spacing (space-y-2)
- High z-index (z-50) to appear above other content
- Renders multiple Toast components simultaneously
- Handles toast dismissal through callback

## Props

```typescript
interface ToastData {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

interface ToastContainerProps {
  toasts: ToastData[];
  onClose: (id: string) => void;
}
```

### `toasts`
- **Type**: `ToastData[]`
- **Required**: Yes
- **Description**: Array of toast objects to display

### `onClose`
- **Type**: `(id: string) => void`
- **Required**: Yes
- **Description**: Callback function to handle toast dismissal

## Usage

The ToastContainer is typically used with the `useToast` hook and ToastProvider:

```tsx
import { ToastContainer } from '@/components/ui/ToastContainer';

function App() {
  const [toasts, setToasts] = useState([]);
  
  const handleClose = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <div>
      {/* Your app content */}
      <ToastContainer toasts={toasts} onClose={handleClose} />
    </div>
  );
}
```

## Integration with ToastProvider

The ToastContainer is designed to work seamlessly with the ToastProvider context:

```tsx
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

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
```

## Styling

The component uses Tailwind CSS classes:
- `fixed`: Fixed positioning
- `top-4 right-4`: Positioned 1rem from top and right edges
- `z-50`: High z-index to appear above other content
- `space-y-2`: 0.5rem vertical spacing between toasts

## Accessibility

- Each Toast component within the container has `role="alert"` for screen readers
- Toasts are keyboard accessible with close buttons
- Auto-dismiss after 3 seconds with manual close option

## Requirements Validation

**Validates Requirements:**
- 9.11: ToastContainer component created at correct path
- 9.12: Renders all active toasts in stacked layout
- Fixed top-right position for consistent placement
- Proper spacing between multiple toasts

## Related Components

- `Toast`: Individual toast notification component
- `useToast`: Hook for managing toast state and display
