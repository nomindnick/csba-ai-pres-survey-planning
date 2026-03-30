"use client";

import { motion } from "framer-motion";

export function ReportPreview() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mx-auto max-w-3xl rounded-xl border border-border-subtle bg-[#fafafa] shadow-xl overflow-hidden"
    >
      {/* Document header */}
      <div className="border-b border-gray-200 bg-white px-10 py-6">
        <div className="text-xs uppercase tracking-widest text-gray-400">
          Draft Report — Generated from Tagged Survey Data
        </div>
        <h2 className="mt-2 text-2xl font-bold text-gray-900">
          Communications System Installation
        </h2>
        <h3 className="text-lg text-gray-600">
          Staff Survey Analysis — Tri-Valley Unified School District
        </h3>
        <div className="mt-2 text-sm text-gray-400">
          500 respondents · March 2026
        </div>
      </div>

      {/* Report body */}
      <div className="px-10 py-6 text-[14px] leading-relaxed text-gray-700 space-y-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h4 className="text-base font-bold text-gray-900 mb-2">Executive Summary</h4>
          <p>
            Overall staff sentiment toward the new communications system is{" "}
            <span className="rounded bg-emerald-100 px-1 font-medium text-emerald-700">
              moderately positive (+0.154)
            </span>, with significant variation by site, position, and tenure.
            Riverside Elementary leads (+0.201), while Valley High trails (+0.095).
            Food Service is the only position group with net negative sentiment (-0.032).
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <h4 className="text-base font-bold text-gray-900 mb-2">Key Findings</h4>
          <div className="space-y-2">
            <div className="flex gap-3">
              <span className="shrink-0 mt-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600">1</span>
              <p>
                <strong>Tenure is the strongest predictor of satisfaction</strong> — sentiment
                declines monotonically from +0.306 (0-3 years) to -0.113 (20+ years). Age shows
                no correlation.
                <span className="ml-1 text-xs text-gray-400">[n=500, r=-0.24]</span>
              </p>
            </div>
            <div className="flex gap-3">
              <span className="shrink-0 mt-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600">2</span>
              <p>
                <strong>Communication was the top negative theme</strong> — 60% of responses
                mention communication gaps. Classified staff (custodial, food service) report
                0% adequate communication.
                <span className="ml-1 text-xs text-gray-400">[298 mentions across 500 responses]</span>
              </p>
            </div>
            <div className="flex gap-3">
              <span className="shrink-0 mt-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600">3</span>
              <p>
                <strong>Food Service experienced operational disruption</strong> — bell schedule
                changes during installation affected lunch service at all three sites.
                <span className="ml-1 text-xs text-gray-400">[n=44, mean=-0.032]</span>
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2 text-xs text-gray-400"
        >
          <svg className="h-4 w-4 shrink-0" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Every finding above cites sample sizes and is traceable to tagged survey data.
          No interpretive claims beyond what the structured data supports.
        </motion.div>
      </div>
    </motion.div>
  );
}
