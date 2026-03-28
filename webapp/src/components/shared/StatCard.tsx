"use client";

import { motion, useSpring, useTransform, useMotionValue } from "framer-motion";
import { useEffect } from "react";

interface StatCardProps {
  value: string | number;
  label: string;
  sublabel?: string;
  color?: string;
  animate?: boolean;
}

function AnimatedNumber({ value, color }: { value: number; color?: string }) {
  const motionValue = useMotionValue(0);
  const spring = useSpring(motionValue, { stiffness: 50, damping: 20 });
  const display = useTransform(spring, (v) =>
    Number.isInteger(value) ? Math.round(v).toString() : v.toFixed(1)
  );

  useEffect(() => {
    motionValue.set(value);
  }, [value, motionValue]);

  return (
    <motion.span style={{ color }}>{display}</motion.span>
  );
}

export function StatCard({ value, label, sublabel, color, animate = true }: StatCardProps) {
  const isNumber = typeof value === "number";

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className="text-[80px] font-extrabold leading-none tracking-tight">
        {isNumber && animate ? (
          <AnimatedNumber value={value} color={color} />
        ) : (
          <span style={{ color }}>{value}</span>
        )}
      </div>
      <div className="text-2xl font-medium text-text-secondary">{label}</div>
      {sublabel && (
        <div className="text-lg text-text-muted">{sublabel}</div>
      )}
    </div>
  );
}
