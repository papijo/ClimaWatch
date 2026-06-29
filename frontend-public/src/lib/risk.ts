export const RISK_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  LOW: { bg: "bg-risk-low-bg", text: "text-risk-low", border: "border-risk-low" },
  MODERATE: { bg: "bg-risk-moderate-bg", text: "text-risk-moderate", border: "border-risk-moderate" },
  HIGH: { bg: "bg-risk-high-bg", text: "text-risk-high", border: "border-risk-high" },
  CRITICAL: { bg: "bg-risk-critical-bg", text: "text-risk-critical", border: "border-risk-critical" },
};

export const RISK_HEX: Record<string, string> = {
  LOW: "#22c55e",
  MODERATE: "#eab308",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
};

export function riskClasses(level: string) {
  return RISK_COLORS[level] ?? RISK_COLORS.LOW;
}
