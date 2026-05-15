import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '@/components/ui/Input';

describe('Input Component', () => {
  describe('Basic Rendering', () => {
    it('renders input element', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');
      expect(input).toBeInTheDocument();
    });

    it('renders with placeholder', () => {
      render(<Input placeholder="Enter text" />);
      const input = screen.getByPlaceholderText('Enter text');
      expect(input).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<Input className="custom-class" />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('custom-class');
    });
  });

  describe('Label Support', () => {
    it('renders with label when provided', () => {
      render(<Input label="Username" />);
      const label = screen.getByText('Username');
      expect(label).toBeInTheDocument();
      expect(label.tagName).toBe('LABEL');
    });

    it('does not render label when not provided', () => {
      const { container } = render(<Input />);
      const label = container.querySelector('label');
      expect(label).not.toBeInTheDocument();
    });

    it('applies correct label styling', () => {
      render(<Input label="Email" />);
      const label = screen.getByText('Email');
      expect(label).toHaveClass('block', 'text-sm', 'font-medium', 'text-gray-700', 'mb-2');
    });
  });

  describe('Input Types', () => {
    it('renders text input by default', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('type', 'text');
    });

    it('renders number input when type is number', () => {
      render(<Input type="number" />);
      const input = screen.getByRole('spinbutton');
      expect(input).toHaveAttribute('type', 'number');
    });

    it('renders email input when type is email', () => {
      render(<Input type="email" />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('type', 'email');
    });

    it('renders password input when type is password', () => {
      const { container } = render(<Input type="password" />);
      const input = container.querySelector('input[type="password"]');
      expect(input).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('displays error message when error prop is provided', () => {
      render(<Input error="This field is required" />);
      const errorMessage = screen.getByText('This field is required');
      expect(errorMessage).toBeInTheDocument();
    });

    it('applies red border when error is present', () => {
      render(<Input error="Error message" />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('border-red-500');
    });

    it('applies gray border when no error', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('border-gray-300');
    });

    it('applies correct error message styling', () => {
      render(<Input error="Error text" />);
      const errorMessage = screen.getByText('Error text');
      expect(errorMessage).toHaveClass('mt-1', 'text-sm', 'text-red-600');
    });

    it('does not display error message when error prop is not provided', () => {
      const { container } = render(<Input />);
      const errorMessage = container.querySelector('.text-red-600');
      expect(errorMessage).not.toBeInTheDocument();
    });
  });

  describe('Normal State Styling', () => {
    it('applies correct base styling', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass(
        'w-full',
        'px-4',
        'py-2',
        'border',
        'rounded-lg',
        'focus:ring-2',
        'focus:ring-green-500',
        'focus:border-transparent',
        'transition'
      );
    });

    it('applies green focus ring', () => {
      render(<Input />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveClass('focus:ring-green-500');
    });
  });

  describe('Props Forwarding', () => {
    it('forwards all HTML input attributes', () => {
      render(
        <Input
          name="username"
          id="user-input"
          disabled
          required
          maxLength={50}
          value="test"
          readOnly
        />
      );
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('name', 'username');
      expect(input).toHaveAttribute('id', 'user-input');
      expect(input).toBeDisabled();
      expect(input).toBeRequired();
      expect(input).toHaveAttribute('maxLength', '50');
      expect(input).toHaveValue('test');
    });

    it('forwards onChange handler', () => {
      const handleChange = jest.fn();
      render(<Input onChange={handleChange} />);
      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'new value' } });
      expect(handleChange).toHaveBeenCalled();
    });

    it('forwards onBlur handler', () => {
      const handleBlur = jest.fn();
      render(<Input onBlur={handleBlur} />);
      const input = screen.getByRole('textbox');
      fireEvent.blur(input);
      expect(handleBlur).toHaveBeenCalled();
    });

    it('forwards onFocus handler', () => {
      const handleFocus = jest.fn();
      render(<Input onFocus={handleFocus} />);
      const input = screen.getByRole('textbox');
      fireEvent.focus(input);
      expect(handleFocus).toHaveBeenCalled();
    });
  });

  describe('Combined Props', () => {
    it('renders with label, placeholder, and error together', () => {
      render(
        <Input
          label="Email Address"
          placeholder="Enter your email"
          error="Invalid email format"
        />
      );
      
      expect(screen.getByText('Email Address')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Enter your email')).toBeInTheDocument();
      expect(screen.getByText('Invalid email format')).toBeInTheDocument();
    });

    it('renders with all props including type', () => {
      render(
        <Input
          type="email"
          label="Email"
          placeholder="user@example.com"
          error="Required field"
          value="test@test.com"
          readOnly
        />
      );
      
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('type', 'email');
      expect(input).toHaveValue('test@test.com');
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Required field')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper input role', () => {
      render(<Input />);
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('supports aria-label', () => {
      render(<Input aria-label="Search field" />);
      const input = screen.getByLabelText('Search field');
      expect(input).toBeInTheDocument();
    });

    it('supports aria-describedby for error messages', () => {
      render(<Input aria-describedby="error-message" />);
      const input = screen.getByRole('textbox');
      expect(input).toHaveAttribute('aria-describedby', 'error-message');
    });
  });
});
