'use client';

import React, { useState } from 'react';
import { Toast } from './Toast';
import { Button } from './Button';

/**
 * Example usage of the Toast component
 * 
 * This demonstrates:
 * - All four toast types (success, error, info, warning)
 * - Auto-dismiss after 3 seconds
 * - Manual close functionality
 * - Multiple toasts displayed simultaneously
 */
export function ToastExample() {
  const [toasts, setToasts] = useState<Array<{
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
  }>>([]);

  const showToast = (type: 'success' | 'error' | 'info' | 'warning', message: string) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, type, message }]);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <div className="p-8 space-y-4">
      <h2 className="text-2xl font-bold mb-4">Toast Component Examples</h2>
      
      <div className="flex flex-wrap gap-4">
        <Button
          variant="primary"
          onClick={() => showToast('success', 'Operation completed successfully!')}
        >
          Show Success Toast
        </Button>
        
        <Button
          variant="danger"
          onClick={() => showToast('error', 'An error occurred. Please try again.')}
        >
          Show Error Toast
        </Button>
        
        <Button
          variant="secondary"
          onClick={() => showToast('info', 'Here is some helpful information.')}
        >
          Show Info Toast
        </Button>
        
        <Button
          variant="ghost"
          onClick={() => showToast('warning', 'Warning: This action cannot be undone.')}
        >
          Show Warning Toast
        </Button>
      </div>

      {/* Toast Container - Fixed position in top-right corner */}
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
    </div>
  );
}
