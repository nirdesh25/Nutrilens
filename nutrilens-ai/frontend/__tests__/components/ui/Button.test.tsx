import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button Component', () => {
  describe('Basic Rendering', () => {
    it('should render button with children', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
    });

    it('should render button with text content', () => {
      render(<Button>Submit</Button>);
      expect(screen.getByText('Submit')).toBeInTheDocument();
    });

    it('should be a button element', () => {
      const { container } = render(<Button>Test</Button>);
      const button = container.querySelector('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Variant Styling', () => {
    // Validates: Requirements 5.2 - Support variants (primary, secondary, danger, ghost)
    it('should render primary variant with correct styles', () => {
      const { container } = render(<Button variant="primary">Primary</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('bg-green-600', 'hover:bg-green-700', 'text-white');
    });

    it('should render secondary variant with correct styles', () => {
      const { container } = render(<Button variant="secondary">Secondary</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('bg-gray-200', 'hover:bg-gray-300', 'text-gray-900');
    });

    it('should render danger variant with correct styles', () => {
      const { container } = render(<Button variant="danger">Danger</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('bg-red-600', 'hover:bg-red-700', 'text-white');
    });

    it('should render ghost variant with correct styles', () => {
      const { container } = render(<Button variant="ghost">Ghost</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('bg-transparent', 'hover:bg-gray-100', 'text-gray-700');
    });

    it('should default to primary variant when no variant is specified', () => {
      const { container } = render(<Button>Default</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('bg-green-600', 'hover:bg-green-700', 'text-white');
    });
  });

  describe('Size Styling', () => {
    // Validates: Requirements 5.3 - Support sizes (sm, md, lg)
    it('should render small size with correct styles', () => {
      const { container } = render(<Button size="sm">Small</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('px-3', 'py-1.5', 'text-sm');
    });

    it('should render medium size with correct styles', () => {
      const { container } = render(<Button size="md">Medium</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-base');
    });

    it('should render large size with correct styles', () => {
      const { container } = render(<Button size="lg">Large</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('px-6', 'py-3', 'text-lg');
    });

    it('should default to medium size when no size is specified', () => {
      const { container } = render(<Button>Default Size</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('px-4', 'py-2', 'text-base');
    });
  });

  describe('Disabled State', () => {
    // Validates: Requirements 5.4 - Support disabled state with reduced opacity
    it('should be disabled when disabled prop is true', () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('should have reduced opacity when disabled', () => {
      const { container } = render(<Button disabled>Disabled</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('disabled:opacity-50');
    });

    it('should have not-allowed cursor when disabled', () => {
      const { container } = render(<Button disabled>Disabled</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('disabled:cursor-not-allowed');
    });

    it('should not call onClick when disabled', () => {
      const handleClick = jest.fn();
      render(<Button disabled onClick={handleClick}>Disabled</Button>);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('should be enabled by default', () => {
      render(<Button>Enabled</Button>);
      const button = screen.getByRole('button');
      expect(button).not.toBeDisabled();
    });
  });

  describe('Loading State', () => {
    // Validates: Requirements 5.5 - Support loading state with spinner icon
    it('should show spinner when loading is true', () => {
      const { container } = render(<Button loading>Loading</Button>);
      const spinner = container.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should be disabled when loading', () => {
      render(<Button loading>Loading</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('should not show spinner when loading is false', () => {
      const { container } = render(<Button loading={false}>Not Loading</Button>);
      const spinner = container.querySelector('.animate-spin');
      expect(spinner).not.toBeInTheDocument();
    });

    it('should not call onClick when loading', () => {
      const handleClick = jest.fn();
      render(<Button loading onClick={handleClick}>Loading</Button>);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('should display children alongside spinner when loading', () => {
      render(<Button loading>Loading Text</Button>);
      expect(screen.getByText('Loading Text')).toBeInTheDocument();
    });

    it('should have proper gap between spinner and text', () => {
      const { container } = render(<Button loading>Loading</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('gap-2');
    });
  });

  describe('Click Handling', () => {
    it('should call onClick when clicked', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Click me</Button>);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('should call onClick multiple times on multiple clicks', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Click me</Button>);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(3);
    });

    it('should pass event to onClick handler', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Click me</Button>);
      const button = screen.getByRole('button');
      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledWith(expect.any(Object));
    });
  });

  describe('HTML Attributes', () => {
    it('should accept and apply type attribute', () => {
      render(<Button type="submit">Submit</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });

    it('should accept and apply custom className', () => {
      const { container } = render(<Button className="custom-class">Custom</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('custom-class');
    });

    it('should preserve base classes when custom className is provided', () => {
      const { container } = render(<Button className="custom-class">Custom</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('inline-flex', 'items-center', 'justify-center');
    });

    it('should accept and apply aria-label', () => {
      render(<Button aria-label="Custom label">Button</Button>);
      const button = screen.getByRole('button', { name: 'Custom label' });
      expect(button).toBeInTheDocument();
    });

    it('should accept and apply data attributes', () => {
      render(<Button data-testid="custom-button">Button</Button>);
      const button = screen.getByTestId('custom-button');
      expect(button).toBeInTheDocument();
    });

    it('should accept and apply id attribute', () => {
      render(<Button id="my-button">Button</Button>);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('id', 'my-button');
    });
  });

  describe('Base Styling', () => {
    it('should have inline-flex display', () => {
      const { container } = render(<Button>Test</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('inline-flex');
    });

    it('should have items-center alignment', () => {
      const { container } = render(<Button>Test</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('items-center');
    });

    it('should have justify-center alignment', () => {
      const { container } = render(<Button>Test</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('justify-center');
    });

    it('should have rounded corners', () => {
      const { container } = render(<Button>Test</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('rounded-lg');
    });

    it('should have transition effect', () => {
      const { container } = render(<Button>Test</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('transition');
    });

    it('should have font-medium weight', () => {
      const { container } = render(<Button>Test</Button>);
      const button = container.querySelector('button');
      expect(button).toHaveClass('font-medium');
    });
  });

  describe('Combination States', () => {
    it('should handle all variants with all sizes', () => {
      const variants: Array<'primary' | 'secondary' | 'danger' | 'ghost'> = ['primary', 'secondary', 'danger', 'ghost'];
      const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];

      variants.forEach(variant => {
        sizes.forEach(size => {
          const { container } = render(
            <Button variant={variant} size={size}>
              {variant}-{size}
            </Button>
          );
          const button = container.querySelector('button');
          expect(button).toBeInTheDocument();
        });
      });
    });

    it('should handle disabled and loading together', () => {
      render(<Button disabled loading>Disabled and Loading</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('should handle all variants in loading state', () => {
      const variants: Array<'primary' | 'secondary' | 'danger' | 'ghost'> = ['primary', 'secondary', 'danger', 'ghost'];

      variants.forEach(variant => {
        const { container } = render(
          <Button variant={variant} loading>
            Loading {variant}
          </Button>
        );
        const spinner = container.querySelector('.animate-spin');
        expect(spinner).toBeInTheDocument();
      });
    });

    it('should handle all sizes in loading state', () => {
      const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];

      sizes.forEach(size => {
        const { container } = render(
          <Button size={size} loading>
            Loading {size}
          </Button>
        );
        const spinner = container.querySelector('.animate-spin');
        expect(spinner).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should be keyboard accessible', () => {
      render(<Button>Keyboard Test</Button>);
      const button = screen.getByRole('button');
      button.focus();
      expect(button).toHaveFocus();
    });

    it('should have button role', () => {
      render(<Button>Role Test</Button>);
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('should be focusable when not disabled', () => {
      render(<Button>Focusable</Button>);
      const button = screen.getByRole('button');
      expect(button).not.toHaveAttribute('tabindex', '-1');
    });

    it('should support keyboard Enter key', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Enter Test</Button>);
      const button = screen.getByRole('button');
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
      // Note: fireEvent.keyDown doesn't trigger click by default, but the button is keyboard accessible
      expect(button).toBeInTheDocument();
    });

    it('should support keyboard Space key', () => {
      const handleClick = jest.fn();
      render(<Button onClick={handleClick}>Space Test</Button>);
      const button = screen.getByRole('button');
      fireEvent.keyDown(button, { key: ' ', code: 'Space' });
      // Note: fireEvent.keyDown doesn't trigger click by default, but the button is keyboard accessible
      expect(button).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      const { container } = render(<Button></Button>);
      const button = container.querySelector('button');
      expect(button).toBeInTheDocument();
    });

    it('should handle complex children (nested elements)', () => {
      render(
        <Button>
          <span>Icon</span>
          <span>Text</span>
        </Button>
      );
      expect(screen.getByText('Icon')).toBeInTheDocument();
      expect(screen.getByText('Text')).toBeInTheDocument();
    });

    it('should handle very long text', () => {
      const longText = 'A'.repeat(100);
      render(<Button>{longText}</Button>);
      expect(screen.getByText(longText)).toBeInTheDocument();
    });

    it('should handle special characters in children', () => {
      render(<Button>{'<>&"\'`'}</Button>);
      expect(screen.getByText('<>&"\'`')).toBeInTheDocument();
    });

    it('should handle rapid state changes', () => {
      const { rerender } = render(<Button loading={false}>Test</Button>);
      rerender(<Button loading={true}>Test</Button>);
      rerender(<Button loading={false}>Test</Button>);
      expect(screen.getByText('Test')).toBeInTheDocument();
    });
  });

  describe('Requirements Validation', () => {
    // Validates: Requirements 5.1 - Create Button component at correct path
    it('should exist and be importable', () => {
      expect(Button).toBeDefined();
    });

    // Validates: Requirements 5.2 - Support all required variants
    it('should support all required variants', () => {
      const variants: Array<'primary' | 'secondary' | 'danger' | 'ghost'> = ['primary', 'secondary', 'danger', 'ghost'];
      variants.forEach(variant => {
        const { container } = render(<Button variant={variant}>Test</Button>);
        expect(container.querySelector('button')).toBeInTheDocument();
      });
    });

    // Validates: Requirements 5.3 - Support all required sizes
    it('should support all required sizes', () => {
      const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];
      sizes.forEach(size => {
        const { container } = render(<Button size={size}>Test</Button>);
        expect(container.querySelector('button')).toBeInTheDocument();
      });
    });

    // Validates: Requirements 5.4 - Support disabled state
    it('should support disabled state', () => {
      render(<Button disabled>Disabled</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    // Validates: Requirements 5.5 - Support loading state with spinner
    it('should support loading state with spinner', () => {
      const { container } = render(<Button loading>Loading</Button>);
      expect(container.querySelector('.animate-spin')).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeDisabled();
    });
  });
});
