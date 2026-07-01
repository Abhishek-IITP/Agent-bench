"use client";
import { motion } from "framer-motion";

const weeks = [
  {
    week: "Week 01",
    label: "Foundation",
    status: "shipped",
    items: [
      "Repository structure",
      "Task specification & schema",
      "Task loader & validator",
      "First benchmark tasks",
    ],
  },
  {
    week: "Week 02",
    label: "Execution",
    status: "upcoming",
    items: [
      "Docker runner",
      "Oracle / NOP validation",
      "CLI interface",
      "10–15 benchmark tasks",
    ],
  },
  {
    week: "Week 03",
    label: "Integration",
    status: "upcoming",
    items: [
      "AI agent integration",
      "Replay trace system",
      "PostgreSQL database",
      "REST API (Elysia)",
    ],
  },
  {
    week: "Week 04",
    label: "Analytics",
    status: "upcoming",
    items: [
      "Multi-run statistical evaluation",
      "Reliability metrics & health",
      "Dashboard",
      "Leaderboards",
    ],
  },
];

export function Roadmap() {
  return (
    <section
      id="roadmap"
      style={{
        padding: "2rem 0",
        position: "relative",
        backgroundColor: "var(--bg-void)",
        overflow: "hidden",
      }}
    >
      {/* Background subtle glow */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%,-50%)",
          width: 800,
          height: 400,
          borderRadius: "50%",
          background: "radial-gradient(ellipse, rgba(74,222,128,0.04) 0%, transparent 70%)",
          filter: "blur(40px)",
          pointerEvents: "none",
        }}
      />

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 2rem", position: "relative", zIndex: 2 }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          style={{ marginBottom: "5rem" }}
        >
          <p
            style={{
              fontFamily: "var(--font-geist-mono, monospace)",
              fontSize: "0.65rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color: "var(--text-muted)",
              marginBottom: "1rem",
            }}
          >
            Building in public
          </p>
          <h2
            style={{
              fontFamily: "var(--font-instrument-serif, Georgia, serif)",
              fontSize: "clamp(2rem, 4vw, 3.25rem)",
              lineHeight: 1.1,
              letterSpacing: "-0.02em",
              color: "var(--text-primary)",
              maxWidth: 540,
            }}
          >
            4 weeks. Every step visible.
          </h2>
        </motion.div>

        {/* Timeline — horizontal line connecting weeks */}
        <div style={{ position: "relative" }}>

          {/* Connecting line (desktop) */}
          <div
            style={{
              position: "absolute",
              top: 22,
              left: 20,
              right: 20,
              height: 1,
              background: "linear-gradient(90deg, var(--signal) 25%, var(--border-subtle) 25%)",
              display: "none", // hidden on small screens
            }}
          />

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "2rem",
            }}
          >
            {weeks.map((week, i) => (
              <motion.div
                key={week.week}
                initial={{ opacity: 0, y: 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
              >
                {/* Top indicator */}
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: "1.25rem" }}>
                  <div
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      backgroundColor: week.status === "shipped" ? "var(--signal)" : "var(--border-glow)",
                      boxShadow: week.status === "shipped" ? "0 0 12px rgba(74,222,128,0.5)" : "none",
                      flexShrink: 0,
                    }}
                  />
                  <span
                    style={{
                      fontFamily: "var(--font-geist-mono, monospace)",
                      fontSize: "0.65rem",
                      letterSpacing: "0.1em",
                      textTransform: "uppercase",
                      color: week.status === "shipped" ? "var(--signal)" : "var(--text-muted)",
                    }}
                  >
                    {week.week}
                  </span>
                  {week.status === "shipped" && (
                    <span
                      style={{
                        fontSize: "0.6rem",
                        fontFamily: "var(--font-geist-mono, monospace)",
                        letterSpacing: "0.08em",
                        textTransform: "uppercase",
                        color: "var(--signal)",
                        backgroundColor: "rgba(74,222,128,0.1)",
                        border: "1px solid rgba(74,222,128,0.2)",
                        padding: "2px 8px",
                        borderRadius: 9999,
                      }}
                    >
                      Shipped
                    </span>
                  )}
                </div>

                {/* Card */}
                <div
                  style={{
                    background: week.status === "shipped"
                      ? "rgba(74,222,128,0.04)"
                      : "rgba(15,16,24,0.5)",
                    border: `1px solid ${week.status === "shipped" ? "rgba(74,222,128,0.15)" : "var(--border-subtle)"}`,
                    borderRadius: 14,
                    padding: "1.5rem",
                    backdropFilter: "blur(8px)",
                    position: "relative",
                    overflow: "hidden",
                  }}
                >
                  {/* Shipped accent line */}
                  {week.status === "shipped" && (
                    <div
                      style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        right: 0,
                        height: 2,
                        background: "linear-gradient(90deg, var(--signal), rgba(74,222,128,0.3))",
                      }}
                    />
                  )}

                  <h3
                    style={{
                      fontFamily: "var(--font-instrument-serif, Georgia, serif)",
                      fontSize: "1.375rem",
                      color: week.status === "shipped" ? "var(--signal)" : "var(--text-primary)",
                      marginBottom: "1rem",
                      letterSpacing: "-0.01em",
                    }}
                  >
                    {week.label}
                  </h3>

                  <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 10 }}>
                    {week.items.map((item) => (
                      <li
                        key={item}
                        style={{ display: "flex", alignItems: "flex-start", gap: 10 }}
                      >
                        <span
                          style={{
                            marginTop: 5,
                            width: 5,
                            height: 5,
                            borderRadius: "50%",
                            backgroundColor: week.status === "shipped"
                              ? "var(--signal)"
                              : "var(--border-glow)",
                            flexShrink: 0,
                          }}
                        />
                        <span
                          style={{
                            fontSize: "0.875rem",
                            color: "var(--text-secondary)",
                            lineHeight: 1.5,
                          }}
                        >
                          {item}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Note */}
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          style={{
            marginTop: "3rem",
            fontSize: "0.875rem",
            color: "var(--text-muted)",
            fontFamily: "var(--font-geist-mono, monospace)",
            letterSpacing: "0.02em",
          }}
        >
          * This roadmap is public. Every shipped week updates the status above.
        </motion.p>
      </div>
    </section>
  );
}
