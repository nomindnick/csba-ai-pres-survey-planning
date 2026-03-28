"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const THUMBNAILS = Array.from({ length: 20 }, (_, i) =>
  `/pdfs/thumb_${String(i + 1).padStart(2, "0")}.png`
);

// Repeat 20 images to fill a grid of ~100
const GRID_ITEMS = Array.from({ length: 100 }, (_, i) => ({
  src: THUMBNAILS[i % 20],
  rotation: (Math.random() - 0.5) * 3,
  opacity: 0.6 + Math.random() * 0.4,
}));

export function PdfWall() {
  return (
    <div className="relative h-full w-full overflow-hidden">
      <div className="grid grid-cols-10 gap-2 p-2">
        {GRID_ITEMS.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.8, y: 30 }}
            animate={{ opacity: item.opacity, scale: 1, y: 0 }}
            transition={{
              duration: 0.3,
              delay: i * 0.008,
              ease: "easeOut",
            }}
            className="overflow-hidden rounded border border-border-subtle/50 bg-white"
            style={{ rotate: `${item.rotation}deg` }}
          >
            <Image
              src={item.src}
              alt={`Survey ${(i % 20) + 1}`}
              width={120}
              height={160}
              className="h-auto w-full"
            />
          </motion.div>
        ))}
      </div>
      {/* Gradient overlay to fade edges */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-bg-primary via-transparent to-transparent" />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-bg-primary/60 via-transparent to-transparent" />
    </div>
  );
}
