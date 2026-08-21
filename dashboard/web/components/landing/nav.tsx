"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GitBranch, Menu, X } from "lucide-react";
import { DASHBOARD_ROUTES } from "@/lib/config";

const links = [
  { label: "Why",     href: "#why" },
  { label: "Metrics", href: "#metrics" },
  { label: "Compare", href: "#compare" },
  { label: "Roadmap", href: "#roadmap" },
];

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", h, { passive: true });
    return () => window.removeEventListener("scroll", h);
  }, []);

  return (
    <>
      <motion.header
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="fixed top-0 left-0 right-0 z-50 h-20 flex items-center bg-transparent"
      >
        <div className="max-w-7xl mx-auto px-6 w-full flex items-center justify-between">

          {/* Wordmark in Serif Font */}
          <a href="#" className="no-underline flex items-center gap-2 group">
            <span className="font-serif text-2xl text-white tracking-tight leading-none">
              AgentBench
            </span>
          </a>

          {/* Center Floating Pill Navbar */}
          <nav className="hidden md:flex items-center gap-7 px-7 py-2.5 rounded-full border border-white/10 bg-white/[0.04] backdrop-blur-md shadow-lg">
            {links.map((l) => (
              <a
                key={l.label}
                href={l.href}
                className="text-sm font-medium text-white/60 hover:text-white transition-colors no-underline"
              >
                {l.label}
              </a>
            ))}
          </nav>

          {/* Right: GitHub + CTA Buttons */}
          <div className="hidden md:flex items-center gap-3">
            <a
              href="https://github.com/Abhishek-IITP/Agent-bench"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium text-white/80 hover:text-white border border-white/15 hover:border-white/30 transition-all duration-150 no-underline bg-transparent"
            >
              <GitBranch size={14} />
              GitHub
            </a>
            <a
              href={DASHBOARD_ROUTES.home}
              className="inline-flex items-center gap-1.5 px-5 py-2 rounded-full text-sm font-semibold no-underline transition-all duration-150 hover:opacity-95 active:scale-[0.98] shadow-md shadow-emerald-500/20"
              style={{
                backgroundColor: "#4ade80",
                color: "#050508",
              }}
            >
              Join waitlist
            </a>
          </div>

          {/* Mobile menu button */}
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden text-white/70 hover:text-white transition-colors p-2 rounded-full border border-white/10 bg-white/5"
            aria-label="Toggle menu"
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </motion.header>

      {/* Mobile overlay */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="fixed inset-x-0 top-20 z-40 md:hidden bg-[#050508]/95 backdrop-blur-xl border-b border-white/10 p-6 flex flex-col gap-5 shadow-2xl"
          >
            <div className="flex flex-col gap-2">
              {links.map((l) => (
                <a
                  key={l.label}
                  href={l.href}
                  onClick={() => setMenuOpen(false)}
                  className="px-4 py-2.5 rounded-lg text-sm text-white/80 hover:text-white hover:bg-white/5 no-underline transition-colors"
                >
                  {l.label}
                </a>
              ))}
            </div>
            <div className="pt-4 border-t border-white/10 flex flex-col gap-3">
              <a
                href="https://github.com/Abhishek-IITP/Agent-bench"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setMenuOpen(false)}
                className="w-full py-2.5 rounded-full text-sm font-medium text-white/80 border border-white/15 text-center no-underline inline-flex items-center justify-center gap-2"
              >
                <GitBranch size={15} />
                GitHub Repository
              </a>
              <a
                href={DASHBOARD_ROUTES.home}
                onClick={() => setMenuOpen(false)}
                className="w-full py-2.5 rounded-full text-sm font-semibold text-center no-underline inline-flex items-center justify-center gap-2"
                style={{ backgroundColor: "#4ade80", color: "#050508" }}
              >
                Join waitlist
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
