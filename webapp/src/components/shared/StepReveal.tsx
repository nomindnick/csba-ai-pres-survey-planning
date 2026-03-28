"use client";

import { motion, type Variants } from "framer-motion";
import { type ReactNode } from "react";

interface StepRevealProps {
  visible: boolean;
  children: ReactNode;
  direction?: "up" | "down" | "left" | "right" | "fade";
  delay?: number;
  duration?: number;
  className?: string;
}

const directionMap: Record<string, { x?: number; y?: number }> = {
  up: { y: 40 },
  down: { y: -40 },
  left: { x: 40 },
  right: { x: -40 },
  fade: {},
};

export function StepReveal({
  visible,
  children,
  direction = "up",
  delay = 0,
  duration = 0.6,
  className,
}: StepRevealProps) {
  const offset = directionMap[direction];

  const variants: Variants = {
    hidden: {
      opacity: 0,
      ...offset,
    },
    visible: {
      opacity: 1,
      x: 0,
      y: 0,
      transition: {
        duration,
        delay,
        ease: [0.25, 0.4, 0.25, 1],
      },
    },
  };

  return (
    <motion.div
      variants={variants}
      initial="hidden"
      animate={visible ? "visible" : "hidden"}
      className={className}
    >
      {children}
    </motion.div>
  );
}
