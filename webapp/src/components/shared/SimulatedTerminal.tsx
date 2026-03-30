"use client";

import { motion } from "framer-motion";

export interface TerminalMessage {
  type: "user" | "ai" | "system";
  content: string | string[];
}

interface SimulatedTerminalProps {
  messages: TerminalMessage[];
  title?: string;
  accentColor?: string;
}

function UserLine({ text, delay, color }: { text: string; delay: number; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.1 }}
      className="flex gap-2"
    >
      <span className="shrink-0 select-none font-bold" style={{ color }}>❯</span>
      <motion.span
        className="text-text-primary"
        initial={{ width: 0 }}
        animate={{ width: "auto" }}
        transition={{ delay: delay + 0.1, duration: 0.4 }}
      >
        {text}
      </motion.span>
    </motion.div>
  );
}

function AiResponse({ lines, delay, color }: { lines: string[]; delay: number; color: string }) {
  return (
    <div className="ml-4 mt-1 mb-3 border-l-2 pl-4" style={{ borderColor: `${color}30` }}>
      {lines.map((line, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: delay + i * 0.06, duration: 0.2 }}
          className="text-text-secondary leading-relaxed"
        >
          {line}
        </motion.div>
      ))}
    </div>
  );
}

function SystemLine({ text, delay }: { text: string; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay, duration: 0.2 }}
      className="mb-2 text-text-muted italic text-xs"
    >
      {text}
    </motion.div>
  );
}

export function SimulatedTerminal({ messages, title, accentColor = "#8b5cf6" }: SimulatedTerminalProps) {
  let cumulativeDelay = 0;

  return (
    <div className="rounded-xl border border-border-subtle bg-[#0c0e14] overflow-hidden shadow-2xl">
      {/* Title bar */}
      <div className="flex items-center gap-2 border-b border-border-subtle bg-bg-surface px-4 py-2.5">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-[#ff5f57]" />
          <div className="h-3 w-3 rounded-full bg-[#febc2e]" />
          <div className="h-3 w-3 rounded-full bg-[#28c840]" />
        </div>
        <span className="ml-2 text-xs text-text-muted font-mono">
          {title ?? "claude-code — survey-analysis"}
        </span>
      </div>

      {/* Terminal body */}
      <div className="p-5 font-mono text-[13px] leading-[1.7] max-h-[calc(100vh-280px)] overflow-y-auto">
        {messages.map((msg, i) => {
          const delay = cumulativeDelay;

          if (msg.type === "user") {
            cumulativeDelay += 0.5;
            return <UserLine key={i} text={msg.content as string} delay={delay} color={accentColor} />;
          }

          if (msg.type === "system") {
            cumulativeDelay += 0.3;
            return <SystemLine key={i} text={msg.content as string} delay={delay} />;
          }

          // AI response
          const lines = Array.isArray(msg.content) ? msg.content : [msg.content];
          cumulativeDelay += lines.length * 0.06 + 0.4;
          return <AiResponse key={i} lines={lines} delay={delay} color={accentColor} />;
        })}
      </div>
    </div>
  );
}
