"use client";

import { motion } from "framer-motion";

// Horizontal bar chart component for the presentation
interface BarDatum {
  label: string;
  value: number;
  n: number;
  color?: string;
}

interface HBarChartProps {
  data: BarDatum[];
  title: string;
  subtitle?: string;
  maxValue?: number;
  showLabels?: boolean;
}

function sentimentColor(value: number) {
  if (value > 0.15) return "#10b981";
  if (value < -0.01) return "#f43f5e";
  return "#f59e0b";
}

export function HBarChart({ data, title, subtitle, maxValue, showLabels = true }: HBarChartProps) {
  const max = maxValue ?? Math.max(...data.map((d) => Math.abs(d.value))) * 1.3;

  return (
    <div>
      <h3 className="text-xl font-bold text-text-primary">{title}</h3>
      {subtitle && <p className="mt-1 text-sm text-text-secondary">{subtitle}</p>}
      <div className="mt-6 space-y-4">
        {data.map((d, i) => {
          const color = d.color ?? sentimentColor(d.value);
          const width = Math.abs(d.value) / max * 100;
          const isNegative = d.value < 0;

          return (
            <motion.div
              key={d.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="flex items-center gap-4"
            >
              <span className="w-40 text-right text-sm font-medium text-text-secondary shrink-0">
                {d.label}
              </span>
              <div className="flex-1 flex items-center gap-3">
                <div className="flex-1 h-8 rounded bg-bg-surface relative overflow-hidden">
                  <motion.div
                    className="absolute top-0 left-0 h-full rounded"
                    style={{ backgroundColor: color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${width}%` }}
                    transition={{ duration: 0.6, delay: i * 0.08 + 0.2, ease: "easeOut" }}
                  />
                </div>
                {showLabels && (
                  <span className="w-16 text-sm font-bold shrink-0" style={{ color }}>
                    {isNegative ? "" : "+"}{d.value.toFixed(3)}
                  </span>
                )}
                <span className="w-14 text-xs text-text-muted shrink-0">n={d.n}</span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

// Pre-built chart configs
export const SITE_DATA: BarDatum[] = [
  { label: "Riverside Elementary", value: 0.201, n: 164 },
  { label: "Hillcrest Elementary", value: 0.166, n: 140 },
  { label: "Valley High", value: 0.095, n: 196 },
];

export const TENURE_DATA: BarDatum[] = [
  { label: "0-3 years", value: 0.306, n: 108 },
  { label: "4-10 years", value: 0.194, n: 184 },
  { label: "11-20 years", value: 0.108, n: 132 },
  { label: "20+ years", value: -0.113, n: 76 },
];

export const POSITION_DATA: BarDatum[] = [
  { label: "District Office", value: 0.418, n: 12 },
  { label: "Counselors", value: 0.326, n: 18 },
  { label: "Site Admins", value: 0.258, n: 20 },
  { label: "Teachers", value: 0.152, n: 310 },
  { label: "Paraprofessionals", value: 0.121, n: 52 },
  { label: "Custodial", value: 0.089, n: 44 },
  { label: "Food Service", value: -0.032, n: 44 },
];

export const FOOD_SERVICE_BY_SITE: BarDatum[] = [
  { label: "Riverside", value: 0.025, n: 14 },
  { label: "Hillcrest", value: -0.015, n: 14 },
  { label: "Valley High", value: -0.107, n: 16 },
];

export const COUNSELOR_SPLIT = [
  { category: "System Reliability", value: 0.62, color: "#10b981" },
  { category: "Safety Features", value: 0.78, color: "#10b981" },
  { category: "Workflow Impact", value: -0.15, color: "#f43f5e" },
  { category: "Confidentiality", value: -0.31, color: "#f43f5e" },
];

export function CounselorSplitChart() {
  return (
    <div>
      <h3 className="text-xl font-bold text-text-primary">Counselors: A Split Story</h3>
      <p className="mt-1 text-sm text-text-secondary">
        High marks for safety — but intercom interrupts sensitive student sessions
      </p>
      <div className="mt-6 grid grid-cols-2 gap-6">
        {/* Positive side */}
        <div className="rounded-xl border border-positive/20 bg-positive/5 p-5">
          <div className="mb-3 text-sm font-bold text-positive">What They Love</div>
          {COUNSELOR_SPLIT.filter(c => c.value > 0).map((c, i) => (
            <motion.div
              key={c.category}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15 }}
              className="mt-3"
            >
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">{c.category}</span>
                <span className="font-bold text-positive">+{c.value.toFixed(2)}</span>
              </div>
              <div className="mt-1 h-2 rounded-full bg-bg-surface overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-positive"
                  initial={{ width: 0 }}
                  animate={{ width: `${c.value * 100}%` }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                />
              </div>
            </motion.div>
          ))}
        </div>
        {/* Negative side */}
        <div className="rounded-xl border border-negative/20 bg-negative/5 p-5">
          <div className="mb-3 text-sm font-bold text-negative">What Concerns Them</div>
          {COUNSELOR_SPLIT.filter(c => c.value < 0).map((c, i) => (
            <motion.div
              key={c.category}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15 }}
              className="mt-3"
            >
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">{c.category}</span>
                <span className="font-bold text-negative">{c.value.toFixed(2)}</span>
              </div>
              <div className="mt-1 h-2 rounded-full bg-bg-surface overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-negative"
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.abs(c.value) * 100}%` }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                />
              </div>
            </motion.div>
          ))}
          <p className="mt-4 text-xs italic text-text-muted">
            &ldquo;I&rsquo;ve had students completely shut down after an interruption.&rdquo;
          </p>
        </div>
      </div>
    </div>
  );
}
