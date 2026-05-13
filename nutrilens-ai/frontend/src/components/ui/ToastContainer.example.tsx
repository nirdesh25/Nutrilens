'use client';

import React, { useState } from 'react';
import { ToastContainer } from './ToastContainer';
import { Button } from './Button';

interface ToastData {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

export function ToastContainerExample() {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  const addToast = (type: ToastData['type'], message: string) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="p-8 space-y-4">
      <h2 className="text-2xl font-bold mb-4">ToastContainer Example</h2>
      
      <div className="space-y-2">
        <p className="text-gray-600 mb-4">
          Click the buttons below to show different types of toast notifications.
          Multiple toasts will stack in the top-right corner.
        </p>
        
        <div className="flex flex-wrap gap-2">
          <Button
            variant="primary"
            onClick={() => addToast('success', 'Operation completed successfully!')}
          >
            Show Success Toast
          </Button>
          
          <Button
            variant="danger"
            onClick={() => addToast('error', 'An error occurred. Please try again.')}
          >
            Show Error Toast
          </Button>
          
          <Button
            variant="secondary"
            onClick={() => addToast('info', 'Here is some helpful information.')}
          >
            Show Info Toast
          </Button>
          
          <Button
            variant="secondary"
            onClick={() => addToast('warning', 'Warning: Please review your input.')}
          >
            Show Warning Toast
          </Button>
          
          <Button
            variant="ghost"
            onClick={() => {
              addToast('success', 'First toast');
              setTimeout(() => addToast('info', 'Second toast'), 200);
              setTimeout(() => addToast('warning', 'Third toast'), 400);
            }}
          >
            Show Multiple Toasts
          </Button>
        </div>
      </div>

      <div className="mt-8 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-semibold mb-2">Active Toasts: {toasts.length}</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          {toasts.map((toast) => (
            <li key={toast.id}>
              {toast.type}: {toast.message}
            </li>
          ))}
        </ul>
      </div>

      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  );
}
