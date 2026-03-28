"use client";

import { motion } from "framer-motion";

interface BuildingMapProps {
  showNorthWing: boolean;
}

export function BuildingMap({ showNorthWing }: BuildingMapProps) {
  const wings = [
    { name: "South Wing", x: 20, y: 180, w: 200, h: 120, sentiment: 0.22, color: "#10b981" },
    { name: "East Wing", x: 240, y: 180, w: 200, h: 120, sentiment: 0.19, color: "#10b981" },
    { name: "West Wing", x: 460, y: 180, w: 200, h: 120, sentiment: 0.15, color: "#10b981" },
    { name: "Admin", x: 240, y: 320, w: 200, h: 60, sentiment: 0.31, color: "#10b981" },
    { name: "North Wing", x: 160, y: 40, w: 360, h: 120, sentiment: -0.24, color: showNorthWing ? "#f43f5e" : "#10b981" },
  ];

  return (
    <div className="flex items-start gap-8">
      {/* Building SVG */}
      <svg width={680} height={400} className="overflow-visible">
        {/* Title */}
        <text x={340} y={20} textAnchor="middle" className="fill-text-secondary text-sm font-medium">
          Hillcrest Elementary — Floor Plan
        </text>

        {wings.map((wing, i) => {
          const isNorthWing = wing.name === "North Wing";
          const fillColor = showNorthWing && isNorthWing ? "#f43f5e12" : `${wing.color}08`;
          const strokeColor = showNorthWing && isNorthWing ? "#f43f5e" : `${wing.color}40`;

          return (
            <motion.g key={wing.name}>
              <motion.rect
                x={wing.x} y={wing.y}
                width={wing.w} height={wing.h}
                rx={8}
                fill={fillColor}
                stroke={strokeColor}
                strokeWidth={showNorthWing && isNorthWing ? 3 : 1}
                initial={{ opacity: 0 }}
                animate={{
                  opacity: 1,
                  fill: fillColor,
                  stroke: strokeColor,
                }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              />
              <text
                x={wing.x + wing.w / 2}
                y={wing.y + wing.h / 2 - 8}
                textAnchor="middle"
                className="fill-text-secondary text-xs font-medium"
              >
                {wing.name}
              </text>
              <text
                x={wing.x + wing.w / 2}
                y={wing.y + wing.h / 2 + 12}
                textAnchor="middle"
                className="text-sm font-bold"
                fill={showNorthWing && isNorthWing ? "#f43f5e" : "#10b981"}
              >
                {wing.sentiment > 0 ? "+" : ""}{wing.sentiment.toFixed(2)}
              </text>

              {/* Pulsing alert on North Wing */}
              {showNorthWing && isNorthWing && (
                <motion.rect
                  x={wing.x} y={wing.y}
                  width={wing.w} height={wing.h}
                  rx={8}
                  fill="none"
                  stroke="#f43f5e"
                  strokeWidth={2}
                  initial={{ opacity: 0.8 }}
                  animate={{ opacity: [0.8, 0.2, 0.8] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </motion.g>
          );
        })}
      </svg>

      {/* Details panel */}
      {showNorthWing && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="max-w-xs space-y-4"
        >
          <div className="rounded-xl border border-negative/30 bg-negative/5 p-5">
            <div className="text-3xl font-extrabold text-negative">100%</div>
            <div className="mt-1 text-sm text-text-secondary">
              of 30 North Wing staff report audio problems
            </div>
          </div>
          <div className="space-y-2 text-sm text-text-secondary">
            <p>• Garbled sound, dead speakers, muffled audio</p>
            <p>• Cannot hear emergency announcements</p>
            <p>• Affects all positions, all tenure bands</p>
            <p>• <span className="font-bold text-text-primary">Invisible in site averages</span> — Hillcrest overall looks fine</p>
          </div>
          <div className="rounded-lg bg-bg-surface px-4 py-3 text-xs italic text-text-muted">
            &ldquo;Half the time there&rsquo;s just dead air or garbled noise.&rdquo;
            <br />— Staff member, North Wing
          </div>
          <div className="rounded-lg border border-positive/30 bg-positive/5 px-4 py-3 text-sm font-medium text-positive">
            → Facilities inspection needed
          </div>
        </motion.div>
      )}
    </div>
  );
}
