"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { fadeUp, staggerContainer } from "@/lib/motion";

export function CTA() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const formspreeUrl = process.env.NEXT_PUBLIC_FORMSPREE_URL;

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email) return;
    if (!formspreeUrl) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(formspreeUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (response.ok) {
        setSubmitted(true);
      }
    } catch {
      // Keep the form visible if submission fails.
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="waitlist" className="py-14 bg-bg-void relative overflow-hidden">
      {/* Glow */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-96 w-96 rounded-full pointer-events-none opacity-30 bg-[radial-gradient(circle,rgba(74,222,128,0.2),transparent_70%)] blur-[60px]"
      />

      <div className="max-w-2xl mx-auto px-6 text-center relative z-10">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
        >
          <motion.p variants={fadeUp} className="text-label-mono mb-6">
            Stay in the loop
          </motion.p>

          <motion.h2 variants={fadeUp} className="font-display text-display-l text-text-primary mb-6">
            Benchmarks should earn your trust.
          </motion.h2>

          <motion.p variants={fadeUp} className="text-text-secondary mb-10">
            Follow the build. Get notified when AgentBench ships.
          </motion.p>

          {submitted ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card p-8 text-center"
            >
              <span className="text-3xl block mb-3">✓</span>
              <p className="font-display text-xl text-text-primary">You&apos;re on the list.</p>
              <p className="text-sm text-text-secondary mt-2">
                I&apos;ll email you when something ships.
              </p>
            </motion.div>
          ) : (
            <motion.form
              variants={fadeUp}
              onSubmit={handleSubmit}
              className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto"
            >
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="flex-1 px-4 py-3 rounded-lg text-sm font-mono-custom outline-none bg-bg-elevated border border-border-subtle text-text-primary focus:border-signal transition-colors"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 rounded-lg font-semibold text-sm bg-signal text-bg-void shrink-0 hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                {loading ? "..." : "Follow the build"}
              </button>
            </motion.form>
          )}
        </motion.div>
      </div>
    </section>
  );
}
