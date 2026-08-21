'use client';

import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-900/50 glass border-t border-slate-700/50 mt-auto animate-fade-in-up">
      <div className="px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <h3 className="text-white font-bold text-sm mb-4">AgentBench</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              A comprehensive benchmarking platform for AI agents. Build, test, and measure agent performance.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Product</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/" className="text-slate-400 hover:text-blue-400 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/tasks" className="text-slate-400 hover:text-blue-400 transition-colors">
                  Tasks
                </Link>
              </li>
              <li>
                <Link href="/leaderboard" className="text-slate-400 hover:text-blue-400 transition-colors">
                  Leaderboard
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Resources</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="/" className="text-slate-400 hover:text-blue-400 transition-colors">
                  Documentation
                </a>
              </li>
              <li>
                <a href="/" className="text-slate-400 hover:text-blue-400 transition-colors">
                  API Reference
                </a>
              </li>
              <li>
                <a href="/" className="text-slate-400 hover:text-blue-400 transition-colors">
                  GitHub
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Legal</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="/" className="text-slate-400 hover:text-blue-400 transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="/" className="text-slate-400 hover:text-blue-400 transition-colors">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="/" className="text-slate-400 hover:text-blue-400 transition-colors">
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-slate-700/50 pt-6">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-xs text-slate-500">
              © {currentYear} AgentBench. All rights reserved.
            </p>
            <div className="flex items-center gap-4 text-xs">
              <span className="text-slate-400">Built with precision | Powered by AI</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
