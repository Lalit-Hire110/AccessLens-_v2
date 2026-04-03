// ---------------------------------------------------------------------------
// AccessLens v2 — Utility Functions
// ---------------------------------------------------------------------------

/**
 * Categorize access gap score into three levels.
 * 
 * @param score - Access gap score (0-1 range)
 * @returns Level: "low", "moderate", or "high"
 */
export function getAccessGapLevel(
  score: number
): "low" | "moderate" | "high" {
  if (score <= 0.2) return "low";
  if (score <= 0.4) return "moderate";
  return "high";
}

/**
 * Get visual styling information for an access gap level.
 * 
 * @param level - Access gap level
 * @returns Styling object with colors, icons, and labels
 */
export function getAccessGapInfo(level: "low" | "moderate" | "high") {
  switch (level) {
    case "low":
      return {
        level: "Low Access Gap",
        color: "text-green-400",
        bgColor: "bg-green-500/10",
        borderColor: "border-green-500/30",
        icon: "✓",
      };
    case "moderate":
      return {
        level: "Moderate Access Gap",
        color: "text-yellow-400",
        bgColor: "bg-yellow-500/10",
        borderColor: "border-yellow-500/30",
        icon: "⚠",
      };
    case "high":
      return {
        level: "High Access Gap",
        color: "text-red-400",
        bgColor: "bg-red-500/10",
        borderColor: "border-red-500/30",
        icon: "⚠",
      };
  }
}

/**
 * Convert a numeric score (0-1) to a human-readable label.
 * 
 * @param score - Numeric score
 * @returns Label: "HIGH", "MEDIUM", or "LOW"
 */
export function getScoreLabel(score: number): string {
  if (score >= 0.7) return "HIGH";
  if (score >= 0.4) return "MEDIUM";
  return "LOW";
}

/**
 * Calculate the difference between two scores and format as a change indicator.
 * 
 * @param before - Original score
 * @param after - New score
 * @returns Formatted change string with arrow (e.g., "↑ 0.15" or "↓ 0.05")
 */
export function formatScoreChange(before: number, after: number): {
  value: number;
  formatted: string;
  direction: "up" | "down" | "same";
  color: string;
} {
  const diff = after - before;
  const absDiff = Math.abs(diff);
  
  if (absDiff < 0.001) {
    return {
      value: 0,
      formatted: "—",
      direction: "same",
      color: "text-gray-400",
    };
  }
  
  if (diff > 0) {
    return {
      value: diff,
      formatted: `↑ ${diff.toFixed(3)}`,
      direction: "up",
      color: "text-green-400",
    };
  }
  
  return {
    value: diff,
    formatted: `↓ ${absDiff.toFixed(3)}`,
    direction: "down",
    color: "text-red-400",
  };
}
