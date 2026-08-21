import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="text-center animate-fade-in-up">
        <div className="mb-8">
          <div className="inline-block">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-600/20 border border-blue-500/30 flex items-center justify-center">
              <span className="text-4xl font-bold text-blue-400">404</span>
            </div>
          </div>
        </div>

        <h1 className="text-4xl font-bold text-white mb-2">Page Not Found</h1>
        <p className="text-slate-300 max-w-md mb-8">
          The page you're looking for doesn't exist. It might have been moved or deleted.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="px-6 py-3 rounded-lg bg-blue-500 text-white font-medium hover:bg-blue-600 transition-colors"
          >
            Go to Dashboard
          </Link>
          <a
            href="/"
            className="px-6 py-3 rounded-lg border border-slate-700 text-slate-300 font-medium hover:border-slate-500 hover:text-white transition-colors"
          >
            Back to Home
          </a>
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
