'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

export function getBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: 'Dashboard', href: '/' }];

  let currentPath = '';
  for (const segment of segments) {
    currentPath += `/${segment}`;
    const label = segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' ');
    breadcrumbs.push({ label, href: currentPath });
  }

  return breadcrumbs;
}

export default function Header() {
  const pathname = usePathname();
  const breadcrumbs = getBreadcrumbs(pathname);
  const pageTitle = breadcrumbs[breadcrumbs.length - 1]?.label || 'Dashboard';

  return (
    <header className="bg-slate-900/40 glass border-b border-slate-700/50 sticky top-0 z-40 animate-slide-in-right">
      <div className="px-4 sm:px-6 lg:px-8 py-3 sm:py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4">
        {/* Left: Title and Breadcrumbs */}
        <div className="flex flex-col min-w-0">
          <h2 className="text-lg sm:text-2xl font-bold text-white mb-1 sm:mb-2 truncate">{pageTitle}</h2>
          <nav className="hidden sm:flex items-center gap-2 text-xs sm:text-sm overflow-x-auto">
            {breadcrumbs.map((item, index) => (
              <div key={item.label} className="flex items-center gap-2 whitespace-nowrap">
                {item.href ? (
                  <Link href={item.href} className="text-slate-400 hover:text-blue-400 transition-colors">
                    {item.label}
                  </Link>
                ) : (
                  <span className="text-slate-400">{item.label}</span>
                )}
                {index < breadcrumbs.length - 1 && <span className="text-slate-600">/</span>}
              </div>
            ))}
          </nav>
        </div>

        {/* Right: User Menu */}
        <div className="flex items-center gap-2 sm:gap-4 shrink-0">
          {/* Stats indicator */}
          <div className="hidden md:flex items-center gap-2 sm:gap-3 px-2 sm:px-4 py-2 rounded-lg bg-slate-700/20 text-xs sm:text-sm">
            <div className="text-right">
              <p className="text-xs text-slate-400">Status</p>
              <p className="text-xs sm:text-sm font-semibold text-green-400">Operational</p>
            </div>
          </div>

          {/* User menu (mock) */}
          <button
            type="button"
            className="flex items-center gap-2 px-2 sm:px-4 py-2 rounded-lg hover:bg-slate-700/30 transition-colors shrink-0"
            aria-label="User menu"
          >
            <div className="w-7 sm:w-8 h-7 sm:h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0">
              <span className="text-white text-xs sm:text-sm font-bold">U</span>
            </div>
            <div className="hidden sm:flex flex-col items-end">
              <p className="text-xs sm:text-sm font-medium text-white">User</p>
              <p className="text-xs text-slate-400">Admin</p>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
}
