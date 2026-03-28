"use client";

import { motion } from "framer-motion";

const SURVEY_FIELDS = [
  { name: "name", example: "Eduardo Gutierrez" },
  { name: "site", example: "Riverside Elementary" },
  { name: "position", example: "Teacher" },
  { name: "years_band", example: "11-20" },
  { name: "q1...q5", example: "\"Honestly, the transition...\"" },
];

const HR_FIELDS = [
  { name: "name", example: "Eduardo Gutierrez", isKey: true },
  { name: "age", example: "43", isNew: true },
  { name: "gender", example: "Male", isNew: true },
  { name: "race_ethnicity", example: "Hispanic/Latino", isNew: true },
  { name: "is_transfer", example: "false", isNew: true },
  { name: "building_wing", example: "null", isNew: true },
  { name: "room_type", example: "Standard", isNew: true },
];

interface DataJoinAnimationProps {
  joined: boolean;
}

export function DataJoinAnimation({ joined }: DataJoinAnimationProps) {
  return (
    <div className="flex items-center justify-center gap-6">
      {/* Survey table */}
      <motion.div
        animate={{ x: joined ? 60 : 0 }}
        transition={{ duration: 0.8, ease: [0.25, 0.4, 0.25, 1] }}
        className="rounded-xl border border-accent-phase2/30 bg-bg-surface"
      >
        <div className="border-b border-border-subtle px-5 py-3 text-sm font-bold text-accent-phase2">
          Survey Data
        </div>
        <div className="p-4">
          {SURVEY_FIELDS.map((f) => (
            <div key={f.name} className="flex items-center gap-4 py-1.5 text-sm">
              <span className="w-28 font-mono text-text-muted">{f.name}</span>
              <span className="text-text-secondary">{f.example}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-border-subtle px-5 py-2 text-xs text-text-muted">
          500 records · 7 fields
        </div>
      </motion.div>

      {/* Join indicator */}
      <motion.div
        animate={{ scale: joined ? 1.2 : 1, opacity: joined ? 1 : 0.5 }}
        transition={{ duration: 0.5, delay: joined ? 0.3 : 0 }}
        className="flex flex-col items-center gap-2"
      >
        <div
          className="flex h-14 w-14 items-center justify-center rounded-full text-xl font-bold"
          style={{
            backgroundColor: joined ? "rgba(245, 158, 11, 0.2)" : "rgba(42, 45, 58, 0.5)",
            color: joined ? "#f59e0b" : "#565a6e",
            border: `2px solid ${joined ? "#f59e0b" : "#2a2d3a"}`,
          }}
        >
          ⋈
        </div>
        <span className="text-xs font-medium" style={{ color: joined ? "#f59e0b" : "#565a6e" }}>
          JOIN ON
        </span>
        <code className="text-xs text-text-muted">name</code>
      </motion.div>

      {/* HR table */}
      <motion.div
        animate={{ x: joined ? -60 : 0 }}
        transition={{ duration: 0.8, ease: [0.25, 0.4, 0.25, 1] }}
        className="rounded-xl border border-accent-phase3/30 bg-bg-surface"
      >
        <div className="border-b border-border-subtle px-5 py-3 text-sm font-bold text-accent-phase3">
          HR Database
        </div>
        <div className="p-4">
          {HR_FIELDS.map((f) => (
            <div key={f.name} className="flex items-center gap-4 py-1.5 text-sm">
              <span className={`w-32 font-mono ${f.isKey ? "text-accent-phase3" : "text-text-muted"}`}>
                {f.name}
              </span>
              <span className="text-text-secondary">{f.example}</span>
              {f.isNew && joined && (
                <motion.span
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5 }}
                  className="rounded bg-accent-phase3/20 px-1.5 py-0.5 text-[10px] font-bold text-accent-phase3"
                >
                  NEW
                </motion.span>
              )}
            </div>
          ))}
        </div>
        <div className="border-t border-border-subtle px-5 py-2 text-xs text-text-muted">
          500 records · 13 fields
        </div>
      </motion.div>
    </div>
  );
}
