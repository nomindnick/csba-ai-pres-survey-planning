"use client";

import { motion } from "framer-motion";

const STEPS = [
  { label: "Hypothesize", icon: "💡", description: "Form 3-5 testable questions", color: "#8b5cf6" },
  { label: "Investigate", icon: "🔬", description: "Parallel agents run Python scripts + read responses", color: "#06b6d4" },
  { label: "Synthesize", icon: "📝", description: "Combine findings into research memo", color: "#10b981" },
  { label: "Judge", icon: "⚖️", description: "Independent LLM scores on 6 rubric dimensions", color: "#f59e0b" },
  { label: "Iterate", icon: "🔄", description: "Judge critique drives next round's hypotheses", color: "#f43f5e" },
];

export function LoopDiagram() {
  return (
    <div className="flex flex-col items-center">
      <div className="flex items-center gap-3">
        {STEPS.map((step, i) => (
          <motion.div
            key={step.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.15, duration: 0.5 }}
            className="flex flex-col items-center"
          >
            <div
              className="flex h-20 w-20 items-center justify-center rounded-2xl border-2 text-3xl"
              style={{ borderColor: step.color, backgroundColor: `${step.color}10` }}
            >
              {step.icon}
            </div>
            <div className="mt-2 text-sm font-bold" style={{ color: step.color }}>
              {step.label}
            </div>
            <div className="mt-1 max-w-[140px] text-center text-[11px] text-text-muted leading-tight">
              {step.description}
            </div>

            {/* Arrow between steps */}
            {i < STEPS.length - 1 && (
              <motion.div
                initial={{ opacity: 0, scaleX: 0 }}
                animate={{ opacity: 1, scaleX: 1 }}
                transition={{ delay: i * 0.15 + 0.3, duration: 0.3 }}
                className="absolute"
                style={{ left: `${(i + 1) * 20}%` }}
              />
            )}
          </motion.div>
        ))}
      </div>

      {/* Arrows between items */}
      <div className="mt-4 flex items-center gap-0">
        {STEPS.map((step, i) => (
          <div key={`arrow-${i}`} className="flex items-center">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              transition={{ delay: i * 0.15 + 0.1 }}
              className="w-[140px]"
            />
            {i < STEPS.length - 1 && (
              <motion.svg
                width="40" height="20" viewBox="0 0 40 20"
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.4 }}
                transition={{ delay: i * 0.15 + 0.2 }}
                className="-mx-3 -mt-[72px]"
              >
                <path d="M5 10 L30 10 M25 5 L30 10 L25 15" stroke={STEPS[i].color} strokeWidth="2" fill="none" />
              </motion.svg>
            )}
          </div>
        ))}
      </div>

      {/* Loop-back arrow */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="mt-4 flex items-center gap-3 rounded-full border border-border-subtle bg-bg-surface px-6 py-2"
      >
        <span className="text-sm text-text-muted">Score &lt; 9.0?</span>
        <span className="text-sm font-bold text-accent-phase4">→ Next round</span>
        <span className="text-sm text-text-muted">|</span>
        <span className="text-sm text-text-muted">Score ≥ 9.0?</span>
        <span className="text-sm font-bold text-positive">→ Stop</span>
      </motion.div>
    </div>
  );
}
