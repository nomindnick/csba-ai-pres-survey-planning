"use client";

import { motion } from "framer-motion";

interface PhaseTitleProps {
  phaseNumber: number;
  title: string;
  subtitle: string;
  accentColor: string;
}

export function PhaseTitle({ phaseNumber, title, subtitle, accentColor }: PhaseTitleProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: [0.25, 0.4, 0.25, 1] }}
        className="text-center"
      >
        <div
          className="mb-4 text-[120px] font-extrabold leading-none"
          style={{ color: accentColor, opacity: 0.15 }}
        >
          {phaseNumber}
        </div>
        <h1
          className="-mt-16 text-[56px] font-bold tracking-tight"
          style={{ color: accentColor }}
        >
          {title}
        </h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-4 text-2xl text-text-secondary"
        >
          {subtitle}
        </motion.p>
      </motion.div>
    </div>
  );
}
