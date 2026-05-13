import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Toast } from '@/components/ui/Toast';

// Mock timers for auto-dismiss testing
jest.useFakeTimers();

describe('Toast Component', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
    jest.clearAllTimers();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  describe('Basic Rendering', () => {
    it('should render toast message', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Operation successful"
          onClose={mockOnClose}
        />
      );

      expect(screen.getByText('Operation successful')).toBeInTheDocument();
    });

    it('should render close button', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Test message"
          onClose={mockOnClose}
        />
      );

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      expect(closeButton).toBeInTheDocument();
    });

    it('should have alert role for accessibility', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message="Test message"
          onClose={mockOnClose}
        />
      );

      const alert = container.querySelector('[role="alert"]');
      expect(alert).toBeInTheDocument();
    });
  });

  describe('Toast Types and Styling', () => {
    // Validates: Requirements 9.3 - Support types (success, error, info, warning)
    it('should render success type with green background', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message="Success message"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('bg-green-500', 'text-white');
    });

    it('should render error type with red background', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="error"
          message="Error message"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('bg-red-500', 'text-white');
    });

    it('should render info type with blue background', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="info"
          message="Info message"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('bg-blue-500', 'text-white');
    });

    it('should render warning type with orange background', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="warning"
          message="Warning message"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('bg-orange-500', 'text-white');
    });

    // Validates: Requirements 9.4 - Use color-coded backgrounds
    it('should use appropriate icons for each type', () => {
      const types: Array<'success' | 'error' | 'info' | 'warning'> = [
        'success',
        'error',
        'info',
        'warning',
      ];

      types.forEach((type) => {
        const { container } = render(
          <Toast
            id={`test-${type}`}
            type={type}
            message={`${type} message`}
            onClose={mockOnClose}
          />
        );

        // Each type should have an icon (svg element)
        const icon = container.querySelector('svg');
        expect(icon).toBeInTheDocument();
      });
    });
  });

  describe('Auto-dismiss Functionality', () => {
    // Validates: Requirements 9.5 - Automatically dismiss after 3 seconds
    it('should auto-dismiss after 3 seconds', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Auto-dismiss test"
          onClose={mockOnClose}
        />
      );

      expect(mockOnClose).not.toHaveBeenCalled();

      // Fast-forward time by 3 seconds
      jest.advanceTimersByTime(3000);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
      expect(mockOnClose).toHaveBeenCalledWith('test-1');
    });

    it('should not auto-dismiss before 3 seconds', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Auto-dismiss test"
          onClose={mockOnClose}
        />
      );

      // Fast-forward time by 2.9 seconds (just before 3 seconds)
      jest.advanceTimersByTime(2900);

      expect(mockOnClose).not.toHaveBeenCalled();
    });

    it('should clean up timer on unmount', () => {
      const { unmount } = render(
        <Toast
          id="test-1"
          type="success"
          message="Unmount test"
          onClose={mockOnClose}
        />
      );

      unmount();

      // Fast-forward time after unmount
      jest.advanceTimersByTime(3000);

      // onClose should not be called after unmount
      expect(mockOnClose).not.toHaveBeenCalled();
    });
  });

  describe('Manual Close Functionality', () => {
    // Validates: Requirements 9.6 - Include a close button for manual dismissal
    it('should call onClose when close button is clicked', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Manual close test"
          onClose={mockOnClose}
        />
      );

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
      expect(mockOnClose).toHaveBeenCalledWith('test-1');
    });

    it('should allow manual close before auto-dismiss', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Manual close test"
          onClose={mockOnClose}
        />
      );

      // Click close button after 1 second
      jest.advanceTimersByTime(1000);
      const closeButton = screen.getByRole('button', { name: /close notification/i });
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);

      // Advance to 3 seconds - should not call onClose again
      jest.advanceTimersByTime(2000);
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Animation and Styling', () => {
    // Validates: Requirements 9.7 - Animate in from the right
    it('should have slide-in animation class', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message="Animation test"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('animate-slide-in-right');
    });

    it('should have proper layout styling', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message="Layout test"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('rounded-lg', 'shadow-lg', 'p-4', 'flex', 'items-center', 'gap-3');
    });

    it('should have minimum width constraint', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message="Short"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('min-w-[300px]');
    });

    it('should have maximum width constraint', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message="Very long message that should be constrained by max width"
          onClose={mockOnClose}
        />
      );

      const toast = container.firstChild as HTMLElement;
      expect(toast).toHaveClass('max-w-md');
    });
  });

  describe('Accessibility', () => {
    it('should be keyboard accessible', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Keyboard test"
          onClose={mockOnClose}
        />
      );

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      closeButton.focus();

      expect(closeButton).toHaveFocus();
    });

    it('should have proper aria-label on close button', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Aria test"
          onClose={mockOnClose}
        />
      );

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      expect(closeButton).toHaveAttribute('aria-label', 'Close notification');
    });

    it('should have proper text sizing for readability', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Text size test"
          onClose={mockOnClose}
        />
      );

      const message = screen.getByText('Text size test');
      expect(message).toHaveClass('text-sm', 'font-medium');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty message string', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message=""
          onClose={mockOnClose}
        />
      );

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should handle very long messages', () => {
      const longMessage = 'A'.repeat(500);
      render(
        <Toast
          id="test-1"
          type="success"
          message={longMessage}
          onClose={mockOnClose}
        />
      );

      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should handle special characters in message', () => {
      const specialMessage = 'Success: <script>alert("xss")</script>';
      render(
        <Toast
          id="test-1"
          type="success"
          message={specialMessage}
          onClose={mockOnClose}
        />
      );

      expect(screen.getByText(specialMessage)).toBeInTheDocument();
    });

    it('should handle multiple rapid close button clicks', () => {
      render(
        <Toast
          id="test-1"
          type="success"
          message="Rapid click test"
          onClose={mockOnClose}
        />
      );

      const closeButton = screen.getByRole('button', { name: /close notification/i });

      fireEvent.click(closeButton);
      fireEvent.click(closeButton);
      fireEvent.click(closeButton);

      // onClose should be called for each click
      expect(mockOnClose).toHaveBeenCalledTimes(3);
    });

    it('should handle different toast IDs correctly', () => {
      const { rerender } = render(
        <Toast
          id="toast-1"
          type="success"
          message="First toast"
          onClose={mockOnClose}
        />
      );

      const closeButton = screen.getByRole('button', { name: /close notification/i });
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledWith('toast-1');

      mockOnClose.mockClear();

      rerender(
        <Toast
          id="toast-2"
          type="error"
          message="Second toast"
          onClose={mockOnClose}
        />
      );

      const closeButton2 = screen.getByRole('button', { name: /close notification/i });
      fireEvent.click(closeButton2);

      expect(mockOnClose).toHaveBeenCalledWith('toast-2');
    });
  });

  describe('Requirements Validation', () => {
    // Validates: Requirements 9.1 - Create Toast component at correct path
    it('should exist and be importable', () => {
      expect(Toast).toBeDefined();
    });

    // Validates: Requirements 9.2 - Display message with icon in fixed position
    it('should display message with icon', () => {
      const { container } = render(
        <Toast
          id="test-1"
          type="success"
          message="Test message"
          onClose={mockOnClose}
        />
      );

      // Icon should be present
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();

      // Message should be present
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    // Validates: Requirements 9.3, 9.4 - Support all types with color-coded backgrounds
    it('should support all required types with appropriate colors', () => {
      const types: Array<{ type: 'success' | 'error' | 'info' | 'warning'; color: string }> = [
        { type: 'success', color: 'bg-green-500' },
        { type: 'error', color: 'bg-red-500' },
        { type: 'info', color: 'bg-blue-500' },
        { type: 'warning', color: 'bg-orange-500' },
      ];

      types.forEach(({ type, color }) => {
        const { container } = render(
          <Toast
            id={`test-${type}`}
            type={type}
            message={`${type} message`}
            onClose={mockOnClose}
          />
        );

        const toast = container.firstChild as HTMLElement;
        expect(toast).toHaveClass(color);
      });
    });
  });
});
