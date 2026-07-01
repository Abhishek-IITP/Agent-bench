import { Nav } from "@/components/nav";
import { Hero } from "@/components/hero";
import { Problem } from "@/components/problem";
import { MetricsBento } from "@/components/metrics-bento";
import { Pipeline } from "@/components/pipeline";
import { Comparison } from "@/components/comparison";
import { Roadmap } from "@/components/roadmap";
import { CTA } from "@/components/cta";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <main style={{ backgroundColor: "var(--bg-void)" }}>
      <Nav />
      <Hero />
      <Problem />
      <MetricsBento />
      <Pipeline />
      <Comparison />
      <Roadmap />
      <CTA />
      <Footer />
    </main>
  );
}
