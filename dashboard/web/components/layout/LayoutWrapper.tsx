'use client';

import Sidebar from './Sidebar';
import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';

interface LayoutWrapperProps {
  children: ReactNode;
}

export default function LayoutWrapper({ children }: LayoutWrapperProps) {
  const pathname = usePathname();
  const isLandingPage = pathname === '/';

  if (isLandingPage) {
    return (
      <div className="min-h-screen" style={{ background: '#050508' }}>
        {children}
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: '#000000' }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main scrollable content */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden">
        {children}
      </main>
    </div>
  );
}
