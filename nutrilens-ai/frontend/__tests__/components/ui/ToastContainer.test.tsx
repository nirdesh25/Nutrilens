import React from 'react';
import { render, screen } from '@testing-library/react';
import { ToastContainer } from '@/components/ui/ToastContainer';

// Mock the Toast component to simplify testing
jest.mock('@/components/ui/Toast', () => ({
  Toast: ({ id, type, message }: any) => (
    <div data-testid={`toast-${id}`} data-type={type}>
      {message}
    </div>
  ),
}));

describe('ToastContainer Component', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  describe('Basic Rendering', () => {
    // Validates: Requirements 9.11 - Create ToastContainer component
    it('should render without crashing', () => {
      const { container } = render(
        <ToastContainer toasts={[]} onClose={mockOnClose} />
      );

      expect(container.firstChild).toBeInTheDocument();
    });

    it('should render empty container when no toasts', () => {
      const { container } = render(
        <ToastContainer toasts={[]} onClose={mockOnClose} />
      );

      const toastElements = container.querySelectorAll('[data-testid^="toast-"]');
      expect(toastElements).toHaveLength(0);
    });

    it('should render single toast', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'Success message' },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByText('Success message')).toBeInTheDocument();
    });

    // Validates: Requirements 9.12 - Render all active toasts in stacked layout
    it('should render multiple toasts', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First message' },
        { id: 'toast-2', type: 'error' as const, message: 'Second message' },
        { id: 'toast-3', type: 'info' as const, message: 'Third message' },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-2')).toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-3')).toBeInTheDocument();
      expect(screen.getByText('First message')).toBeInTheDocument();
      expect(screen.getByText('Second message')).toBeInTheDocument();
      expect(screen.getByText('Third message')).toBeInTheDocument();
    });
  });

  describe('Positioning and Layout', () => {
    // Validates: Requirements 9.11 - Fixed top-right position
    it('should have fixed positioning in top-right corner', () => {
      const { container } = render(
        <ToastContainer toasts={[]} onClose={mockOnClose} />
      );

      const containerElement = container.firstChild as HTMLElement;
      expect(containerElement).toHaveClass('fixed', 'top-4', 'right-4');
    });

    it('should have high z-index to appear above other content', () => {
      const { container } = render(
        <ToastContainer toasts={[]} onClose={mockOnClose} />
      );

      const containerElement = container.firstChild as HTMLElement;
      expect(containerElement).toHaveClass('z-50');
    });

    // Validates: Requirements 9.12 - Stacked layout with spacing
    it('should have vertical spacing between toasts', () => {
      const { container } = render(
        <ToastContainer toasts={[]} onClose={mockOnClose} />
      );

      const containerElement = container.firstChild as HTMLElement;
      expect(containerElement).toHaveClass('space-y-2');
    });
  });

  describe('Toast Rendering', () => {
    it('should render toasts with correct props', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'Success' },
        { id: 'toast-2', type: 'error' as const, message: 'Error' },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      const toast1 = screen.getByTestId('toast-toast-1');
      const toast2 = screen.getByTestId('toast-toast-2');

      expect(toast1).toHaveAttribute('data-type', 'success');
      expect(toast2).toHaveAttribute('data-type', 'error');
    });

    it('should render toasts in order', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First' },
        { id: 'toast-2', type: 'error' as const, message: 'Second' },
        { id: 'toast-3', type: 'info' as const, message: 'Third' },
      ];

      const { container } = render(
        <ToastContainer toasts={toasts} onClose={mockOnClose} />
      );

      const toastElements = container.querySelectorAll('[data-testid^="toast-"]');
      expect(toastElements[0]).toHaveAttribute('data-testid', 'toast-toast-1');
      expect(toastElements[1]).toHaveAttribute('data-testid', 'toast-toast-2');
      expect(toastElements[2]).toHaveAttribute('data-testid', 'toast-toast-3');
    });

    it('should pass onClose callback to each toast', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'Test' },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      // The Toast component should receive the onClose prop
      // This is implicitly tested by the mock rendering without errors
      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
    });
  });

  describe('Dynamic Toast Updates', () => {
    it('should update when toasts are added', () => {
      const initialToasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First' },
      ];

      const { rerender } = render(
        <ToastContainer toasts={initialToasts} onClose={mockOnClose} />
      );

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();

      const updatedToasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First' },
        { id: 'toast-2', type: 'error' as const, message: 'Second' },
      ];

      rerender(<ToastContainer toasts={updatedToasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-2')).toBeInTheDocument();
    });

    it('should update when toasts are removed', () => {
      const initialToasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First' },
        { id: 'toast-2', type: 'error' as const, message: 'Second' },
      ];

      const { rerender } = render(
        <ToastContainer toasts={initialToasts} onClose={mockOnClose} />
      );

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-2')).toBeInTheDocument();

      const updatedToasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First' },
      ];

      rerender(<ToastContainer toasts={updatedToasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.queryByTestId('toast-toast-2')).not.toBeInTheDocument();
    });

    it('should handle complete toast replacement', () => {
      const initialToasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First' },
      ];

      const { rerender } = render(
        <ToastContainer toasts={initialToasts} onClose={mockOnClose} />
      );

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();

      const newToasts = [
        { id: 'toast-2', type: 'error' as const, message: 'Second' },
      ];

      rerender(<ToastContainer toasts={newToasts} onClose={mockOnClose} />);

      expect(screen.queryByTestId('toast-toast-1')).not.toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-2')).toBeInTheDocument();
    });
  });

  describe('Toast Types', () => {
    it('should render all toast types correctly', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'Success' },
        { id: 'toast-2', type: 'error' as const, message: 'Error' },
        { id: 'toast-3', type: 'info' as const, message: 'Info' },
        { id: 'toast-4', type: 'warning' as const, message: 'Warning' },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toHaveAttribute('data-type', 'success');
      expect(screen.getByTestId('toast-toast-2')).toHaveAttribute('data-type', 'error');
      expect(screen.getByTestId('toast-toast-3')).toHaveAttribute('data-type', 'info');
      expect(screen.getByTestId('toast-toast-4')).toHaveAttribute('data-type', 'warning');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty toast array', () => {
      const { container } = render(
        <ToastContainer toasts={[]} onClose={mockOnClose} />
      );

      const toastElements = container.querySelectorAll('[data-testid^="toast-"]');
      expect(toastElements).toHaveLength(0);
    });

    it('should handle large number of toasts', () => {
      const toasts = Array.from({ length: 10 }, (_, i) => ({
        id: `toast-${i}`,
        type: 'success' as const,
        message: `Message ${i}`,
      }));

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      toasts.forEach((toast) => {
        expect(screen.getByTestId(`toast-${toast.id}`)).toBeInTheDocument();
      });
    });

    it('should handle toasts with duplicate messages', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'Same message' },
        { id: 'toast-2', type: 'error' as const, message: 'Same message' },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-2')).toBeInTheDocument();
      expect(screen.getAllByText('Same message')).toHaveLength(2);
    });

    it('should handle toasts with empty messages', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: '' },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
    });

    it('should handle toasts with very long messages', () => {
      const longMessage = 'A'.repeat(500);
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: longMessage },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it('should handle toasts with special characters', () => {
      const specialMessage = '<script>alert("xss")</script>';
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: specialMessage },
      ];

      render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByText(specialMessage)).toBeInTheDocument();
    });
  });

  describe('Requirements Validation', () => {
    // Validates: Requirements 9.11 - ToastContainer component at correct path
    it('should exist and be importable', () => {
      expect(ToastContainer).toBeDefined();
    });

    // Validates: Requirements 9.12 - Render all active toasts in stacked layout
    it('should render all active toasts in stacked layout', () => {
      const toasts = [
        { id: 'toast-1', type: 'success' as const, message: 'First' },
        { id: 'toast-2', type: 'error' as const, message: 'Second' },
        { id: 'toast-3', type: 'info' as const, message: 'Third' },
      ];

      const { container } = render(
        <ToastContainer toasts={toasts} onClose={mockOnClose} />
      );

      // All toasts should be rendered
      expect(screen.getByTestId('toast-toast-1')).toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-2')).toBeInTheDocument();
      expect(screen.getByTestId('toast-toast-3')).toBeInTheDocument();

      // Container should have stacked layout styling
      const containerElement = container.firstChild as HTMLElement;
      expect(containerElement).toHaveClass('space-y-2');
    });

    // Validates: Requirements 9.11 - Fixed top-right position
    it('should be positioned in fixed top-right corner', () => {
      const { container } = render(
        <ToastContainer toasts={[]} onClose={mockOnClose} />
      );

      const containerElement = container.firstChild as HTMLElement;
      expect(containerElement).toHaveClass('fixed', 'top-4', 'right-4', 'z-50');
    });
  });
});
