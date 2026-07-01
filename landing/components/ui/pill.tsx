import { cn } from "@/lib/utils";

type PillVariant = "healthy" | "flaky" | "broken" | "saturated" | "trivial";

interface PillProps {
  variant: PillVariant;
  children: React.ReactNode;
  className?: string;
}

export function Pill({ variant, children, className }: PillProps) {
  return (
    <span className={cn(`pill pill-${variant}`, className)}>
      <span
        className="w-1.5 h-1.5 rounded-full inline-block"
        style={{
          backgroundColor:
            variant === "healthy"   ? "var(--status-healthy)"   :
            variant === "flaky"     ? "var(--status-flaky)"     :
            variant === "broken"    ? "var(--status-broken)"    :
            variant === "saturated" ? "var(--status-saturated)" :
                                      "var(--status-trivial)",
        }}
      />
      {children}
    </span>
  );
}
