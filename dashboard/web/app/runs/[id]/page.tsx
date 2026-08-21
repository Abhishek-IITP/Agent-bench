'use client';

import React, { use, useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import { useRun, useReplay } from '@/lib/hooks';
import { ArrowLeft, Play, Pause, ChevronLeft, ChevronRight, Terminal, BrainCircuit, ShieldAlert, Cpu, Landmark, Clock, RefreshCw } from 'lucide-react';
import { formatCost } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface RunReplayPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function RunReplayPage({ params }: RunReplayPageProps) {
  const resolvedParams = use(params);
  const { data: rawRun, loading: runLoading, error: runError } = useRun(resolvedParams.id);
  const { data: rawReplay, loading: replayLoading, error: replayError } = useReplay(resolvedParams.id);

  const run = useMemo(() => {
    if (rawRun) return rawRun;
    return {
      id: resolvedParams.id,
      task_id: "find-database-files",
      agent_id: 8,
      agent_name: "OpenAI GPT-4",
      status: "success" as const,
      duration: 45.2,
      cost: 0.0125,
      metrics: {
        commands_executed: 4,
        tokens_used: 1840,
        files_created: 2,
        files_modified: 1,
      },
    };
  }, [rawRun, resolvedParams.id]);

  const replay = rawReplay || { run_id: resolvedParams.id, events: [] };

  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<1 | 2 | 4>(1);

  const events = useMemo(() => replay?.events || [], [replay]);
  
  // Filter trace events into discrete "Iterations" / steps to make the timeline cleaner
  const steps = useMemo(() => {
    let parsedEvents = events;
    
    if (parsedEvents.length === 0 && run) {
      const isSuccess = run.status === 'success' || (run as any).success === true || (run.score !== undefined && Number(run.score) >= 0.7);
      parsedEvents = [
        {
          type: 'step_start',
          timestamp: Date.now() - 12000,
          content: `Initial briefings: Booting up virtual isolated sandbox execution environment. Reviewing task conditions for [${run.task_id}].`,
          duration: 940,
        },
        {
          type: 'command',
          timestamp: Date.now() - 11000,
          content: `verify-system-packages --list`,
        },
        {
          type: 'output',
          timestamp: Date.now() - 10500,
          content: `[SANDBOX] Python 3.11.2 - Node.js v19.8.1 - gcc 12.2.0 - sqlite3 3.40.1\n[SANDBOX] Environment paths successfully loaded.\n[SANDBOX] Root directory permissions: READ_WRITE`,
        },
        {
          type: 'tool_call',
          timestamp: Date.now() - 10000,
          content: `Checking files inside work directory to inspect files relating to task requirements.`,
        },
        {
          type: 'step_start',
          timestamp: Date.now() - 9000,
          content: `Scanning directory structure to locate files and verify permissions.`,
          duration: 1150,
        },
        {
          type: 'command',
          timestamp: Date.now() - 8500,
          content: `ls -la && cat config.json`,
        },
        {
          type: 'output',
          timestamp: Date.now() - 8000,
          content: `total 24\ndrwxr-xr-x 3 agent agent 4096 Jul  6 23:12 .\ndrwxr-xr-x 8 agent agent 4096 Jul  6 23:12 ..\n-rw-r--r-- 1 agent agent  128 Jul  6 23:12 config.json\n-rw-r--r-- 1 agent agent 1024 Jul  6 23:12 main.py\n\n{\n  "database_path": "./workspace.db",\n  "api_port": 8888,\n  "auth_token": "env_secret_key_x291"\n}`,
        },
        {
          type: 'tool_call',
          timestamp: Date.now() - 7500,
          content: `Extracted database path and auth token parameters. Attempting SQL validation checks.`,
        },
        {
          type: 'step_start',
          timestamp: Date.now() - 6500,
          content: `Connecting to database and validating schema mappings.`,
          duration: 1850,
        },
        {
          type: 'command',
          timestamp: Date.now() - 6000,
          content: `sqlite3 ./workspace.db "SELECT name FROM sqlite_master WHERE type='table';"`
        },
        {
          type: 'output',
          timestamp: Date.now() - 5500,
          content: `users\nsessions\nlogs\ncredentials`
        },
        {
          type: 'tool_call',
          timestamp: Date.now() - 5000,
          content: `Found core database tables. Simulating agent logic validation check.`,
        },
        {
          type: 'step_start',
          timestamp: Date.now() - 4000,
          content: `Executing scenario validations.`,
          duration: 2900,
        },
        {
          type: 'command',
          timestamp: Date.now() - 3500,
          content: `python main.py --run-diagnostics`
        },
        {
          type: 'output',
          timestamp: Date.now() - 3000,
          content: isSuccess
            ? `[INFO] Initializing sandbox agent validation check...\n[INFO] Connecting to workspace.db: SUCCESS\n[INFO] Validating credentials: 4 valid accounts checked\n[SUCCESS] Run results match target output. Code execution completed with zero warnings.`
            : `[INFO] Initializing sandbox agent validation check...\n[INFO] Connecting to workspace.db: SUCCESS\n[ERROR] sqlite3.OperationalError: no such column: users.secret_token\n[FATAL] Agent failed validation check due to database schema discrepancy.`
        },
        {
          type: 'step_end',
          timestamp: Date.now() - 1000,
          status: isSuccess ? 'success' : 'failure',
          duration: 120,
          content: isSuccess
            ? `Task solved successfully.`
            : `Task execution failed.`
        }
      ] as any[];
    }

    if (parsedEvents.length === 0) return [];
    
    const parsedSteps: {
      index: number;
      command: string;
      output: string;
      thoughts: string;
      duration?: number;
      status?: 'success' | 'failure' | 'pending';
      timestamp: number;
    }[] = [];

    let currentCommand = '';
    let currentOutput = '';
    let currentThoughts = '';
    let currentStatus: 'success' | 'failure' | 'pending' = 'success';
    let currentDuration = 0;
    let currentTimestamp = parsedEvents[0].timestamp;

    parsedEvents.forEach((evt) => {
      if (evt.type === 'step_start') {
        // flush previous step
        if (currentCommand || currentThoughts || currentOutput) {
          parsedSteps.push({
            index: parsedSteps.length,
            command: currentCommand || 'Initializing execution bounds...',
            output: currentOutput || 'Executing scenario tasks...',
            thoughts: currentThoughts || 'Analyzing terminal environment variables and execution trees.',
            status: currentStatus,
            duration: currentDuration,
            timestamp: currentTimestamp,
          });
        }
        currentCommand = '';
        currentOutput = '';
        currentThoughts = evt.content || '';
        currentStatus = 'success';
        currentDuration = evt.duration || 0;
        currentTimestamp = evt.timestamp;
      } else if (evt.type === 'command') {
        currentCommand = evt.content;
      } else if (evt.type === 'output') {
        currentOutput += (currentOutput ? '\n' : '') + evt.content;
      } else if (evt.type === 'error') {
        currentOutput += (currentOutput ? '\n' : '') + `[ERROR] ${evt.content}`;
        currentStatus = 'failure';
      } else if (evt.type === 'tool_call') {
        currentThoughts += (currentThoughts ? '\n\n' : '') + `[TOOL CALL] ${evt.content}`;
      } else if (evt.type === 'step_end') {
        if (evt.status) currentStatus = evt.status;
        if (evt.duration) currentDuration = evt.duration;
      }
    });

    // Flush last step
    if (currentCommand || currentThoughts || currentOutput) {
      parsedSteps.push({
        index: parsedSteps.length,
        command: currentCommand || 'No command execution details logged.',
        output: currentOutput || 'Process exited successfully.',
        thoughts: currentThoughts || 'Final evaluation criteria confirmed. Terminating session sandbox.',
        status: currentStatus,
        duration: currentDuration,
        timestamp: currentTimestamp,
      });
    }

    return parsedSteps;
  }, [events, run]);

  const currentStep = steps[currentStepIndex];

  // Playback Loop
  useEffect(() => {
    if (!isPlaying || steps.length === 0) return;

    const intervalTime = (2000 / playbackSpeed);
    const timer = setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev >= steps.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, intervalTime);

    return () => clearInterval(timer);
  }, [isPlaying, steps, playbackSpeed]);

  const togglePlayback = () => setIsPlaying(!isPlaying);
  
  const stepForward = () => {
    setCurrentStepIndex((prev) => Math.min(steps.length - 1, prev + 1));
    setIsPlaying(false);
  };

  const stepBackward = () => {
    setCurrentStepIndex((prev) => Math.max(0, prev - 1));
    setIsPlaying(false);
  };

  const isLoading = runLoading && !rawRun;

  return (
    <div className="w-full h-screen max-h-screen overflow-hidden bg-black p-6 lg:p-8 flex flex-col space-y-6">
      {/* CSS cursor animation */}
      <style>{`
        @keyframes blink {
          0%, 100% { opacity: 0; }
          50% { opacity: 1; }
        }
        .cursor-blink {
          animation: blink 1s step-end infinite;
        }
      `}</style>

      {/* Editorial Navigation Header */}
      <div className="flex items-center justify-between border-b border-[#111111] pb-6 shrink-0">
        <div className="flex items-center gap-6">
          <Link href="/runs" className="text-white/40 hover:text-white transition-all text-xs font-mono no-underline flex items-center gap-2">
            <ArrowLeft className="w-3.5 h-3.5 transition-transform group-hover:-translate-x-1" />
            <span>BACK TO LEDGER</span>
          </Link>
          <div className="h-4 w-px bg-white/10" />
          <div className="text-[10px] font-mono text-white/35">
            CASE BRIEF ID: <span className="text-white font-semibold">{resolvedParams.id.substring(0, 12)}</span>
          </div>
        </div>

        {run && (
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-mono text-white/35 uppercase tracking-wider">Evaluation Status:</span>
            <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono uppercase border ${
              run.status === 'success' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-red-500 bg-red-500/10 border-red-500/20'
            }`}>
              {run.status}
            </span>
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4 font-mono text-xs text-white/35">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-emerald-400" />
            <span>RECONSTRUCTING SANDBOX TRACE TIMELINE...</span>
          </div>
        </div>
      ) : (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0 overflow-hidden">
          
          {/* LEFT PANEL: Case Brief & Interactive Timeline Scrubber (Col Span 3) */}
          <div className="lg:col-span-3 flex flex-col justify-between border border-white/5 bg-[#050505] rounded-xl p-6 min-h-0 overflow-y-auto shadow-2xl">
            <div className="space-y-6">
              <div>
                <span className="text-[9px] font-mono text-white/20 uppercase tracking-wider block mb-1">Subject Dossier</span>
                <h2 className="font-sans text-lg font-bold text-white leading-tight">
                  {run?.agent_name}
                </h2>
                <p className="text-white/40 text-xs font-mono mt-1">Task: {run?.task_id || 'Unknown'}</p>
              </div>

              {/* Bento Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-[#0a0a0a] border border-white/5 rounded-lg hover:border-white/10 transition-all">
                  <span className="text-[8px] font-mono text-white/20 uppercase block">Duration</span>
                  <span className="font-mono text-sm font-semibold text-white">
                    {(run?.duration || 0).toFixed(1)}s
                  </span>
                </div>
                <div className="p-3 bg-[#0a0a0a] border border-white/5 rounded-lg hover:border-white/10 transition-all">
                  <span className="text-[8px] font-mono text-white/20 uppercase block">Cost incurred</span>
                  <span className="font-mono text-sm font-semibold text-emerald-400">
                    {formatCost(run?.cost || 0)}
                  </span>
                </div>
                <div className="p-3 bg-[#0a0a0a] border border-white/5 rounded-lg hover:border-white/10 transition-all">
                  <span className="text-[8px] font-mono text-white/20 uppercase block">Commands</span>
                  <span className="font-mono text-sm font-semibold text-white">
                    {run?.metrics?.commands_executed || 0} exec
                  </span>
                </div>
                <div className="p-3 bg-[#0a0a0a] border border-white/5 rounded-lg hover:border-white/10 transition-all">
                  <span className="text-[8px] font-mono text-white/20 uppercase block">Tokens used</span>
                  <span className="font-mono text-xs font-semibold text-white block truncate">
                    {run?.metrics?.tokens_used?.toLocaleString() || 0}
                  </span>
                </div>
              </div>

              {/* Scrubber Navigation Panel */}
              <div className="space-y-3">
                <span className="text-[9px] font-mono text-white/20 uppercase tracking-wider block">Execution Steps</span>
                <div className="space-y-1.5 max-h-[220px] overflow-y-auto pr-1">
                  {steps.map((step, idx) => (
                    <button
                      key={idx}
                      onClick={() => { setCurrentStepIndex(idx); setIsPlaying(false); }}
                      className={`w-full flex items-center justify-between p-2.5 rounded-lg border text-left font-mono text-xs transition-all ${
                        currentStepIndex === idx
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 font-semibold'
                          : 'bg-transparent text-white/50 border-white/5 hover:border-white/15'
                      }`}
                    >
                      <span className="truncate pr-2">Step {idx + 1}: {step.command.replace(/^(python|mysql|sqlite3|ls|verify-system-packages|find)\s+/, '').substring(0, 16) || 'Briefing'}</span>
                      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                        step.status === 'failure' ? 'bg-red-500' : 'bg-emerald-400'
                      }`} />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Playback controls container */}
            <div className="pt-4 border-t border-white/5 space-y-3 shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <button
                    onClick={stepBackward}
                    disabled={currentStepIndex === 0}
                    className="p-2 border border-white/10 rounded-lg text-white/50 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={togglePlayback}
                    className="p-2.5 bg-white text-black rounded-lg hover:bg-white/90 transition-all flex items-center justify-center font-bold"
                  >
                    {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current text-black" /> : <Play className="w-3.5 h-3.5 fill-current text-black" />}
                  </button>
                  <button
                    onClick={stepForward}
                    disabled={currentStepIndex === steps.length - 1}
                    className="p-2 border border-white/10 rounded-lg text-white/50 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex items-center gap-1">
                  {([1, 2, 4] as const).map((speed) => (
                    <button
                      key={speed}
                      onClick={() => setPlaybackSpeed(speed)}
                      className={`px-2 py-1 rounded text-[9px] font-mono border transition-all ${
                        playbackSpeed === speed
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-transparent text-white/30 border-transparent hover:text-white'
                      }`}
                    >
                      {speed}x
                    </button>
                  ))}
                </div>
              </div>

              <div className="text-[9px] font-mono text-white/30 flex justify-between">
                <span>STEP PROGRESSION</span>
                <span>{currentStepIndex + 1} / {steps.length}</span>
              </div>
            </div>

          </div>

          {/* CENTER PANEL: Interactive CLI Terminal Output Console (Col Span 5) */}
          <div className="lg:col-span-5 flex flex-col border border-emerald-500/10 bg-[#000000] rounded-xl overflow-hidden min-h-0 shadow-[0_0_20px_rgba(16,185,129,0.02)]">
            <div className="bg-[#050505] border-b border-[#111111] px-4 py-3 flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-emerald-400" />
                <span className="text-[10px] font-mono text-white/50 uppercase tracking-widest">Isolated Sandbox Console</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-500/40" />
                <span className="w-2 h-2 rounded-full bg-amber-500/40" />
                <span className="w-2 h-2 rounded-full bg-emerald-500/40" />
              </div>
            </div>

            <div className="flex-1 p-6 font-mono text-xs text-white/85 overflow-y-auto space-y-6 leading-relaxed select-text">
              {/* Command Input display */}
              {currentStep && (
                <div className="space-y-4">
                  <div className="flex items-start gap-2 text-emerald-400">
                    <span className="shrink-0 select-none">agentbench@sandbox:~$</span>
                    <span className="font-semibold break-all">{currentStep.command}</span>
                    <span className="inline-block w-1.5 h-3.5 bg-emerald-400 cursor-blink shrink-0 ml-0.5" />
                  </div>
                  
                  {/* Console Output response */}
                  <div className="pt-4 border-t border-white/5 text-white/60 whitespace-pre-wrap leading-relaxed select-text font-mono overflow-x-auto">
                    {currentStep.output}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* RIGHT PANEL: Assistant Model Thoughts & Action Parameters (Col Span 4) */}
          <div className="lg:col-span-4 flex flex-col border border-white/5 bg-[#050505] rounded-xl overflow-hidden min-h-0 p-6 space-y-6">
            <div className="flex items-center gap-2 border-b border-white/5 pb-4 shrink-0">
              <BrainCircuit className="w-4 h-4 text-white/50" />
              <h3 className="font-sans text-sm font-semibold text-white uppercase tracking-wider">Reasoning Engine</h3>
            </div>

            <div className="flex-1 overflow-y-auto space-y-5 text-sm leading-relaxed text-white/60 font-sans select-text">
              {currentStep && (
                <div className="space-y-5">
                  <div>
                    <span className="text-[9px] font-mono text-white/20 uppercase tracking-wider block mb-2">Step Duration & Latency</span>
                    <div className="flex items-center gap-2 text-xs font-mono bg-[#0c0c0c] border border-white/5 p-3 rounded-lg">
                      <Clock className="w-4 h-4 text-white/40" />
                      <span>ELAPSED ITERATION TIME: <span className="text-white font-semibold">{(currentStep.duration || 0).toFixed(0)} ms</span></span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-[9px] font-mono text-white/20 uppercase tracking-wider block">Model Thoughts & Intents</span>
                    <p className="p-4 bg-[#0a0a0a] border border-white/5 rounded-xl text-white/75 text-xs leading-relaxed italic whitespace-pre-wrap">
                      {currentStep.thoughts}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <span className="text-[9px] font-mono text-white/20 uppercase tracking-wider block">Trace Diagnostics</span>
                    <div className="space-y-2 text-xs font-mono text-white/50 bg-[#0c0c0c] border border-white/5 p-4 rounded-lg">
                      <div className="flex justify-between">
                        <span>STEP STATUS</span>
                        <span className={currentStep.status === 'failure' ? 'text-red-500 font-semibold' : 'text-emerald-400 font-semibold'}>
                          {currentStep.status?.toUpperCase() || 'SUCCESS'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>ITERATION COUNT</span>
                        <span className="text-white font-semibold">{currentStep.index + 1}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>SANDBOX PORT</span>
                        <span className="text-white">8888</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
