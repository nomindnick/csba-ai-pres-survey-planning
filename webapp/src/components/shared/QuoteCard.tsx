"use client";

import { motion } from "framer-motion";

interface QuoteCardProps {
  quote: string;
  attribution: string;
  className?: string;
}

export function QuoteCard({ quote, attribution, className = "" }: QuoteCardProps) {
  return (
    <motion.blockquote
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className={`relative border-l-4 border-accent-primary py-2 pl-6 ${className}`}
    >
      <p className="text-xl italic leading-relaxed text-text-primary">
        &ldquo;{quote}&rdquo;
      </p>
      <footer className="mt-3 text-base text-text-secondary">
        &mdash; {attribution}
      </footer>
    </motion.blockquote>
  );
}
