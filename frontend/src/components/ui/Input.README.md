# Input Component

A flexible and accessible input component with built-in validation support, label, and error message display.

## Features

- ✅ Supports all standard HTML input types (text, number, email, password, etc.)
- ✅ Optional label above the input field
- ✅ Error state with red border and error message display
- ✅ Placeholder text support
- ✅ Full TypeScript support with type safety
- ✅ Accessible with proper ARIA attributes
- ✅ Responsive and mobile-friendly
- ✅ Consistent styling with Tailwind CSS
- ✅ Focus state with green ring (matches app theme)

## Props

The Input component extends all standard HTML input attributes and adds the following custom props:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | `undefined` | Optional label text displayed above the input |
| `error` | `string` | `undefined` | Error message displayed below the input. When present, applies error styling |
| `className` | `string` | `''` | Additional CSS classes to apply to the input element |
| All HTML input props | - | - | Supports all standard input attributes (type, placeholder, value, onChange, etc.) |

## Usage

### Basic Text Input

```tsx
import { Input } from '@/components/ui/Input';

<Input
  type="text"
  placeholder="Enter your name"
/>
```

### Input with Label

```tsx
<Input
  type="text"
  label="Full Name"
  placeholder="John Doe"
/>
```

### Input with Error State

```tsx
<Input
  type="email"
  label="Email Address"
  placeholder="user@example.com"
  error="Invalid email format"
/>
```

### Controlled Input with Validation

```tsx
const [email, setEmail] = useState('');
const [emailError, setEmailError] = useState('');

const validateEmail = (value: string) => {
  if (!value) {
    setEmailError('Email is required');
  } else if (!/\S+@\S+\.\S+/.test(value)) {
    setEmailError('Invalid email format');
  } else {
    setEmailError('');
  }
};

<Input
  type="email"
  label="Email Address"
  placeholder="user@example.com"
  value={email}
  onChange={(e) => {
    setEmail(e.target.value);
    validateEmail(e.target.value);
  }}
  error={emailError}
/>
```

### Password Input

```tsx
<Input
  type="password"
  label="Password"
  placeholder="Enter your password"
/>
```

### Number Input

```tsx
<Input
  type="number"
  label="Age"
  placeholder="Enter your age"
  min={0}
  max={120}
/>
```

### Disabled Input

```tsx
<Input
  type="text"
  label="Disabled Field"
  disabled
  value="Read-only value"
/>
```

### Required Input

```tsx
<Input
  type="text"
  label="Required Field"
  placeholder="This field is required"
  required
/>
```

## Styling

### Normal State
- Border: `border-gray-300`
- Focus: `focus:ring-2 focus:ring-green-500 focus:border-transparent`
- Padding: `px-4 py-2`
- Border radius: `rounded-lg`

### Error State
- Border: `border-red-500`
- Error message: `text-red-600 text-sm mt-1`

### Label
- Font: `text-sm font-medium text-gray-700`
- Spacing: `mb-2`

## Accessibility

The Input component follows accessibility best practices:

- Proper semantic HTML with `<input>` and `<label>` elements
- Label is associated with input for screen readers
- Error messages are displayed in a clear, readable format
- Supports all standard ARIA attributes
- Keyboard navigation works as expected
- Focus states are clearly visible

## Validation Requirements

The component satisfies the following requirements from the design document:

- **Requirement 5.16**: Input component created at src/components/ui/Input.tsx ✅
- **Requirement 5.17**: Supports text, number, email, and password types ✅
- **Requirement 5.18**: Displays error state with red border and error message ✅
- **Requirement 5.19**: Supports label and placeholder props ✅

## Design Properties

The component implements the following correctness properties:

- **Property 10**: Input Type Attribute - The rendered input element has the type attribute set to the specified value ✅
- **Property 11**: Input Props Rendering - Both label and placeholder are present in the rendered output when provided ✅

## Examples

See `Input.example.tsx` for comprehensive usage examples including:
- Basic inputs with different types
- Form validation
- Error handling
- Controlled components
- Custom styling

## Integration

The Input component is designed to work seamlessly with:
- Form libraries (React Hook Form, Formik, etc.)
- Validation libraries (Yup, Zod, etc.)
- State management solutions (useState, Zustand, etc.)
- The NutriLens AI application's design system

## Browser Support

The component works in all modern browsers that support:
- ES6+ JavaScript
- CSS Grid and Flexbox
- HTML5 input types
