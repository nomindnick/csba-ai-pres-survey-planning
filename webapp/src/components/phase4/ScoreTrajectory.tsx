"use client";

import { motion } from "framer-motion";

interface ScorePoint {
  round: number;
  score: number;
  label: string;
}

const SCORES: ScorePoint[] = [
  { round: 1, score: 6.7, label: "Broad patterns identified" },
  { round: 2, score: 7.7, label: "Confounders tested, scorer validated" },
  { round: 3, score: 8.8, label: "Multivariate regression (R²=0.128)" },
  { round: 4, score: 9.0, label: "Text clustering + per-question analysis" },
];

const CHART_WIDTH = 700;
const CHART_HEIGHT = 300;
const PADDING = { top: 30, right: 60, bottom: 50, left: 60 };

interface ScoreTrajectoryProps {
  revealedPoints: number; // 0-4
}

export function ScoreTrajectory({ revealedPoints }: ScoreTrajectoryProps) {
  const innerW = CHART_WIDTH - PADDING.left - PADDING.right;
  const innerH = CHART_HEIGHT - PADDING.top - PADDING.bottom;

  const xScale = (round: number) => PADDING.left + ((round - 1) / 3) * innerW;
  const yScale = (score: number) => PADDING.top + innerH - ((score - 5) / 5) * innerH;

  // Build path
  const visibleScores = SCORES.slice(0, revealedPoints);
  const pathD = visibleScores
    .map((s, i) => `${i === 0 ? "M" : "L"} ${xScale(s.round)} ${yScale(s.score)}`)
    .join(" ");

  return (
    <div className="flex flex-col items-center">
      <svg width={CHART_WIDTH} height={CHART_HEIGHT} className="overflow-visible">
        {/* Grid lines */}
        {[6, 7, 8, 9, 10].map((v) => (
          <g key={v}>
            <line
              x1={PADDING.left} y1={yScale(v)}
              x2={CHART_WIDTH - PADDING.right} y2={yScale(v)}
              stroke="#2a2d3a" strokeDasharray={v === 9 ? "none" : "4 4"}
              strokeWidth={v === 9 ? 2 : 1}
            />
            <text x={PADDING.left - 12} y={yScale(v) + 4} textAnchor="end" className="fill-text-muted text-xs">
              {v}.0
            </text>
          </g>
        ))}

        {/* Threshold line label */}
        <text
          x={CHART_WIDTH - PADDING.right + 8} y={yScale(9) + 4}
          className="fill-positive text-xs font-bold"
        >
          Target
        </text>

        {/* Threshold line highlight */}
        <line
          x1={PADDING.left} y1={yScale(9)}
          x2={CHART_WIDTH - PADDING.right} y2={yScale(9)}
          stroke="#10b981" strokeWidth={2} strokeDasharray="6 4"
          opacity={0.6}
        />

        {/* Line path */}
        {revealedPoints > 0 && (
          <motion.path
            d={pathD}
            fill="none"
            stroke="#f43f5e"
            strokeWidth={3}
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          />
        )}

        {/* Data points */}
        {visibleScores.map((s, i) => (
          <motion.g
            key={s.round}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.2, duration: 0.3 }}
          >
            <circle
              cx={xScale(s.round)} cy={yScale(s.score)}
              r={8}
              fill="#f43f5e"
              stroke="#0f1117"
              strokeWidth={3}
            />
            <text
              x={xScale(s.round)} y={yScale(s.score) - 16}
              textAnchor="middle"
              className="fill-text-primary text-sm font-bold"
            >
              {s.score}
            </text>
            <text
              x={xScale(s.round)} y={CHART_HEIGHT - 10}
              textAnchor="middle"
              className="fill-text-muted text-xs"
            >
              Round {s.round}
            </text>
          </motion.g>
        ))}
      </svg>

      {/* Labels below */}
      {revealedPoints > 0 && (
        <div className="mt-4 flex gap-4">
          {visibleScores.map((s, i) => (
            <motion.div
              key={s.round}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.2 + 0.3 }}
              className="flex-1 rounded-lg border border-border-subtle bg-bg-surface px-3 py-2 text-center"
            >
              <div className="text-xs font-bold text-accent-phase4">Round {s.round}</div>
              <div className="mt-1 text-[11px] text-text-muted">{s.label}</div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
