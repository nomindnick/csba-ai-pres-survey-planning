"use client";

import { motion, AnimatePresence } from "framer-motion";

interface SimpsonParadoxProps {
  stage: "aggregate" | "split";
}

const AGGREGATE = [
  { label: "Female", value: 0.158, color: "#8b5cf6" },
  { label: "Male", value: 0.143, color: "#06b6d4" },
];

const BY_SITE = [
  {
    site: "Riverside Elementary",
    female: 0.183,
    male: 0.253,
    maleColor: "#10b981",
  },
  {
    site: "Hillcrest Elementary",
    female: 0.171,
    male: 0.160,
    maleColor: "#f59e0b",
  },
  {
    site: "Valley High",
    female: 0.130,
    male: -0.154,
    maleColor: "#f43f5e",
  },
];

function Bar({
  value,
  color,
  maxVal,
  delay,
  height = 48,
}: {
  value: number;
  color: string;
  maxVal: number;
  delay: number;
  height?: number;
}) {
  const width = (Math.abs(value) / maxVal) * 100;
  return (
    <div className="relative overflow-hidden rounded-lg bg-bg-surface" style={{ height }}>
      <motion.div
        className="absolute inset-y-0 left-0 rounded-lg flex items-center px-4"
        style={{ backgroundColor: `${color}18` }}
        initial={{ width: 0 }}
        animate={{ width: `${Math.max(width, 8)}%` }}
        transition={{ duration: 0.7, delay, ease: "easeOut" }}
      >
        <span className="text-lg font-extrabold whitespace-nowrap" style={{ color }}>
          {value >= 0 ? "+" : ""}{value.toFixed(3)}
        </span>
      </motion.div>
    </div>
  );
}

export function SimpsonParadox({ stage }: SimpsonParadoxProps) {
  return (
    <div className="flex flex-col items-center">
      <AnimatePresence mode="wait">
        {stage === "aggregate" && (
          <motion.div
            key="aggregate"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full max-w-2xl"
          >
            <div className="mb-8 text-center">
              <h3 className="text-2xl font-bold text-text-primary">
                Gender &amp; Sentiment — Overall
              </h3>
              <p className="mt-2 text-lg text-text-secondary">
                Looks like gender doesn&rsquo;t matter much.
              </p>
            </div>

            <div className="space-y-6">
              {AGGREGATE.map((d, i) => (
                <div key={d.label}>
                  <div className="mb-2 flex items-baseline justify-between">
                    <span className="text-lg font-medium" style={{ color: d.color }}>{d.label}</span>
                    <span className="text-sm text-text-muted">Difference: 0.015</span>
                  </div>
                  <Bar value={d.value} color={d.color} maxVal={0.35} delay={i * 0.2} />
                </div>
              ))}
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mt-8 text-center"
            >
              <span className="rounded-full bg-bg-surface px-6 py-2 text-sm text-text-muted">
                Correlation ≈ 0 — gender appears irrelevant
              </span>
            </motion.div>
          </motion.div>
        )}

        {stage === "split" && (
          <motion.div
            key="split"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full max-w-3xl"
          >
            <div className="mb-6 text-center">
              <h3 className="text-2xl font-bold text-text-primary">
                But split by site...
              </h3>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-2 text-lg text-accent-phase4 font-medium"
              >
                The aggregate was hiding opposite effects.
              </motion.p>
            </div>

            <div className="space-y-8">
              {BY_SITE.map((site, si) => (
                <motion.div
                  key={site.site}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: si * 0.2 }}
                >
                  <div className="mb-3 text-sm font-medium text-text-secondary">{site.site}</div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="mb-1 text-xs text-text-muted flex items-center gap-2">
                        <span className="inline-block h-2 w-2 rounded-full bg-[#8b5cf6]" />
                        Female
                      </div>
                      <Bar value={site.female} color="#8b5cf6" maxVal={0.35} delay={si * 0.2 + 0.1} height={40} />
                    </div>
                    <div>
                      <div className="mb-1 text-xs text-text-muted flex items-center gap-2">
                        <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: site.maleColor }} />
                        Male
                      </div>
                      <Bar value={site.male} color={site.maleColor} maxVal={0.35} delay={si * 0.2 + 0.2} height={40} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* The "whoa" callout */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.2, duration: 0.5 }}
              className="mt-8 rounded-xl border border-accent-phase4/30 bg-accent-phase4/5 p-5 text-center"
            >
              <p className="text-lg font-bold text-text-primary">
                Males <span className="text-positive">+0.253</span> at Riverside but{" "}
                <span className="text-negative">-0.154</span> at Valley High
              </p>
              <p className="mt-2 text-sm text-text-secondary">
                A 0.407-point swing in the same variable. The aggregate zero was{" "}
                <span className="font-bold text-accent-phase4">masking opposite effects</span>.
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
