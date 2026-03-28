"use client";

import { motion } from "framer-motion";

// Real survey responses from the corpus
const RESPONSES = [
  { id: 1, name: "Eduardo G.", q: "Q1", text: "Honestly, the transition has been smoother than I expected. The new system hasn't really disrupted my routines much." },
  { id: 2, name: "Rachel B.", q: "Q3", text: "I was pretty blindsided by the whole thing. I found out about the installation timeline from another teacher, not from admin." },
  { id: 3, name: "Megan M.", q: "Q5", text: "I don't think we needed a new system. The old one worked fine for what we needed." },
  { id: 5, name: "Noelle K.", q: "Q4", text: "The audio quality is miles ahead of what I'm used to. At my previous district we didn't even have speakers in every room." },
  { id: 4, name: "Andrea L.", q: "Q2", text: "The training felt a little rushed. I picked up the basics but I know there are features I'm not using." },
  { id: 6, name: "Vinh W.", q: "Q1", text: "It hasn't changed things much for me. I use the intercom for the same purposes I always have." },
  { id: 7, name: "Carlos R.", q: "Q5", text: "The whole rollout felt rushed and poorly communicated. I would have appreciated being consulted." },
  { id: 8, name: "Diana T.", q: "Q4", text: "The workflow for making announcements from my classroom is genuinely improved. The interface is more intuitive." },
  { id: 9, name: "James P.", q: "Q3", text: "We were told it was coming, but the specifics trickled in slowly. Nobody had a firm answer." },
  { id: 10, name: "Maria S.", q: "Q2", text: "Training was solid. I came in with pretty low expectations and was pleasantly surprised." },
  { id: 11, name: "Kevin H.", q: "Q1", text: "It's been a disruption, honestly. Everything takes a few extra steps now." },
  { id: 12, name: "Linda F.", q: "Q5", text: "The bell schedule kept changing during the install and it threw off our whole lunch service." },
  { id: 13, name: "Paul M.", q: "Q4", text: "The speakers are noticeably clearer than the old ones. Genuine improvement." },
  { id: 14, name: "Sarah W.", q: "Q3", text: "I felt well-informed about the change. We got emails, it was discussed at staff meetings." },
  { id: 15, name: "Robert J.", q: "Q1", text: "The system glitches occasionally — I've had it cut out mid-announcement twice since we started." },
  { id: 16, name: "Chen L.", q: "Q2", text: "Training was adequate. I've been through enough of these system changes over the years." },
];

interface ResponseStreamProps {
  showSentiment: boolean;
}

function getSentiment(text: string): "positive" | "negative" | "neutral" {
  const negWords = ["blindsided", "rushed", "disruption", "don't think", "poorly", "threw off", "glitches"];
  const posWords = ["smoother", "miles ahead", "improved", "solid", "pleasantly", "clearer", "well-informed", "genuinely"];
  const hasNeg = negWords.some((w) => text.toLowerCase().includes(w));
  const hasPos = posWords.some((w) => text.toLowerCase().includes(w));
  if (hasNeg && !hasPos) return "negative";
  if (hasPos && !hasNeg) return "positive";
  return "neutral";
}

const sentimentColors = {
  positive: { bg: "rgba(16, 185, 129, 0.08)", border: "rgba(16, 185, 129, 0.3)", text: "#10b981" },
  negative: { bg: "rgba(244, 63, 94, 0.08)", border: "rgba(244, 63, 94, 0.3)", text: "#f43f5e" },
  neutral: { bg: "rgba(245, 158, 11, 0.08)", border: "rgba(245, 158, 11, 0.3)", text: "#f59e0b" },
};

export function ResponseStream({ showSentiment }: ResponseStreamProps) {
  return (
    <div className="grid grid-cols-2 gap-3 overflow-hidden" style={{ maxHeight: "calc(100vh - 220px)" }}>
      {RESPONSES.map((r, i) => {
        const sentiment = getSentiment(r.text);
        const colors = sentimentColors[sentiment];

        return (
          <motion.div
            key={r.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.03 }}
            className="rounded-lg border px-4 py-3 transition-all duration-700"
            style={
              showSentiment
                ? { backgroundColor: colors.bg, borderColor: colors.border }
                : { backgroundColor: "rgba(26, 29, 39, 0.8)", borderColor: "#2a2d3a" }
            }
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-text-muted">
                {r.name} — {r.q}
              </span>
              {showSentiment && (
                <motion.span
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 + i * 0.04 }}
                  className="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase"
                  style={{ backgroundColor: colors.border, color: colors.text }}
                >
                  {sentiment}
                </motion.span>
              )}
            </div>
            <p className="mt-1.5 text-sm leading-relaxed text-text-secondary line-clamp-2">
              {r.text}
            </p>
          </motion.div>
        );
      })}
    </div>
  );
}
