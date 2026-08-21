'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { LayoutGrid, ClipboardList, Play, Trophy, Activity, Terminal, Zap, Home } from 'lucide-react';

import { useEffect, useState } from 'react';

const navItems = [
  {
    label: 'Overview',
    href: '/overview',
    icon: <LayoutGrid className="w-4 h-4" />,
  },
  {
    label: 'Test Model',
    href: '/test',
    icon: <Zap className="w-4 h-4" />,
    highlight: true,
  },
  {
    label: 'Tasks',
    href: '/tasks',
    icon: <ClipboardList className="w-4 h-4" />,
  },
  {
    label: 'Runs',
    href: '/runs',
    icon: <Play className="w-4 h-4" />,
  },
  {
    label: 'Leaderboard',
    href: '/leaderboard',
    icon: <Trophy className="w-4 h-4" />,
  },
  {
    label: 'Health',
    href: '/health',
    icon: <Activity className="w-4 h-4" />,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    setTimeStr(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    const timer = setInterval(() => {
      setTimeStr(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <aside
      className="hidden md:flex flex-col select-none relative z-30"
      style={{
        width: '240px',
        minWidth: '240px',
        background: '#000000',
        borderRight: '1px solid #111111',
        height: '100vh',
        position: 'sticky',
        top: 0,
      }}
    >
      {/* Brand Logo */}
      <div className="p-8 border-b border-[#111111]">
        <Link href="/" className="flex items-center gap-3 group no-underline">
          <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-105">
            <Terminal className="w-4 h-4 text-black" />
          </div>
          <div>
            <p className="font-display text-xl text-white tracking-tight leading-none">
              AgentBench
            </p>
            <p className="text-[10px] text-white/35 font-mono tracking-widest uppercase mt-1">
              Intel Center
            </p>
          </div>
        </Link>
      </div>

      {/* Live System Pulse */}
      <div className="px-8 py-4 border-b border-[#111111] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </div>
          <span className="text-[10px] font-mono tracking-wider text-white/40 uppercase">
            System Live
          </span>
        </div>
        <span suppressHydrationWarning className="text-[10px] font-mono text-white/20">
          {timeStr}
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-8 space-y-8">
        <div>
          <p className="text-[9px] font-mono text-white/25 tracking-widest uppercase px-4 mb-4">
            Navigation
          </p>
          <div className="space-y-1">
            {navItems.map((item: any) => {
              const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors relative group no-underline ${
                    item.highlight ? 'border border-emerald-500/20 bg-emerald-500/5' : ''
                  }`}
                  style={{
                    color: item.highlight ? '#10b981' : isActive ? '#ffffff' : 'rgba(255,255,255,0.4)',
                  }}
                >
                  {/* Sliding Pill Active Highlight */}
                  {isActive && !item.highlight && (
                    <motion.div
                      layoutId="sidebar-active-pill"
                      className="absolute inset-0 bg-[#111111] border border-white/5 rounded-lg -z-10"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}

                  {/* Left Active indicator bar */}
                  {isActive && !item.highlight && (
                    <motion.div
                      layoutId="sidebar-active-bar"
                      className="absolute left-0 w-[2px] h-[16px] bg-emerald-500 rounded-r"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}

                  <span className={`transition-colors duration-200 ${
                    item.highlight ? 'text-emerald-500' : isActive ? 'text-white' : 'text-white/30 group-hover:text-white/60'
                  }`}>
                    {item.icon}
                  </span>
                  <span className="font-sans font-medium">
                    {item.label}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Bottom Footer Info & Home Link */}
      <div className="p-6 border-t border-[#111111] space-y-3">
        <Link
          href="/"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-xs font-mono text-white/60 hover:text-white transition-all no-underline"
        >
          <Home className="w-3.5 h-3.5" />
          <span>Back to Landing</span>
        </Link>
        <div className="flex flex-col gap-0.5 font-mono text-[9px] text-white/25">
          <p>© 2026 AGENTBENCH</p>
          <p>VERSION 5.4.0</p>
        </div>
      </div>
    </aside>
  );
}
