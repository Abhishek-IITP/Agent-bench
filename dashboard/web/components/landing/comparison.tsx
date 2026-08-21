"use client";
import { motion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";
import { Check, Minus } from "lucide-react";

const features = [
  { label: "Terminal tasks" },
  { label: "Docker isolation" },
  { label: "Oracle/NOP validation" },
  { label: "Multi-run reliability", ours: true },
  { label: "Benchmark health",      ours: true },
  { label: "Replay analytics",      ours: true },
  { label: "Cost-aware metrics",    ours: true },
  { label: "Failure taxonomy",      ours: true },
  { label: "Drift detection",       ours: true },
];

const competitors = [
  { name: "Terminal Bench", values: [true,  true,  true,  false, false, false, false, false, false] },
  { name: "SWE-bench",      values: [false, true,  "~",   false, false, false, false, false, false] },
  { name: "GAIA",           values: [false, false, false, false, false, false, false, false, false] },
  { name: "AgentBench",     values: [true,  true,  true,  true,  true,  true,  true,  true,  true], ours: true },
];

function Cell({ val, ours }: { val: boolean | string; ours?: boolean }) {
  if (val === "~") return <Minus size={14} className="mx-auto opacity-40" />;
  if (val === true)
    return <Check size={14} className={`mx-auto ${ours ? "text-signal" : "text-text-muted"}`} />;
  return <span className="block mx-auto w-4 h-px opacity-20 bg-text-muted" />;
}

export function Comparison() {
  return (
    <section id="compare" className="py-20 bg-bg-void relative">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          className="mb-14"
        >
          <motion.p variants={fadeUp} className="text-label-mono mb-4">How we compare</motion.p>
          <motion.h2 variants={fadeUp} className="font-display text-display-l text-text-primary max-w-2xl">
            Not competing on quantity. Competing on measurement quality.
          </motion.h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ type: "spring", stiffness: 80, damping: 18 }}
          className="overflow-x-auto"
        >
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="text-left pb-4 pr-6 text-label-mono w-48">Feature</th>
                {competitors.map((c) => (
                  <th
                    key={c.name}
                    className={`pb-4 px-4 text-center font-mono-custom text-xs ${c.ours ? "text-signal" : "text-text-muted"}`}
                  >
                    {c.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {features.map((feat, fi) => (
                <motion.tr
                  key={feat.label}
                  initial={{ opacity: 0, x: -16 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: fi * 0.04 }}
                  className="border-t border-border-subtle"
                >
                  <td className="py-3.5 pr-6">
                    <span className={`text-sm ${feat.ours ? "text-text-primary font-semibold" : "text-text-secondary"}`}>
                      {feat.label}
                      {feat.ours && (
                        <span className="ml-2 text-label-mono text-signal">unique</span>
                      )}
                    </span>
                  </td>
                  {competitors.map((c, ci) => (
                    <td
                      key={ci}
                      className={`py-3.5 px-4 text-center ${c.ours ? "bg-signal/5" : ""}`}
                    >
                      <Cell val={c.values[fi]} ours={c.ours} />
                    </td>
                  ))}
                </motion.tr>
              ))}
            </tbody>
          </table>
        </motion.div>

        {/* Quote */}
        <motion.blockquote
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="mt-14 max-w-3xl border-l-2 border-signal pl-6"
        >
          <p className="font-display text-xl text-text-primary mb-3">
            &ldquo;AgentBench is a reliability-first AI agent benchmark. Instead of measuring whether
            an agent can solve a task once, it measures how consistently, reproducibly, and
            efficiently it solves the task across repeated runs — while continuously evaluating
            the health of the benchmark itself.&rdquo;
          </p>
          <p className="text-sm text-text-muted">
            Not trying to have more tasks than Terminal Bench or more bugs than SWE-bench.
            Trying to have better measurements.
          </p>
        </motion.blockquote>
      </div>
    </section>
  );
}
