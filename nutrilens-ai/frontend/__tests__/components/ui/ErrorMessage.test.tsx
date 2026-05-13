import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

describe('ErrorMessage Component', () => {
  describe('Basic Rendering', () => {
    it('should render error message text', () => {
      const message = 'Something went wrong';
      render(<ErrorMessage message={message} />);
      
      expect(screen.getByText(message)).toBeInTheDocument();
    });

    it('should display error icon', () => {
      render(<ErrorMessage message="Error occurred" />);
      
      // AlertCircle icon should be rendered
      const icon = document.querySelector('.lucide-alert-circle');
      expect(icon).toBeInTheDocument();
    });

    it('should use red color scheme', () => {
      const { container } = render(<ErrorMessage message="Error" />);
      
      // Check for red text color on message
      const messageElement = screen.getByText('Error');
      expect(messageElement).toHaveClass('text-red-700');
      
      // Check for red icon color
      const icon = container.querySelector('.text-red-500');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Retry Button', () => {
    it('should render retry button when onRetry is provided', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();
    });

    it('should not render retry button when onRetry is not provided', () => {
      render(<ErrorMessage message="Error" />);
      
      const retryButton = screen.queryByRole('button', { name: /retry/i });
      expect(retryButton).not.toBeInTheDocument();
    });

    it('should call onRetry when retry button is clicked', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);
      
      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it('should render retry button with danger variant', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorMessage message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      // Button should have danger variant styling (red background)
      expect(retryButton).toHaveClass('bg-red-600');
    });
  });

  describe('Layout and Styling', () => {
    it('should center content', () => {
      const { container } = render(<ErrorMessage message="Error" />);
      
      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('flex', 'flex-col', 'items-center', 'justify-center');
    });

    it('should apply proper spacing', () => {
      const { container } = render(<ErrorMessage message="Error" />);
      
      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('p-6');
    });

    it('should center text', () => {
      const { container } = render(<ErrorMessage message="Error" />);
      
      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('text-center');
    });
  });

  describe('Accessibility', () => {
    it('should have proper text hierarchy', () => {
      render(<ErrorMessage message="Error occurred" />);
      
      const message = screen.getByText('Error occurred');
      expect(message).toHaveClass('text-lg', 'font-medium');
    });

    it('should be keyboard accessible when retry button is present', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      retryButton.focus();
      
      expect(retryButton).toHaveFocus();
    });
  });

  describe('Requirements Validation', () => {
    // Validates: Requirements 8.1 - Create ErrorMessage component
    it('should exist at correct path', () => {
      // This test validates the component can be imported
      expect(ErrorMessage).toBeDefined();
    });

    // Validates: Requirements 8.2 - Display error icon and error text
    it('should display both error icon and error text', () => {
      const message = 'Test error message';
      const { container } = render(<ErrorMessage message={message} />);
      
      // Icon should be present
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
      
      // Text should be present
      expect(screen.getByText(message)).toBeInTheDocument();
    });

    // Validates: Requirements 8.3 - Support optional retry button with onRetry callback
    it('should support optional retry button with callback', () => {
      const onRetry = jest.fn();
      
      // Without onRetry - no button
      const { rerender } = render(<ErrorMessage message="Error" />);
      expect(screen.queryByRole('button')).not.toBeInTheDocument();
      
      // With onRetry - button appears and works
      rerender(<ErrorMessage message="Error" onRetry={onRetry} />);
      const button = screen.getByRole('button', { name: /retry/i });
      expect(button).toBeInTheDocument();
      
      fireEvent.click(button);
      expect(onRetry).toHaveBeenCalled();
    });

    // Validates: Requirements 8.4 - Use red color scheme
    it('should use red color scheme for error indication', () => {
      const { container } = render(<ErrorMessage message="Error" />);
      
      // Icon should be red
      const icon = container.querySelector('.text-red-500');
      expect(icon).toBeInTheDocument();
      
      // Text should be red
      const text = screen.getByText('Error');
      expect(text).toHaveClass('text-red-700');
      
      // Button (if present) should use danger variant (red)
      const onRetry = jest.fn();
      const { container: containerWithButton } = render(
        <ErrorMessage message="Error" onRetry={onRetry} />
      );
      const button = screen.getByRole('button', { name: /retry/i });
      expect(button).toHaveClass('bg-red-600');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty message string', () => {
      render(<ErrorMessage message="" />);
      
      // Component should still render without crashing
      const { container } = render(<ErrorMessage message="" />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('should handle very long error messages', () => {
      const longMessage = 'A'.repeat(500);
      render(<ErrorMessage message={longMessage} />);
      
      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should handle special characters in message', () => {
      const specialMessage = 'Error: <script>alert("xss")</script>';
      render(<ErrorMessage message={specialMessage} />);
      
      // React should escape the content automatically
      expect(screen.getByText(specialMessage)).toBeInTheDocument();
    });

    it('should handle multiple rapid retry clicks', () => {
      const onRetry = jest.fn();
      render(<ErrorMessage message="Error" onRetry={onRetry} />);
      
      const button = screen.getByRole('button', { name: /retry/i });
      
      // Click multiple times rapidly
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);
      
      expect(onRetry).toHaveBeenCalledTimes(3);
    });
  });
});
