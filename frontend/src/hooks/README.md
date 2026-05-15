# useToast Hook

A React hook for managing toast notifications with queue support.

## Features

- ✅ Toast queue management for multiple simultaneous notifications
- ✅ Unique ID generation for each toast
- ✅ Support for 4 toast types: success, error, info, warning
- ✅ Context-based state management
- ✅ TypeScript support with full type safety
- ✅ Simple API with showToast and removeToast functions

## Installation

The hook is already included in the project. No additional installation needed.

## Setup

Wrap your application with `ToastProvider` in your root layout:

```tsx
// app/layout.tsx
import { ToastProvider } from '@/hooks/useToast';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ToastProvider>
          {children}
        </ToastProvider>
      </body>
    </html>
  );
}
```

## Usage

### Basic Usage

```tsx
import { useToast } from '@/hooks/useToast';

function MyComponent() {
  const { showToast } = useToast();

  const handleClick = () => {
    showToast({
      type: 'success',
      message: 'Operation completed successfully!',
    });
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

### Toast Types

```tsx
// Success toast (green)
showToast({ type: 'success', message: 'Profile updated!' });

// Error toast (red)
showToast({ type: 'error', message: 'Failed to save changes' });

// Info toast (blue)
showToast({ type: 'info', message: 'New feature available' });

// Warning toast (orange)
showToast({ type: 'warning', message: 'Please verify your email' });
```

### API Call Example

```tsx
const { showToast } = useToast();

const saveData = async () => {
  try {
    await api.updateProfile(data);
    showToast({ type: 'success', message: 'Profile updated!' });
  } catch (error) {
    showToast({ type: 'error', message: 'Update failed' });
  }
};
```

### Multiple Toasts

The hook automatically manages a queue of toasts. You can show multiple toasts simultaneously:

```tsx
const { showToast } = useToast();

const processSteps = () => {
  showToast({ type: 'info', message: 'Starting process...' });
  showToast({ type: 'success', message: 'Step 1 completed' });
  showToast({ type: 'success', message: 'Step 2 completed' });
};
```

### Manual Toast Removal

```tsx
const { showToast, removeToast, toasts } = useToast();

// Show a toast and get its ID
const handleShow = () => {
  showToast({ type: 'info', message: 'Processing...' });
};

// Remove a specific toast by ID
const handleRemove = () => {
  if (toasts.length > 0) {
    removeToast(toasts[0].id);
  }
};
```

## API Reference

### `useToast()`

Returns an object with the following properties:

#### `toasts: Toast[]`

Array of currently active toasts.

```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}
```

#### `showToast(toast: Omit<Toast, 'id'>): void`

Displays a new toast notification. The ID is automatically generated.

**Parameters:**
- `toast.type`: The type of toast ('success' | 'error' | 'info' | 'warning')
- `toast.message`: The message to display

**Example:**
```tsx
showToast({ type: 'success', message: 'Saved!' });
```

#### `removeToast(id: string): void`

Removes a toast from the queue by its ID.

**Parameters:**
- `id`: The unique ID of the toast to remove

**Example:**
```tsx
removeToast('abc123xyz');
```

## TypeScript Types

```typescript
interface Toast {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

interface ToastContextType {
  toasts: Toast[];
  showToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}
```

## Error Handling

The hook will throw an error if used outside of `ToastProvider`:

```typescript
// ❌ This will throw an error
function MyComponent() {
  const { showToast } = useToast(); // Error: useToast must be used within ToastProvider
}

// ✅ This is correct
function App() {
  return (
    <ToastProvider>
      <MyComponent />
    </ToastProvider>
  );
}
```

## Implementation Details

- **Unique ID Generation**: Uses `Math.random().toString(36).substring(2, 11)` to generate unique IDs
- **Queue Management**: Toasts are stored in an array and can be displayed simultaneously
- **State Management**: Uses React Context API with useState for state management
- **Type Safety**: Full TypeScript support with proper type definitions

## Related Components

This hook is designed to work with:
- `Toast` component (src/components/ui/Toast.tsx)
- `ToastContainer` component (src/components/ui/ToastContainer.tsx)

These components handle the visual rendering and auto-dismiss functionality.

## Requirements Validation

This hook validates the following requirements:
- **Requirement 9.8**: Create useToast hook at src/hooks/useToast.ts ✅
- **Requirement 9.9**: Provide showToast function to display notifications ✅
- **Requirement 9.10**: Manage toast queue for multiple simultaneous notifications ✅
