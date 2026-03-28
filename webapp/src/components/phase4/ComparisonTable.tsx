"use client";

import { motion } from "framer-motion";

export function ComparisonTable() {
  const rows = [
    { label: "Rounds", manual: "6", auto: "4" },
    { label: "Final Score", manual: "8.3", auto: "9.0" },
    { label: "Approach", manual: "Guided prompting", auto: "Judge-scored loop" },
    { label: "Unique Findings", manual: "Hedging language, qualitative themes", auto: "Regression, text clustering" },
    { label: "Character", manual: "Exploratory, qualitative depth", auto: "Rigorous, quantitative precision" },
    { label: "Human Role", manual: "Coaching a researcher", auto: "Designing a meta-system" },
  ];

  return (
    <div>
      <div className="grid grid-cols-3 gap-4">
        {/* Headers */}
        <div />
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-t-xl bg-accent-primary/10 px-5 py-3 text-center text-sm font-bold text-accent-primary"
        >
          Manual Research Loop
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-t-xl bg-accent-phase4/10 px-5 py-3 text-center text-sm font-bold text-accent-phase4"
        >
          Auto-Research Loop
        </motion.div>

        {/* Rows */}
        {rows.map((row, i) => (
          <motion.div
            key={row.label}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className="contents"
          >
            <div className="flex items-center border-b border-border-subtle px-4 py-3 text-sm font-medium text-text-secondary">
              {row.label}
            </div>
            <div className="flex items-center border-b border-border-subtle bg-bg-surface/50 px-5 py-3 text-sm text-text-primary">
              {row.manual}
            </div>
            <div className="flex items-center border-b border-border-subtle bg-bg-surface/50 px-5 py-3 text-sm text-text-primary">
              {row.auto}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Bottom insight */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="mt-6 rounded-xl border border-border-subtle bg-bg-surface p-5 text-center"
      >
        <p className="text-lg font-bold text-text-primary">
          Same data. Same AI. Different design → Different insights.
        </p>
        <p className="mt-2 text-sm text-text-secondary">
          Neither found everything. Both found things the other missed.
        </p>
      </motion.div>
    </div>
  );
}
