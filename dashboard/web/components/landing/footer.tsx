import { GitBranch, ExternalLink } from "lucide-react";
import { DASHBOARD_ROUTES } from "@/lib/config";

export function Footer() {
  return (
    <footer className="border-t border-white/10 py-12 px-6 bg-bg-void">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <span className="font-display text-lg text-white font-bold">AgentBench</span>
          <p className="text-sm text-white/50 mt-1">Reliability-first AI agent benchmarking framework & platform</p>
        </div>
        <div className="flex flex-wrap items-center gap-6 text-sm font-mono text-white/60">
          <a
            href={DASHBOARD_ROUTES.home}
            className="hover:text-emerald-400 transition-colors no-underline inline-flex items-center gap-1"
          >
            Dashboard <ExternalLink size={12} />
          </a>
          <a
            href={DASHBOARD_ROUTES.test}
            className="hover:text-emerald-400 transition-colors no-underline"
          >
            Test Model
          </a>
          <a
            href={DASHBOARD_ROUTES.leaderboard}
            className="hover:text-emerald-400 transition-colors no-underline"
          >
            Leaderboard
          </a>
          <a
            href="https://github.com/Abhishek-IITP/Agent-bench"
            target="_blank"
            rel="noopener noreferrer"
            className="text-white/60 hover:text-white transition-colors no-underline flex items-center gap-1.5"
            aria-label="GitHub"
          >
            <GitBranch size={16} />
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
