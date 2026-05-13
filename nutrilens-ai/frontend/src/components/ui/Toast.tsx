'use client';

import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react';

interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  onClose: (id: string) => void;
}

export function Toast({ id, type, message, onClose }: ToastProps) {
  const [visible, setVisible] = useState(false);

  // Longer duration for error/warning alerts
  const duration = type === 'error' ? 6000 : type === 'warning' ? 5000 : 3000;

  useEffect(() => {
    // Trigger entrance animation
    setTimeout(() => setVisible(true), 10);

    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(() => onClose(id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, onClose, duration]);

  const typeConfig = {
    success: {
      bg: 'bg-emerald-500/20 border-emerald-500/50',
      text: 'text-emerald-200',
      icon: 'text-emerald-400',
      bar: 'bg-emerald-500',
      Icon: CheckCircle,
    },
    error: {
      bg: 'bg-red-500/20 border-red-500/50',
      text: 'text-red-200',
      icon: 'text-red-400',
      bar: 'bg-red-500',
      Icon: XCircle,
    },
    info: {
      bg: 'bg-blue-500/20 border-blue-500/50',
      text: 'text-blue-200',
      icon: 'text-blue-400',
      bar: 'bg-blue-500',
      Icon: Info,
    },
    warning: {
      bg: 'bg-orange-500/20 border-orange-500/50',
      text: 'text-orange-200',
      icon: 'text-orange-400',
      bar: 'bg-orange-500',
      Icon: AlertTriangle,
    },
  };

  const config = typeConfig[type];
  const Icon = config.Icon;

  return (
    <div
      className={`
        ${config.bg} ${config.text}
        backdrop-blur-xl border rounded-2xl shadow-2xl
        p-4 flex items-start gap-3 min-w-[320px] max-w-sm
        transition-all duration-300 overflow-hidden relative
        ${visible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'}
      `}
      role="alert"
    >
      {/* Animated progress bar */}
      <div
        className={`absolute bottom-0 left-0 h-0.5 ${config.bar} opacity-60`}
        style={{ animation: `shrink ${duration}ms linear forwards` }}
      />

      <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${config.icon}`} />
      <p className="flex-1 text-sm font-medium leading-relaxed">{message}</p>
      <button
        onClick={() => { setVisible(false); setTimeout(() => onClose(id), 300); }}
        className="flex-shrink-0 hover:opacity-80 transition mt-0.5"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
