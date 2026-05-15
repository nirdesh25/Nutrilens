import { renderHook, act } from '@testing-library/react';
import { ToastProvider, useToast } from '@/hooks/useToast';
import { ReactNode } from 'react';

describe('useToast', () => {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <ToastProvider>{children}</ToastProvider>
  );

  test('throws error when used outside ToastProvider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      renderHook(() => useToast());
    }).toThrow('useToast must be used within ToastProvider');
    
    consoleSpy.mockRestore();
  });

  test('initializes with empty toasts array', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    
    expect(result.current.toasts).toEqual([]);
  });

  test('showToast adds a toast with unique ID', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    
    act(() => {
      result.current.showToast({
        type: 'success',
        message: 'Test message',
      });
    });
    
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0]).toMatchObject({
      type: 'success',
      message: 'Test message',
    });
    expect(result.current.toasts[0].id).toBeDefined();
    expect(typeof result.current.toasts[0].id).toBe('string');
  });

  test('showToast generates unique IDs for multiple toasts', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    
    act(() => {
      result.current.showToast({ type: 'success', message: 'First' });
      result.current.showToast({ type: 'error', message: 'Second' });
      result.current.showToast({ type: 'info', message: 'Third' });
    });
    
    expect(result.current.toasts).toHaveLength(3);
    
    const ids = result.current.toasts.map((t) => t.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(3); // All IDs should be unique
  });

  test('removeToast removes the correct toast by ID', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    
    act(() => {
      result.current.showToast({ type: 'success', message: 'First' });
      result.current.showToast({ type: 'error', message: 'Second' });
      result.current.showToast({ type: 'info', message: 'Third' });
    });
    
    const secondToastId = result.current.toasts[1].id;
    
    act(() => {
      result.current.removeToast(secondToastId);
    });
    
    expect(result.current.toasts).toHaveLength(2);
    expect(result.current.toasts.find((t) => t.id === secondToastId)).toBeUndefined();
    expect(result.current.toasts[0].message).toBe('First');
    expect(result.current.toasts[1].message).toBe('Third');
  });

  test('removeToast handles non-existent ID gracefully', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    
    act(() => {
      result.current.showToast({ type: 'success', message: 'Test' });
    });
    
    const initialLength = result.current.toasts.length;
    
    act(() => {
      result.current.removeToast('non-existent-id');
    });
    
    expect(result.current.toasts).toHaveLength(initialLength);
  });

  test('supports all toast types', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    
    const types: Array<'success' | 'error' | 'info' | 'warning'> = [
      'success',
      'error',
      'info',
      'warning',
    ];
    
    act(() => {
      types.forEach((type) => {
        result.current.showToast({ type, message: `${type} message` });
      });
    });
    
    expect(result.current.toasts).toHaveLength(4);
    types.forEach((type, index) => {
      expect(result.current.toasts[index].type).toBe(type);
      expect(result.current.toasts[index].message).toBe(`${type} message`);
    });
  });

  test('maintains toast queue order (FIFO)', () => {
    const { result } = renderHook(() => useToast(), { wrapper });
    
    act(() => {
      result.current.showToast({ type: 'success', message: 'First' });
      result.current.showToast({ type: 'error', message: 'Second' });
      result.current.showToast({ type: 'info', message: 'Third' });
    });
    
    expect(result.current.toasts[0].message).toBe('First');
    expect(result.current.toasts[1].message).toBe('Second');
    expect(result.current.toasts[2].message).toBe('Third');
  });
});
