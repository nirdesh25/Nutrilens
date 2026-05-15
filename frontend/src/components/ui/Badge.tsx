import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant: 'green' | 'orange' | 'red' | 'blue' | 'gray' | 'brown';
}

export function Badge({ children, variant }: BadgeProps) {
  const variantStyles = {
    green: 'bg-green-100 text-green-700',
    orange: 'bg-orange-100 text-orange-700',
    red: 'bg-red-100 text-red-700',
    blue: 'bg-blue-100 text-blue-700',
    gray: 'bg-gray-100 text-gray-700',
    brown: 'bg-amber-100 text-amber-700',
  };
  
  return (
    <span className={`px-2 md:px-3 py-1 rounded-full text-xs md:text-sm font-medium ${variantStyles[variant]}`}>
      {children}
    </span>
  );
}
