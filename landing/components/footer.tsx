import { GitBranch } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border-subtle py-12 px-6 bg-bg-void">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <span className="font-display text-lg text-text-primary">AgentBench</span>
          <p className="text-sm text-text-muted mt-1">Reliability-first AI agent benchmarking</p>
        </div>
        <div className="flex items-center gap-6">
          <a
            href="https://github.com/Abhishek-IITP/Agent-bench"
            target="_blank"
            rel="noopener noreferrer"
            className="text-text-muted hover:text-text-primary transition-colors"
            aria-label="GitHub"
          >
            <GitBranch size={18} />
          </a>
          <span className="text-label-mono">MIT · Built in public · 2026</span>
        </div>
      </div>
    </footer>
  );
}
