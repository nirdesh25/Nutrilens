import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Card } from './Card';
import { Button } from './Button';

interface ErrorCardProps {
  message: string;
  onRetry: () => void;
}

export function ErrorCard({ message, onRetry }: ErrorCardProps) {
  return (
    <Card className="border-2 border-red-200">
      <div className="flex flex-col items-center justify-center text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <p className="text-red-700 text-lg font-medium mb-4">{message}</p>
        <Button variant="danger" onClick={onRetry}>
          Retry
        </Button>
      </div>
    </Card>
  );
}
