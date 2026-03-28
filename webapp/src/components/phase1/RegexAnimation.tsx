"use client";

import { motion, AnimatePresence } from "framer-motion";

interface RegexField {
  label: string;
  pattern: string;
  color: string;
  startIndex: number;
  endIndex: number;
}

const SURVEY_TEXT = `Tri-Valley Unified School District
Staff Communications System Survey

Name: Eduardo Gutierrez
Site: Riverside Elementary
Position: Teacher
Years at District: 11-20
Years in Profession: 16-25

Q1: Overall, how has the new communications system affected your daily work experience?
Honestly, the transition has been smoother than I expected. The new system hasn't really disrupted my routines much — if anything, the intercom is a little easier to use than the old one.

Q2: How would you rate the training you received?
The training was okay. It covered the basics, but I felt like it moved fast and didn't leave much room for questions.

Q3: How well was the change communicated to you?
Communication was decent but not great. I heard about the change at a staff meeting, and then there were a couple of emails.`;

const REGEX_FIELDS: RegexField[] = [
  { label: "name", pattern: "Name: (.+)", color: "#06b6d4", startIndex: 100, endIndex: 119 },
  { label: "site", pattern: "Site: (.+)", color: "#8b5cf6", startIndex: 120, endIndex: 143 },
  { label: "position", pattern: "Position: (.+)", color: "#f59e0b", startIndex: 144, endIndex: 162 },
  { label: "years_district", pattern: "Years at District: (.+)", color: "#10b981", startIndex: 163, endIndex: 186 },
  { label: "q1_response", pattern: "Q1: .+\\n(.+)", color: "#f43f5e", startIndex: 268, endIndex: 434 },
];

interface RegexAnimationProps {
  activeField: number; // -1 = none, 0-4 = highlighting that field
  showFailure?: boolean;
}

export function RegexAnimation({ activeField, showFailure = false }: RegexAnimationProps) {
  const lines = SURVEY_TEXT.split("\n");

  return (
    <div className="flex gap-6">
      {/* Text panel */}
      <div className="flex-1 rounded-xl border border-border-subtle bg-bg-surface p-6 font-mono text-sm leading-relaxed">
        <div className="mb-3 text-xs font-medium text-text-muted">
          {showFailure ? "survey_005.pdf (handwriting font)" : "survey_001.pdf (extracted text)"}
        </div>
        {lines.map((line, i) => {
          // Check if this line contains any part of the active field
          const field = activeField >= 0 ? REGEX_FIELDS[activeField] : null;
          const lineStart = SURVEY_TEXT.indexOf(line);
          const lineEnd = lineStart + line.length;
          const isHighlighted =
            field &&
            !showFailure &&
            lineStart < field.endIndex &&
            lineEnd > field.startIndex;

          return (
            <div
              key={i}
              className={`transition-all duration-300 ${
                isHighlighted
                  ? "rounded px-2 -mx-2"
                  : activeField >= 0
                  ? "opacity-40"
                  : ""
              }`}
              style={
                isHighlighted
                  ? { backgroundColor: `${field!.color}15`, borderLeft: `2px solid ${field!.color}` }
                  : undefined
              }
            >
              {line || "\u00A0"}
            </div>
          );
        })}
        {showFailure && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 rounded-lg bg-negative/10 border border-negative/30 px-4 py-3 text-negative text-xs"
          >
            ⚠ Regex failed: &quot;Name:&quot; pattern not found — handwriting font uses inconsistent spacing
          </motion.div>
        )}
      </div>

      {/* Regex patterns panel */}
      <div className="w-72 space-y-2">
        <div className="mb-3 text-xs font-medium text-text-muted">Regex Patterns</div>
        <AnimatePresence>
          {REGEX_FIELDS.map((field, i) => (
            <motion.div
              key={field.label}
              initial={{ opacity: 0, x: 20 }}
              animate={{
                opacity: i <= activeField ? 1 : 0.3,
                x: 0,
                scale: i === activeField ? 1.02 : 1,
              }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className="rounded-lg border border-border-subtle bg-bg-surface px-4 py-3"
              style={
                i === activeField && !showFailure
                  ? { borderColor: field.color, boxShadow: `0 0 12px ${field.color}20` }
                  : undefined
              }
            >
              <div className="text-xs font-medium" style={{ color: field.color }}>
                {field.label}
              </div>
              <code className="mt-1 block text-xs text-text-muted">{field.pattern}</code>
              {i === activeField && showFailure && (
                <div className="mt-1 text-xs text-negative">✗ No match</div>
              )}
              {i === activeField && !showFailure && (
                <div className="mt-1 text-xs text-positive">✓ Match found</div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
