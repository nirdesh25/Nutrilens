# Toast Component

A notification component that displays temporary messages with auto-dismiss functionality.

## Features

- **Four Types**: success, error, info, warning
- **Color-Coded**: Each type has a distinct background color and icon
- **Auto-Dismiss**: Automatically closes after 3 seconds
- **Manual Close**: Includes a close button for immediate dismissal
- **Slide-In Animation**: Animates in from the right side
- **Accessible**: Includes proper ARIA attributes and keyboard navigation

## Props

```typescript
interface ToastProps {
  id: string;                                    // Unique identifier for the toast
  type: 'success' | 'error' | 'info' | 'warning'; // Toast type
  message: string;                               // Message to display
  onClose: (id: string) => void;                 // Callback when toast is closed
}
```

## Usage

### Basic Usage

```tsx
import { Toast } from '@/components/ui/Toast';

function MyComponent() {
  const [toasts, setToasts] = useState([]);

  const showToast = (type, message) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, type, message }]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <>
      <button onClick={() => showToast('success', 'Saved successfully!')}>
        Save
      </button>

      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            id={toast.id}
            type={toast.type}
            message={toast.message}
            onClose={removeToast}
          />
        ))}
      </div>
    </>
  );
}
```

### With useToast Hook (Recommended)

For a more integrated solution, use the `useToast` hook (see `hooks/useToast.ts`):

```tsx
import { useToast } from '@/hooks/useToast';

function MyComponent() {
  const { showToast } = useToast();

  const handleSave = async () => {
    try {
      await saveData();
      showToast({ type: 'success', message: 'Saved successfully!' });
    } catch (error) {
      showToast({ type: 'error', message: 'Failed to save' });
    }
  };

  return <button onClick={handleSave}>Save</button>;
}
```

## Toast Types

### Success
- **Color**: Green background (`bg-green-500`)
- **Icon**: CheckCircle
- **Use Case**: Successful operations, confirmations

### Error
- **Color**: Red background (`bg-red-500`)
- **Icon**: XCircle
- **Use Case**: Failed operations, validation errors

### Info
- **Color**: Blue background (`bg-blue-500`)
- **Icon**: Info
- **Use Case**: Informational messages, tips

### Warning
- **Color**: Orange background (`bg-orange-500`)
- **Icon**: AlertTriangle
- **Use Case**: Warnings, cautions, important notices

## Behavior

### Auto-Dismiss
- Toasts automatically close after **3 seconds**
- The timer starts when the toast is mounted
- The timer is cleaned up if the toast is manually closed or unmounted

### Manual Close
- Click the X button to immediately dismiss the toast
- Clicking close will call the `onClose` callback with the toast's ID

### Animation
- Toasts slide in from the right with a smooth animation
- Animation class: `animate-slide-in-right`
- Duration: 0.3 seconds

## Styling

### Layout
- **Min Width**: 300px
- **Max Width**: 28rem (448px)
- **Padding**: 1rem (16px)
- **Border Radius**: 0.5rem (8px)
- **Shadow**: Large shadow for depth

### Positioning
The Toast component itself doesn't handle positioning. Wrap toasts in a container with fixed positioning:

```tsx
<div className="fixed top-4 right-4 z-50 space-y-2">
  {/* Toasts here */}
</div>
```

## Accessibility

- **Role**: `alert` - Announces to screen readers
- **Keyboard**: Close button is keyboard accessible
- **ARIA Label**: Close button has `aria-label="Close notification"`
- **Text Size**: `text-sm` for readability
- **Color Contrast**: White text on colored backgrounds meets WCAG standards

## Requirements Validation

This component validates the following requirements:

- **9.1**: Toast component created at `src/components/ui/Toast.tsx`
- **9.2**: Displays message with icon in fixed position (top-right corner)
- **9.3**: Supports types: success, error, info, warning
- **9.4**: Uses color-coded backgrounds with appropriate icons
- **9.5**: Auto-dismisses after 3 seconds using useEffect with setTimeout
- **9.6**: Includes manual close button
- **9.7**: Adds slide-in animation from right

## Examples

See `Toast.example.tsx` for a complete working example with all toast types.

## Testing

Unit tests are available in `__tests__/components/ui/Toast.test.tsx` covering:
- Basic rendering
- All toast types and styling
- Auto-dismiss functionality
- Manual close functionality
- Animation and styling
- Accessibility
- Edge cases
