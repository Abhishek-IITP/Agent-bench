"use client";
import { motion } from "framer-motion";
import { HeroDataPanel } from "@/components/landing/hero-data-panel";

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
