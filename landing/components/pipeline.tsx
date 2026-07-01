"use client";
import { motion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";

const nodes = ["Task", "Runner", "Docker", "Agent", "Outputs", "Tests", "Metrics", "Dashboard"];

export function Pipeline() {
  return (
    <section className="py-18 bg-bg-void relative overflow-hidden">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
          className="text-center mb-14"
        >
          <motion.p variants={fadeUp} className="text-label-mono mb-4">How it works</motion.p>
          <motion.h2 variants={fadeUp} className="font-display text-display-l text-text-primary max-w-xl mx-auto">
            From task to insight, automatically.
          </motion.h2>
        </motion.div>

        <div className="flex flex-wrap justify-center items-center">
          {nodes.map((node, i) => (
            <div key={node} className="flex items-center">
              <motion.div
                initial={{ opacity: 0, scale: 0.7 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, type: "spring", stiffness: 200, damping: 18 }}
                className="glass-card px-4 py-2.5 text-center"
              >
                <span className="font-mono-custom text-sm text-text-primary">{node}</span>
              </motion.div>
              {i < nodes.length - 1 && (
                <motion.div
                  initial={{ scaleX: 0, opacity: 0 }}
                  whileInView={{ scaleX: 1, opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 + 0.15, duration: 0.3 }}
                  className="origin-left"
                >
                  <svg width="32" height="16" viewBox="0 0 32 16">
                    <path d="M 0 8 L 24 8 M 20 4 L 28 8 L 20 12" stroke="#252840" strokeWidth="1.5" fill="none" />
                  </svg>
                </motion.div>
              )}
            </div>
          ))}
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.8 }}
          className="text-center text-sm text-text-muted mt-8 max-w-lg mx-auto"
        >
          Every task runs in an isolated Docker container. The agent operates on the filesystem,
          outputs get evaluated by hidden tests, and metrics are stored for statistical analysis.
        </motion.p>
      </div>
    </section>
  );
}
