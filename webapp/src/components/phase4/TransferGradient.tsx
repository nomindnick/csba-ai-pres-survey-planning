"use client";

import { motion } from "framer-motion";

const TRANSFER_DATA = [
  { label: "From worse system", value: 0.582, positive: "87%", negative: "0%", n: 30, color: "#10b981" },
  { label: "From comparable", value: 0.215, positive: "42%", negative: "17%", n: 12, color: "#f59e0b" },
  { label: "From better system", value: 0.102, positive: "35%", negative: "39%", n: 26, color: "#f43f5e" },
];

export function TransferGradient() {
  return (
    <div className="flex items-start gap-8">
      <div className="flex-1">
        <div className="space-y-6">
          {TRANSFER_DATA.map((d, i) => (
            <motion.div
              key={d.label}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.2, duration: 0.5 }}
            >
              <div className="flex items-baseline justify-between">
                <span className="text-lg font-medium text-text-primary">{d.label}</span>
                <span className="text-sm text-text-muted">n={d.n}</span>
              </div>

              {/* Bar */}
              <div className="mt-2 h-12 rounded-lg bg-bg-surface overflow-hidden relative">
                <motion.div
                  className="absolute inset-y-0 left-0 rounded-lg flex items-center px-4"
                  style={{ backgroundColor: `${d.color}20` }}
                  initial={{ width: 0 }}
                  animate={{ width: `${(d.value / 0.65) * 100}%` }}
                  transition={{ duration: 0.8, delay: i * 0.2 + 0.2, ease: "easeOut" }}
                >
                  <span className="text-2xl font-extrabold" style={{ color: d.color }}>
                    +{d.value.toFixed(3)}
                  </span>
                </motion.div>
              </div>

              {/* Stats below */}
              <div className="mt-1 flex gap-4 text-xs">
                <span className="text-positive">{d.positive} positive</span>
                <span className="text-negative">{d.negative} negative</span>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Gap annotation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-6 flex items-center gap-3"
        >
          <div className="h-px flex-1 bg-border-subtle" />
          <span className="text-sm font-bold text-accent-phase4">0.48-point gap</span>
          <div className="h-px flex-1 bg-border-subtle" />
        </motion.div>
      </div>

      {/* Insight panel */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.8 }}
        className="w-72 space-y-4"
      >
        <div className="rounded-xl border border-border-subtle bg-bg-surface p-5">
          <h4 className="text-lg font-bold text-accent-phase4">The Reference-Point Effect</h4>
          <p className="mt-2 text-sm leading-relaxed text-text-secondary">
            Same system. Opposite reactions. Satisfaction reflects what people are{" "}
            <em>comparing against</em>, not the system itself.
          </p>
        </div>
        <div className="rounded-lg bg-bg-surface px-4 py-3 text-xs italic text-text-muted">
          &ldquo;Coming from a district where the communications setup was really outdated, I appreciate how much more capable this one is.&rdquo;
          <br />— Transfer from worse system
        </div>
        <div className="rounded-lg bg-bg-surface px-4 py-3 text-xs italic text-text-muted">
          &ldquo;At my last district everything just worked. This takes more fiddling.&rdquo;
          <br />— Transfer from better system
        </div>
      </motion.div>
    </div>
  );
}
