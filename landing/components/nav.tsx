"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GitBranch, Menu, X } from "lucide-react";

const links = [
  { label: "Why",      href: "#why" },
  { label: "Metrics",  href: "#metrics" },
  { label: "Compare",  href: "#compare" },
  { label: "Roadmap",  href: "#roadmap" },
];

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", h, { passive: true });
    return () => window.removeEventListener("scroll", h);
  }, []);

  return (
    <>
      <motion.header
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className={`fixed top-0 left-0 right-0 z-50 h-16 flex items-center transition-all duration-300 ${
          scrolled
            ? "bg-bg-void/80 backdrop-blur-md border-b border-border-subtle"
            : "bg-transparent border-b border-transparent"
        }`}
      >
        <div className="max-w-6xl mx-auto px-6 w-full flex items-center justify-between">

          {/* Wordmark */}
          <a href="#" className="no-underline flex items-center gap-2 group">
            <span className="font-display text-xl text-white tracking-tight leading-none">
              AgentBench
            </span>
          </a>

          {/* Desktop nav — centered, pill-shaped like Polaris */}
          <nav className="hidden md:flex items-center gap-1 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm">
            {links.map((l) => (
              <a
                key={l.label}
                href={l.href}
                className="px-4 py-1.5 rounded-full text-sm text-white/60 hover:text-white hover:bg-white/10 transition-all duration-200 no-underline"
              >
                {l.label}
              </a>
            ))}
          </nav>

          {/* Right: GitHub + CTA */}
          <div className="hidden md:flex items-center gap-2.5">
            <a
              href="https://github.com/Abhishek-IITP/Agent-bench"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-sm text-white/60 hover:text-white border border-white/15 hover:border-white/30 transition-all duration-200 no-underline bg-transparent hover:bg-white/5"
            >
              <GitBranch size={13} />
              GitHub
            </a>
            <a
              href="#waitlist"
              className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-semibold no-underline transition-all duration-200 hover:opacity-90"
              style={{
                backgroundColor: "#4ade80",
                color: "#050508",
                boxShadow: "0 0 20px rgba(74,222,128,0.3)",
              }}
            >
              Join waitlist
            </a>
          </div>

          {/* Mobile menu button */}
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden text-white/60 hover:text-white transition-colors p-1"
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
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 md:hidden flex flex-col items-center justify-center gap-8"
            style={{ backgroundColor: "#050508" }}
          >
            {links.map((l, i) => (
              <motion.a
                key={l.label}
                href={l.href}
                onClick={() => setMenuOpen(false)}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.07 }}
                className="font-display text-4xl text-white no-underline"
              >
                {l.label}
              </motion.a>
            ))}
            <motion.a
              href="#waitlist"
              onClick={() => setMenuOpen(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.35 }}
              className="mt-4 px-8 py-3 rounded-full font-semibold text-base no-underline"
              style={{ backgroundColor: "#4ade80", color: "#050508" }}
            >
              Join waitlist
            </motion.a>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
