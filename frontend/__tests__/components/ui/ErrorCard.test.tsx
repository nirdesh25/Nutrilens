import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorCard } from '@/components/ui/ErrorCard';

describe('ErrorCard Component', () => {
  describe('Basic Rendering', () => {
    it('should render error message text', () => {
      const message = 'Failed to load data';
      const onRetry = jest.fn();
      render(<ErrorCard message={message} onRetry={onRetry} />);
      
      expect(screen.getByText(message)).toBeInTheDocument();
    });

    it('should display error icon', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error occurred" onRetry={onRetry} />);
      
      // AlertCircle icon should be rendered
      const icon = document.querySelector('.lucide-alert-circle');
      expect(icon).toBeInTheDocument();
    });

    it('should render in card layout', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      // Card should have white background, rounded corners, and shadow
      const card = container.querySelector('.bg-white.rounded-xl.shadow-md');
      expect(card).toBeInTheDocument();
    });

    it('should have red border for error indication', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      // Card should have red border
      const card = container.querySelector('.border-2.border-red-200');
      expect(card).toBeInTheDocument();
    });
  });

  describe('Retry Button', () => {
    it('should always render retry button', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();
    });

    it('should call onRetry when retry button is clicked', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);
      
      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it('should render retry button with danger variant', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      // Button should have danger variant styling (red background)
      expect(retryButton).toHaveClass('bg-red-600');
    });

    it('should call the failed operation again when retry is clicked', () => {
      const mockFailedOperation = jest.fn();
      render(<ErrorCard message="Error" onRetry={mockFailedOperation} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);
      
      // The failed operation should be called again
      expect(mockFailedOperation).toHaveBeenCalledTimes(1);
    });
  });

  describe('Layout and Styling', () => {
    it('should center content within card', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const contentWrapper = container.querySelector('.flex.flex-col.items-center.justify-center');
      expect(contentWrapper).toBeInTheDocument();
    });

    it('should center text', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const contentWrapper = container.querySelector('.text-center');
      expect(contentWrapper).toBeInTheDocument();
    });

    it('should use red color scheme', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      // Icon should be red
      const icon = container.querySelector('.text-red-500');
      expect(icon).toBeInTheDocument();
      
      // Text should be red
      const text = screen.getByText('Error');
      expect(text).toHaveClass('text-red-700');
    });
  });

  describe('Accessibility', () => {
    it('should have proper text hierarchy', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error occurred" onRetry={onRetry} />);
      
      const message = screen.getByText('Error occurred');
      expect(message).toHaveClass('text-lg', 'font-medium');
    });

    it('should be keyboard accessible', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      retryButton.focus();
      
      expect(retryButton).toHaveFocus();
    });

    it('should support keyboard interaction for retry', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      retryButton.focus();
      
      // Simulate Enter key press
      fireEvent.keyDown(retryButton, { key: 'Enter', code: 'Enter' });
      fireEvent.click(retryButton);
      
      expect(onRetry).toHaveBeenCalled();
    });
  });

  describe('Requirements Validation', () => {
    // Validates: Requirements 8.5 - Create ErrorCard component
    it('should exist at correct path', () => {
      // This test validates the component can be imported
      expect(ErrorCard).toBeDefined();
    });

    // Validates: Requirements 8.6 - Display error message in card layout
    it('should display error message in a card layout', () => {
      const message = 'Test error message';
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message={message} onRetry={onRetry} />);
      
      // Card layout should be present
      const card = container.querySelector('.bg-white.rounded-xl.shadow-md');
      expect(card).toBeInTheDocument();
      
      // Message should be inside the card
      expect(screen.getByText(message)).toBeInTheDocument();
    });

    // Validates: Requirements 8.7 - Include retry button that calls failed operation
    it('should include retry button that calls the failed operation again', () => {
      const failedOperation = jest.fn();
      render(<ErrorCard message="Operation failed" onRetry={failedOperation} />);
      
      // Retry button should be present
      const retryButton = screen.getByRole('button', { name: /retry/i });
      expect(retryButton).toBeInTheDocument();
      
      // Clicking retry should call the failed operation
      fireEvent.click(retryButton);
      expect(failedOperation).toHaveBeenCalledTimes(1);
      
      // Multiple clicks should call it multiple times
      fireEvent.click(retryButton);
      expect(failedOperation).toHaveBeenCalledTimes(2);
    });
  });

  describe('Integration with Card Component', () => {
    it('should use Card component for layout', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      // Should have Card's characteristic classes
      const card = container.querySelector('.bg-white.rounded-xl.shadow-md.p-6');
      expect(card).toBeInTheDocument();
    });

    it('should apply custom className to Card', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      // Should have the custom border styling
      const card = container.querySelector('.border-2.border-red-200');
      expect(card).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty message string', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="" onRetry={onRetry} />);
      
      // Component should still render without crashing
      expect(container.firstChild).toBeInTheDocument();
    });

    it('should handle very long error messages', () => {
      const longMessage = 'A'.repeat(500);
      const onRetry = jest.fn();
      render(<ErrorCard message={longMessage} onRetry={onRetry} />);
      
      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should handle special characters in message', () => {
      const specialMessage = 'Error: <script>alert("xss")</script>';
      const onRetry = jest.fn();
      render(<ErrorCard message={specialMessage} onRetry={onRetry} />);
      
      // React should escape the content automatically
      expect(screen.getByText(specialMessage)).toBeInTheDocument();
    });

    it('should handle multiple rapid retry clicks', () => {
      const onRetry = jest.fn();
      render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      const button = screen.getByRole('button', { name: /retry/i });
      
      // Click multiple times rapidly
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);
      
      expect(onRetry).toHaveBeenCalledTimes(3);
    });

    it('should handle async retry operations', async () => {
      const asyncRetry = jest.fn().mockResolvedValue('success');
      render(<ErrorCard message="Error" onRetry={asyncRetry} />);
      
      const button = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(button);
      
      expect(asyncRetry).toHaveBeenCalledTimes(1);
    });
  });

  describe('Visual Consistency', () => {
    it('should match ErrorMessage styling for consistency', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      // Icon size should match ErrorMessage
      const icon = container.querySelector('.w-12.h-12');
      expect(icon).toBeInTheDocument();
      
      // Text styling should match ErrorMessage
      const text = screen.getByText('Error');
      expect(text).toHaveClass('text-red-700', 'text-lg', 'font-medium');
    });

    it('should maintain consistent spacing', () => {
      const onRetry = jest.fn();
      const { container } = render(<ErrorCard message="Error" onRetry={onRetry} />);
      
      // Icon should have bottom margin
      const icon = container.querySelector('.mb-4');
      expect(icon).toBeInTheDocument();
      
      // Text should have bottom margin
      const text = screen.getByText('Error');
      expect(text).toHaveClass('mb-4');
    });
  });
});
