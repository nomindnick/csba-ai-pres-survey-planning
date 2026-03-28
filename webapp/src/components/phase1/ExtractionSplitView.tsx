"use client";

import { motion } from "framer-motion";

const PROMPT_TEXT = `Extract the following fields from this survey PDF as JSON:

{
  "name": "respondent's full name",
  "site": "school site name",
  "position": "job title",
  "years_at_district_band": "tenure band",
  "years_in_profession_band": "career band",
  "q1": "full response to question 1",
  "q2": "full response to question 2",
  "q3": "full response to question 3",
  "q4": "full response to question 4",
  "q5": "full response to question 5"
}`;

const JSON_OUTPUT = `{
  "name": "Eduardo Gutierrez",
  "site": "Riverside Elementary",
  "position": "Teacher",
  "years_at_district_band": "11-20",
  "years_in_profession_band": "16-25",
  "q1": "Honestly, the transition has been
    smoother than I expected...",
  "q2": "The training was okay. It covered
    the basics...",
  "q3": "Communication was decent but not
    great...",
  "q4": "The workflow for making announcements
    is genuinely improved...",
  "q5": "The system glitches occasionally..."
}`;

interface FieldHighlight {
  field: string;
  color: string;
}

const FIELD_HIGHLIGHTS: FieldHighlight[] = [
  { field: "name", color: "#06b6d4" },
  { field: "site", color: "#8b5cf6" },
  { field: "position", color: "#f59e0b" },
  { field: "q1", color: "#f43f5e" },
  { field: "q2", color: "#10b981" },
];

interface ExtractionSplitViewProps {
  showConnectors: boolean;
}

export function ExtractionSplitView({ showConnectors }: ExtractionSplitViewProps) {
  const highlightJson = (text: string) => {
    const lines = text.split("\n");
    return lines.map((line, i) => {
      const highlight = FIELD_HIGHLIGHTS.find((h) =>
        line.trim().startsWith(`"${h.field}"`)
      );
      return (
        <div
          key={i}
          className={`transition-all duration-500 ${
            showConnectors && highlight
              ? "rounded px-2 -mx-2"
              : ""
          }`}
          style={
            showConnectors && highlight
              ? { backgroundColor: `${highlight.color}15`, borderLeft: `2px solid ${highlight.color}` }
              : undefined
          }
        >
          {line || "\u00A0"}
        </div>
      );
    });
  };

  return (
    <div className="flex items-stretch gap-4">
      {/* API Prompt */}
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="flex-1 rounded-xl border border-border-subtle bg-bg-surface"
      >
        <div className="border-b border-border-subtle px-5 py-3 text-sm font-medium text-accent-phase1">
          API Prompt
        </div>
        <pre className="p-5 text-[13px] leading-relaxed text-text-secondary font-mono whitespace-pre-wrap">
          {PROMPT_TEXT}
        </pre>
      </motion.div>

      {/* Arrow */}
      <div className="flex flex-col items-center justify-center gap-2">
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.3 }}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-accent-phase1/20 text-accent-phase1"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </motion.div>
        <span className="text-xs text-text-muted">Claude API</span>
      </div>

      {/* JSON Output */}
      <motion.div
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="flex-1 rounded-xl border border-border-subtle bg-bg-surface"
      >
        <div className="border-b border-border-subtle px-5 py-3 text-sm font-medium text-positive">
          Structured Output
        </div>
        <pre className="p-5 text-[13px] leading-relaxed text-text-secondary font-mono whitespace-pre-wrap">
          {highlightJson(JSON_OUTPUT)}
        </pre>
      </motion.div>
    </div>
  );
}
