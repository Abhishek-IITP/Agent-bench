'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error for debugging
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="text-center animate-fade-in-up max-w-md">
        <div className="mb-8">
          <div className="inline-block">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-red-500/20 to-orange-600/20 border border-red-500/30 flex items-center justify-center">
              <span className="text-4xl font-bold text-red-400">!</span>
            </div>
          </div>
        </div>

        <h1 className="text-4xl font-bold text-white mb-2">Something Went Wrong</h1>
        <p className="text-slate-300 mb-2">
          An unexpected error occurred while processing your request.
        </p>
        
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-left">
            <p className="text-xs font-mono text-red-300 break-all">
              {error.message}
            </p>
          </div>
        )}

        <p className="text-slate-400 text-sm mt-4">Error ID: {error.digest}</p>

        <div className="flex flex-col gap-4 justify-center mt-8">
          <button
            onClick={reset}
            className="px-6 py-3 rounded-lg bg-blue-500 text-white font-medium hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
          <Link
            href="/"
            className="px-6 py-3 rounded-lg border border-slate-700 text-slate-300 font-medium hover:border-slate-500 hover:text-white transition-colors"
          >
            Go to Dashboard
          </Link>
        </div>
      </div>

      {/* Background decorations */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl opacity-20"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl opacity-20"></div>
      </div>
    </div>
  );
}
