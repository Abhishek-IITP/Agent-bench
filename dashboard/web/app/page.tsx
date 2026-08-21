import { Nav } from "@/components/landing/nav";
import { Hero } from "@/components/landing/hero";
import { Problem } from "@/components/landing/problem";
import { MetricsBento } from "@/components/landing/metrics-bento";
import { StatsShowcase } from "@/components/landing/stats-showcase";
import { Pipeline } from "@/components/landing/pipeline";
import { Comparison } from "@/components/landing/comparison";
import { CTA } from "@/components/landing/cta";
import { Footer } from "@/components/landing/footer";

export default function Home() {
  return (
    <main style={{ backgroundColor: "#050508", color: "#ffffff", minHeight: "100vh" }}>
      <Nav />
      <Hero />
      <Problem />
      <MetricsBento />
      <StatsShowcase />
      <Pipeline />
      <Comparison />
      <CTA />
      <Footer />
    </main>
  );
}
