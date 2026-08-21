"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Play, Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";

// Local UI components replacing missing shadcn files
function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={`rounded-xl border border-zinc-800 bg-zinc-900 ${className || ""}`} {...props} />;
}

function Button({ className, variant, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: string }) {
  const base = "inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50";
  const styles = variant === "outline"
    ? "border border-zinc-700 bg-transparent text-white hover:bg-zinc-800"
    : className || "";
  return <button className={`${base} ${styles}`} {...props} />;
}

function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`flex h-10 w-full rounded-md border border-zinc-700 bg-black px-3 py-2 text-sm text-white placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-zinc-400 ${className || ""}`} {...props} />;
}

function Label({ className, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return <label className={`text-sm font-medium leading-none ${className || ""}`} {...props} />;
}

function Badge({ className, variant, ...props }: React.HTMLAttributes<HTMLDivElement> & { variant?: string }) {
  const variantStyles = variant === 'destructive' 
    ? 'bg-red-500/20 text-red-400 border-red-500/30' 
    : 'bg-zinc-800 text-zinc-300 border-zinc-700';
  return <div className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors ${variantStyles} ${className || ""}`} {...props} />;
}

export default function TestModelPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    modelType: "openai",
    modelName: "gpt-4",
    apiKey: "",
    task: "find-database-files",
    runs: 1,
    notes: "",
  });

  const tasks = [
    { id: "find-database-files", name: "Find Database Files", difficulty: "easy" },
    { id: "extract-emails", name: "Extract Email Addresses", difficulty: "easy" },
    { id: "sort-json-by-field", name: "Sort JSON by Field", difficulty: "easy" },
    { id: "calculate-statistics", name: "Calculate Statistics", difficulty: "medium" },
    { id: "debug-python-error", name: "Debug Python Error", difficulty: "medium" },
    { id: "count-error-lines", name: "Count Error Lines", difficulty: "easy" },
    { id: "filter-logs-by-date", name: "Filter Logs by Date", difficulty: "medium" },
    { id: "find-largest-file", name: "Find Largest File", difficulty: "easy" },
    { id: "parse-config-values", name: "Parse Config Values", difficulty: "medium" },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";
      const res = await fetch(`${apiUrl}/api/bench/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run benchmark");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold mb-4">Test Your Model</h1>
          <p className="text-gray-400 text-lg">
            Run your AI model against our benchmark tasks and see how it performs.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Configuration Form */}
          <Card className="bg-zinc-900 border-zinc-800 p-8">
            <h2 className="text-2xl font-semibold mb-6">Configuration</h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Model Type */}
              <div>
                <Label htmlFor="modelType" className="text-white mb-2 block">Model Provider</Label>
                <select
                  value={formData.modelType}
                  onChange={(e) => setFormData({ ...formData, modelType: e.target.value })}
                  className="w-full h-10 rounded-md border border-zinc-700 bg-black px-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-zinc-400"
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="local">Local Model</option>
                  <option value="custom">Custom API</option>
                </select>
              </div>

              {/* Model Name */}
              <div>
                <Label htmlFor="modelName" className="text-white mb-2 block">Model Name</Label>
                <Input
                  id="modelName"
                  value={formData.modelName}
                  onChange={(e) => setFormData({ ...formData, modelName: e.target.value })}
                  placeholder="e.g., gpt-4, claude-3-opus"
                  className="bg-black border-zinc-700"
                />
              </div>

              {/* API Key */}
              <div>
                <Label htmlFor="apiKey" className="text-white mb-2 block">API Key (optional)</Label>
                <Input
                  id="apiKey"
                  type="password"
                  value={formData.apiKey}
                  onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                  placeholder="sk-..."
                  className="bg-black border-zinc-700"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty to use configured keys
                </p>
              </div>

              {/* Task Selection */}
              <div>
                <Label htmlFor="task" className="text-white mb-2 block">Benchmark Task</Label>
                <select
                  value={formData.task}
                  onChange={(e) => setFormData({ ...formData, task: e.target.value })}
                  className="w-full h-10 rounded-md border border-zinc-700 bg-black px-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-zinc-400"
                >
                  {tasks.map((task) => (
                    <option key={task.id} value={task.id}>
                      {task.name} ({task.difficulty})
                    </option>
                  ))}
                </select>
              </div>

              {/* Number of Runs */}
              <div>
                <Label htmlFor="runs" className="text-white mb-2 block">Number of Runs</Label>
                <Input
                  id="runs"
                  type="number"
                  min="1"
                  max="20"
                  value={formData.runs}
                  onChange={(e) => setFormData({ ...formData, runs: parseInt(e.target.value) })}
                  className="bg-black border-zinc-700"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Multiple runs provide reliability metrics
                </p>
              </div>

              {/* Notes */}
              <div>
                <Label htmlFor="notes" className="text-white mb-2 block">Notes (optional)</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Add any notes about this test run..."
                  className="bg-black border-zinc-700 min-h-[100px]"
                />
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-white text-black hover:bg-gray-200"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Benchmark...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Run Benchmark
                  </>
                )}
              </Button>
            </form>
          </Card>

          {/* Results Display */}
          <div className="space-y-6">
            {/* Info Card */}
            {!result && !error && (
              <Card className="bg-zinc-900 border-zinc-800 p-8">
                <h2 className="text-2xl font-semibold mb-4">How It Works</h2>
                <div className="space-y-4 text-gray-400">
                  <div className="flex items-start gap-3">
                    <div className="bg-white text-black rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-1">
                      1
                    </div>
                    <div>
                      <p className="font-medium text-white">Configure Your Model</p>
                      <p className="text-sm">Select your model provider and enter credentials</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="bg-white text-black rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-1">
                      2
                    </div>
                    <div>
                      <p className="font-medium text-white">Choose a Task</p>
                      <p className="text-sm">Select from our curated benchmark tasks</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="bg-white text-black rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-1">
                      3
                    </div>
                    <div>
                      <p className="font-medium text-white">Run the Test</p>
                      <p className="text-sm">We'll execute your model in an isolated environment</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="bg-white text-black rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 mt-1">
                      4
                    </div>
                    <div>
                      <p className="font-medium text-white">Get Results</p>
                      <p className="text-sm">View detailed metrics and compare with others</p>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Error Display */}
            {error && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Results Display */}
            {result && (
              <Card className="bg-zinc-900 border-zinc-800 p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-semibold">Results</h2>
                  {result.success ? (
                    <Badge className="bg-green-500 text-white">
                      <CheckCircle2 className="w-4 h-4 mr-1" />
                      Passed
                    </Badge>
                  ) : (
                    <Badge variant="destructive">
                      <XCircle className="w-4 h-4 mr-1" />
                      Failed
                    </Badge>
                  )}
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-black p-4 rounded-lg">
                      <div className="text-gray-400 text-sm mb-1">Duration</div>
                      <div className="text-2xl font-bold flex items-center">
                        <Clock className="w-5 h-5 mr-2" />
                        {result.duration}s
                      </div>
                    </div>

                    <div className="bg-black p-4 rounded-lg">
                      <div className="text-gray-400 text-sm mb-1">Score</div>
                      <div className="text-2xl font-bold">
                        {(result.score * 100).toFixed(1)}%
                      </div>
                    </div>

                    <div className="bg-black p-4 rounded-lg">
                      <div className="text-gray-400 text-sm mb-1">Tokens Used</div>
                      <div className="text-2xl font-bold">
                        {result.tokens_used.toLocaleString()}
                      </div>
                    </div>

                    <div className="bg-black p-4 rounded-lg">
                      <div className="text-gray-400 text-sm mb-1">Cost</div>
                      <div className="text-2xl font-bold">
                        ${result.cost}
                      </div>
                    </div>
                  </div>

                  <div className="bg-black p-4 rounded-lg">
                    <div className="text-gray-400 text-sm mb-2">Tests</div>
                    <div className="text-xl">
                      {result.tests_passed} / {result.tests_total} passed
                    </div>
                    <div className="w-full bg-zinc-800 rounded-full h-2 mt-2">
                      <div
                        className={`h-2 rounded-full ${result.success ? "bg-green-500" : "bg-red-500"}`}
                        style={{ width: `${(result.tests_passed / result.tests_total) * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="bg-black p-4 rounded-lg">
                    <div className="text-gray-400 text-sm mb-2">Run ID</div>
                    <code className="text-xs text-gray-300">{result.run_id}</code>
                  </div>

                  <Button
                    onClick={() => (window.location.href = `/runs/${result.run_id}`)}
                    className="w-full"
                    variant="outline"
                  >
                    View Detailed Results
                  </Button>
                </div>
              </Card>
            )}

            {/* Quick Stats */}
            <Card className="bg-zinc-900 border-zinc-800 p-6">
              <h3 className="text-lg font-semibold mb-4">Benchmark Statistics</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Tasks</span>
                  <span className="font-medium">{tasks.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Average Success Rate</span>
                  <span className="font-medium">74.2%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Runs</span>
                  <span className="font-medium">1,247</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Active Models</span>
                  <span className="font-medium">8</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
