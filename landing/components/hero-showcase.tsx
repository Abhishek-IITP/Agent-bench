"use client";
import { motion } from "framer-motion";
import { HeroDataPanel } from "@/components/hero-data-panel";

export function HeroShowcase() {
  return (
    <section
      style={{
        position: "relative",
        padding: "0 1.5rem 8rem",
        backgroundColor: "var(--bg-void)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      {/* Centered glow behind the card */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "50%",
          transform: "translateX(-50%)",
          width: 600,
          height: 400,
          borderRadius: "50%",
          background: "radial-gradient(ellipse, rgba(74,222,128,0.08) 0%, transparent 70%)",
          filter: "blur(40px)",
          pointerEvents: "none",
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 48, scale: 0.96 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ type: "spring", stiffness: 80, damping: 20 }}
        style={{ position: "relative", zIndex: 10, width: "100%", maxWidth: 440 }}
      >
        <HeroDataPanel />
      </motion.div>
    </section>
  );
}
