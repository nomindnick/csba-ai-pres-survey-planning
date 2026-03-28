"use client";

import { motion } from "framer-motion";

interface ThemeNode {
  name: string;
  count: number;
  color: string;
  children?: { name: string; count: number }[];
}

const TAXONOMY: ThemeNode[] = [
  {
    name: "System Quality",
    count: 342,
    color: "#10b981",
    children: [
      { name: "Audio Clarity", count: 156 },
      { name: "Reliability", count: 98 },
      { name: "Interface/Usability", count: 88 },
    ],
  },
  {
    name: "Communication",
    count: 298,
    color: "#f43f5e",
    children: [
      { name: "Timeline Gaps", count: 134 },
      { name: "Lack of Consultation", count: 89 },
      { name: "Information Flow", count: 75 },
    ],
  },
  {
    name: "Training",
    count: 245,
    color: "#8b5cf6",
    children: [
      { name: "Pace/Coverage", count: 112 },
      { name: "Follow-up Needed", count: 78 },
      { name: "Hands-on vs Demo", count: 55 },
    ],
  },
  {
    name: "Workflow Impact",
    count: 218,
    color: "#f59e0b",
    children: [
      { name: "Daily Routines", count: 95 },
      { name: "Bell Schedule", count: 67 },
      { name: "Classroom Disruption", count: 56 },
    ],
  },
  {
    name: "Change Management",
    count: 187,
    color: "#06b6d4",
    children: [
      { name: "Process Concerns", count: 92 },
      { name: "Respect/Consultation", count: 58 },
      { name: "Prior Experience", count: 37 },
    ],
  },
];

interface TaxonomyTreeProps {
  revealLevel: number; // 0 = nothing, 1 = top-level only, 2 = with children
}

export function TaxonomyTree({ revealLevel }: TaxonomyTreeProps) {
  return (
    <div className="flex h-full items-start justify-center gap-5">
      {TAXONOMY.map((theme, i) => (
        <motion.div
          key={theme.name}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: revealLevel >= 1 ? 1 : 0, y: revealLevel >= 1 ? 0 : 30 }}
          transition={{ duration: 0.5, delay: i * 0.1 }}
          className="flex-1"
        >
          {/* Top-level theme */}
          <div
            className="rounded-xl border px-4 py-4 text-center"
            style={{ borderColor: `${theme.color}40`, backgroundColor: `${theme.color}08` }}
          >
            <div className="text-sm font-bold" style={{ color: theme.color }}>
              {theme.name}
            </div>
            <div className="mt-1 text-2xl font-extrabold text-text-primary">
              {theme.count}
            </div>
            <div className="text-xs text-text-muted">mentions</div>
          </div>

          {/* Children */}
          {theme.children && (
            <div className="mt-2 space-y-1.5">
              {theme.children.map((child, j) => (
                <motion.div
                  key={child.name}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{
                    opacity: revealLevel >= 2 ? 1 : 0,
                    x: revealLevel >= 2 ? 0 : -10,
                  }}
                  transition={{ duration: 0.3, delay: i * 0.1 + j * 0.08 + 0.3 }}
                  className="flex items-center justify-between rounded-lg border border-border-subtle bg-bg-surface px-3 py-2"
                >
                  <span className="text-xs text-text-secondary">{child.name}</span>
                  <span className="text-xs font-bold" style={{ color: theme.color }}>
                    {child.count}
                  </span>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
}
