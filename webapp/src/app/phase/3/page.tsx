"use client";

import { motion } from "framer-motion";
import { PresentationShell, PhaseTitle, StepReveal, QuoteCard, SimulatedTerminal } from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";
import { DataJoinAnimation } from "@/components/phase3/DataJoinAnimation";
import {
  HBarChart,
  SITE_DATA,
  TENURE_DATA,
  POSITION_DATA,
} from "@/components/phase3/AnalysisCharts";
import { ReportPreview } from "@/components/phase3/ReportPreview";

const TOTAL_STEPS = 13;

// Terminal: querying the database for patterns
const TERMINAL_QUERY = [
  { type: "user" as const, content: "I have 500 tagged survey responses joined with HR data. Show me sentiment broken down by site and by tenure band." },
  { type: "ai" as const, content: [
    "Here's the breakdown:",
    "",
    "  By Site:",
    "    Riverside Elementary:  +0.201  (n=164)",
    "    Hillcrest Elementary:  +0.166  (n=140)",
    "    Valley High:           +0.095  (n=196)",
    "",
    "  By Tenure:",
    "    0-3 years:   +0.306  (n=108)",
    "    4-10 years:  +0.194  (n=184)",
    "    11-20 years: +0.108  (n=132)",
    "    20+ years:   -0.113  (n=76)   ← only negative group",
    "",
    "  Notable: tenure correlates at r=-0.24, but age shows",
    "  essentially zero correlation (r=+0.057). It's institutional",
    "  attachment, not age, driving the pattern.",
  ]},
  { type: "user" as const, content: "Which position groups are most negative? And are there any cross-tab patterns worth flagging?" },
  { type: "ai" as const, content: [
    "  Position sentiment (sorted):",
    "    District Office:    +0.418  (n=12)  — most positive",
    "    Counselors:         +0.326  (n=18)",
    "    Site Admins:        +0.258  (n=20)",
    "    Teachers:           +0.152  (n=310)",
    "    Paraprofessionals:  +0.121  (n=52)",
    "    Custodial:          +0.089  (n=44)",
    "    Food Service:       -0.032  (n=44)  ← only negative",
    "",
    "  Cross-tab flag: Food Service is negative at every site,",
    "  worst at Valley High (-0.107). Their top theme is",
    "  \"Workflow Impact > Bell Schedule\" — the installation",
    "  disrupted lunch service operations.",
  ]},
];

// Terminal: directing report generation
const TERMINAL_REPORT = [
  { type: "user" as const, content: "Draft a board-ready report section summarizing these findings. Cite sample sizes. Keep it factual — only what the tagged data supports." },
  { type: "ai" as const, content: [
    "  Drafting report from structured survey data...",
    "",
    "  ✓ Executive summary (overall sentiment + site comparison)",
    "  ✓ Finding 1: Tenure as strongest predictor (with statistics)",
    "  ✓ Finding 2: Communication theme analysis (298 mentions)",
    "  ✓ Finding 3: Food service operational disruption",
    "  ✓ Position-by-site cross-tabulation table",
    "  ✓ Recommendations based on tagged themes",
    "",
    "  Report drafted. Every claim cites sample size and is",
    "  traceable to the tagged data. No interpretive claims",
    "  beyond what the structured fields support.",
  ]},
];

export default function Phase3Page() {
  const { step, isVisible, totalSteps } = usePresentation({
    totalSteps: TOTAL_STEPS,
  });

  return (
    <PresentationShell currentStep={step} totalSteps={totalSteps}>
      {/* Step 0: Phase title */}
      {step === 0 && (
        <PhaseTitle
          phaseNumber={3}
          title="Analysis & Reporting"
          subtitle="From Tagged Data to Board-Ready Report"
          accentColor="#f59e0b"
        />
      )}

      {/* Step 1: Data join — separated */}
      {step === 1 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-center text-2xl font-bold text-text-primary">
              Join survey responses with HR demographics
            </h2>
            <p className="mb-8 text-center text-lg text-text-secondary">
              Now we know not just <em>what they said</em>, but <em>who they are</em>.
            </p>
          </StepReveal>
          <StepReveal visible delay={0.3}>
            <DataJoinAnimation joined={false} />
          </StepReveal>
        </div>
      )}

      {/* Step 2: Data join — merged */}
      {step === 2 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-center text-2xl font-bold text-text-primary">
              Matched on name: 500 complete records
            </h2>
            <p className="mb-8 text-center text-lg text-text-secondary">
              7 survey fields + 13 HR fields = <span className="font-bold text-accent-phase3">20 dimensions per person</span>
            </p>
          </StepReveal>
          <DataJoinAnimation joined={true} />
        </div>
      )}

      {/* Step 3: Site + tenure charts condensed */}
      {step === 3 && (
        <div className="flex h-full items-center justify-center gap-12 px-8">
          <StepReveal visible direction="left" className="flex-1">
            <HBarChart
              data={SITE_DATA}
              title="By Site"
              subtitle="Valley High trails"
            />
          </StepReveal>
          <StepReveal visible direction="right" delay={0.2} className="flex-1">
            <HBarChart
              data={TENURE_DATA}
              title="By Tenure"
              subtitle="Monotonic decline with district tenure"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 4: Position chart */}
      {step === 4 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <HBarChart
              data={POSITION_DATA}
              title="By Position"
              subtitle="Food Service is the only group with negative overall sentiment."
            />
          </StepReveal>
          <StepReveal visible delay={0.5}>
            <QuoteCard
              quote="The bell schedule kept changing during the install and it threw off our whole lunch service."
              attribution="Food Service Staff, Valley High"
              className="mt-6"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 5: Terminal — querying the database */}
      {step === 5 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Query the data: find patterns, cross-tabulate, flag anomalies
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimulatedTerminal
              messages={TERMINAL_QUERY}
              accentColor="#f59e0b"
              title="claude-code — survey-analysis/data"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 6: Terminal — direct report generation */}
      {step === 6 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Direct AI to draft the report from the data
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimulatedTerminal
              messages={[...TERMINAL_QUERY, ...TERMINAL_REPORT]}
              accentColor="#f59e0b"
              title="claude-code — survey-analysis/data"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 7: Report preview */}
      {step === 7 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-6 text-center text-2xl font-bold text-text-primary">
              The output: a structured, citeable report
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.3}>
            <ReportPreview />
          </StepReveal>
        </div>
      )}

      {/* Step 8: Accountability checkpoint */}
      {step === 8 && (
        <div className="flex h-full flex-col items-center justify-center">
          <StepReveal visible direction="fade" duration={0.8}>
            <h2 className="text-center text-3xl font-bold text-text-primary">
              The Accountability Checkpoint
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.4}>
            <div className="mt-8 grid grid-cols-3 gap-6 max-w-4xl">
              {[
                {
                  icon: "✓",
                  title: "Verified Taxonomy",
                  desc: "You reviewed and refined the theme categories before tagging.",
                  color: "#10b981",
                },
                {
                  icon: "✓",
                  title: "Traceable Claims",
                  desc: "Every finding cites sample sizes and maps to tagged data fields.",
                  color: "#10b981",
                },
                {
                  icon: "✓",
                  title: "Human-Directed Queries",
                  desc: "You chose what to analyze. AI executed, you decided what matters.",
                  color: "#10b981",
                },
              ].map((item, i) => (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + i * 0.15 }}
                  className="rounded-xl border border-positive/20 bg-positive/5 p-6 text-center"
                >
                  <div className="text-3xl font-bold" style={{ color: item.color }}>{item.icon}</div>
                  <div className="mt-3 text-base font-bold text-text-primary">{item.title}</div>
                  <div className="mt-2 text-sm text-text-secondary">{item.desc}</div>
                </motion.div>
              ))}
            </div>
          </StepReveal>
          <StepReveal visible delay={1}>
            <p className="mt-8 text-lg text-text-secondary">
              This report is <span className="font-bold text-positive">safe to present to a board</span>.
              Everything in it is defensible.
            </p>
          </StepReveal>
        </div>
      )}

      {/* Step 9: This alone is valuable */}
      {step === 9 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <StepReveal visible direction="fade">
            <h2 className="text-3xl font-bold text-text-primary max-w-2xl">
              This alone is already powerful.
            </h2>
            <p className="mt-4 text-xl text-text-secondary max-w-2xl">
              You went from 500 raw PDFs to a board-ready report
              with verified findings and cited statistics.
            </p>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mt-6 text-lg text-text-muted"
            >
              Most organizations would stop here.
            </motion.p>
          </StepReveal>
        </div>
      )}

      {/* Step 10: The tradeoff */}
      {step === 10 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <StepReveal visible direction="fade" duration={0.8}>
            <h2 className="text-3xl font-bold text-text-primary">
              But what are we missing?
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.5}>
            <div className="mt-8 grid grid-cols-2 gap-8 max-w-3xl text-left">
              <div className="rounded-xl border border-positive/20 bg-positive/5 p-6">
                <h3 className="text-lg font-bold text-positive">What this approach gives you</h3>
                <ul className="mt-3 space-y-2 text-sm text-text-secondary">
                  <li>• Counts, averages, cross-tabulations</li>
                  <li>• Theme distributions and sentiment scores</li>
                  <li>• Patterns visible in structured fields</li>
                  <li>• Defensible, citeable claims</li>
                </ul>
              </div>
              <div className="rounded-xl border border-neutral/20 bg-neutral/5 p-6">
                <h3 className="text-lg font-bold text-neutral">What it can&rsquo;t tell you</h3>
                <ul className="mt-3 space-y-2 text-sm text-text-secondary">
                  <li>• <em>Why</em> people feel the way they do</li>
                  <li>• Patterns hidden by aggregation</li>
                  <li>• What people <em>didn&rsquo;t</em> say (silence as signal)</li>
                  <li>• Interactions between variables that cancel out</li>
                </ul>
              </div>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Step 11: The structured data limitation */}
      {step === 11 && (
        <div className="flex h-full flex-col items-center justify-center text-center max-w-3xl mx-auto">
          <StepReveal visible>
            <p className="text-2xl leading-relaxed text-text-secondary">
              Structured data tells you <span className="font-bold text-text-primary">what</span> happened.
            </p>
            <motion.p
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="mt-4 text-2xl leading-relaxed text-text-secondary"
            >
              The actual responses tell you <span className="font-bold text-accent-phase4">why</span>.
            </motion.p>
          </StepReveal>
          <StepReveal visible delay={1}>
            <p className="mt-8 text-lg text-text-muted">
              To get there, we need AI that doesn&rsquo;t just query data —
              it needs to <em>read</em>, <em>investigate</em>, and <em>challenge its own assumptions</em>.
            </p>
          </StepReveal>
        </div>
      )}

      {/* Step 12: Bridge to Phase 4 */}
      {step === 12 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <p className="text-2xl text-text-secondary">
              What if we gave AI the autonomy to investigate on its own —
            </p>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.6 }}
              className="mt-4 text-3xl font-bold text-accent-phase4"
            >
              with guardrails?
            </motion.p>
          </motion.div>
        </div>
      )}
    </PresentationShell>
  );
}
