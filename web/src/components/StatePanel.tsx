"use client";

interface StatePanelProps {
  state: 'loading' | 'empty' | 'error' | 'success';
  message?: string;
}

export default function StatePanel({ state, message }: StatePanelProps) {
  const render = () => {
    switch (state) {
      case 'loading':
        return <p className="text-muted animate-pulse">Loading…</p>;
      case 'empty':
        return <p className="text-muted">{message || 'Nothing to display.'}</p>;
      case 'error':
        return <p className="text-red-600">Error: {message || 'Something went wrong.'}</p>;
      case 'success':
        return <p className="text-success">{message || 'Success!'}</p>;
    }
  };
  return <div className="p-4 bg-muted rounded-md">{render()}</div>;
}
