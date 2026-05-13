import React from 'react';
import { Spinner } from './Spinner';

interface LoadingPageProps {
  message?: string;
}

export function LoadingPage({ message = 'Loading...' }: LoadingPageProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <Spinner size="lg" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
}
