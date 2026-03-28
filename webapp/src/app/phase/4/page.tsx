"use client";

import { motion } from "framer-motion";
import {
  PresentationShell,
  PhaseTitle,
  StepReveal,
  StatCard,
  QuoteCard,
  CodeBlock,
} from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";
import { LoopDiagram } from "@/components/phase4/LoopDiagram";
import { ScoreTrajectory } from "@/components/phase4/ScoreTrajectory";
import { BuildingMap } from "@/components/phase4/BuildingMap";
import { TransferGradient } from "@/components/phase4/TransferGradient";
import { SimpsonParadox } from "@/components/phase4/SimpsonParadox";
import { ComparisonTable } from "@/components/phase4/ComparisonTable";

const TOTAL_STEPS = 20;

const RESEARCH_CODE = `# The auto-research loop
while judge_score < 9.0 and round_num <= 12:
    # 1. Agent forms hypotheses from judge critique
    hypotheses = formulate_hypotheses(
        prior_findings, judge_critique
    )

    # 2. Parallel sub-agents investigate
    findings = investigate_parallel(
        data, hypotheses  # Python scripts + reading responses
    )

    # 3. Synthesize into research memo
    memo = rewrite_memo(prior_findings + findings)

    # 4. Independent judge scores the work
    judge_score, critique = invoke_judge(
        round_log, memo, rubric  # 6 dimensions, 1-10 each
    )

    round_num += 1`;

export default function Phase4Page() {
  const { step, isVisible, totalSteps } = usePresentation({
    totalSteps: TOTAL_STEPS,
  });

  return (
    <PresentationShell currentStep={step} totalSteps={totalSteps}>
      {/* === LAYER 1: THE LOOP === */}

      {/* Step 0: Phase title */}
      {step === 0 && (
        <PhaseTitle
          phaseNumber={4}
          title="Agentic Research"
          subtitle="Autonomous Investigation with Guardrails"
          accentColor="#f43f5e"
        />
      )}

      {/* Step 1: What is agentic research? */}
      {step === 1 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <StepReveal visible>
            <h2 className="text-3xl font-bold text-text-primary">
              What happens when you give AI <span className="text-accent-phase4">autonomy</span> to investigate?
            </h2>
            <p className="mt-4 max-w-2xl text-xl text-text-secondary">
              Instead of asking one question at a time, we set up a loop:
              the AI investigates, an independent judge evaluates,
              and the critique drives the next round.
            </p>
          </StepReveal>
        </div>
      )}

      {/* Step 2: Loop architecture */}
      {step === 2 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-8 text-center text-2xl font-bold text-text-primary">
              The Research Loop
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <LoopDiagram />
          </StepReveal>
        </div>
      )}

      {/* Step 3: Judge rubric */}
      {step === 3 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              The Judge: 6 Dimensions of Research Quality
            </h2>
          </StepReveal>
          <div className="grid grid-cols-3 gap-4">
            {[
              { name: "Breadth", desc: "Did it examine all available data dimensions?", icon: "🔭" },
              { name: "Depth", desc: "Did it test interactions, not just surface comparisons?", icon: "🔬" },
              { name: "Evidence", desc: "Statistics with sample sizes? Representative quotes?", icon: "📊" },
              { name: "Rigor", desc: "Were confounders tested? Findings challenged?", icon: "⚗️" },
              { name: "Actionability", desc: "Could a school administrator act on the recommendations?", icon: "🎯" },
              { name: "Honesty", desc: "Are limitations acknowledged? Surprising findings highlighted?", icon: "🪞" },
            ].map((dim, i) => (
              <motion.div
                key={dim.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="rounded-xl border border-border-subtle bg-bg-surface p-5"
              >
                <div className="text-2xl">{dim.icon}</div>
                <div className="mt-2 text-base font-bold text-text-primary">{dim.name}</div>
                <div className="mt-1 text-sm text-text-muted">{dim.desc}</div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Step 4: Code snippet */}
      {step === 4 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              The loop in code
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <CodeBlock
              code={RESEARCH_CODE}
              language="python"
              title="research_loop.py"
              highlightLines={[2, 17, 18, 19]}
            />
          </StepReveal>
        </div>
      )}

      {/* Step 5: Score trajectory — all 4 rounds */}
      {step === 5 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-center text-2xl font-bold text-text-primary">
              Score Trajectory: Quality Improved Each Round
            </h2>
            <p className="mb-6 text-center text-lg text-text-secondary">
              4 rounds to reach the 9.0 threshold — each judge critique drove deeper investigation
            </p>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <ScoreTrajectory revealedPoints={4} />
          </StepReveal>
        </div>
      )}

      {/* Step 6: Transition to discoveries */}
      {step === 6 && (
        <div className="flex h-full flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
            className="text-center"
          >
            <p className="text-3xl font-bold text-text-primary">
              What did the AI discover?
            </p>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mt-4 text-xl text-text-secondary"
            >
              Patterns that were <span className="text-accent-phase4 font-medium">invisible</span> in the standard analysis
            </motion.p>
          </motion.div>
        </div>
      )}

      {/* === LAYER 2: THE DISCOVERIES === */}

      {/* Steps 7-8: North Wing */}
      {step === 7 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Discovery 1
            </div>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              A Hardware Defect Hidden in Averages
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.3}>
            <BuildingMap showNorthWing={false} />
          </StepReveal>
        </div>
      )}

      {step === 8 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Discovery 1
            </div>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              North Wing: 100% Audio Failure
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <BuildingMap showNorthWing={true} />
          </StepReveal>
        </div>
      )}

      {/* Steps 9-10: Transfer Paradox */}
      {step === 9 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Discovery 2
            </div>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              The Transfer Paradox: Same System, Opposite Reactions
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.3}>
            <TransferGradient />
          </StepReveal>
        </div>
      )}

      {/* Steps 10-11: Simpson's Paradox — THE flagship moment */}
      {step === 10 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Discovery 3
            </div>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimpsonParadox stage="aggregate" />
          </StepReveal>
        </div>
      )}

      {step === 11 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Discovery 3: Simpson&rsquo;s Paradox
            </div>
          </StepReveal>
          <StepReveal visible delay={0.1}>
            <SimpsonParadox stage="split" />
          </StepReveal>
        </div>
      )}

      {/* Step 12: Q4 Non-response */}
      {step === 12 && (
        <div className="flex h-full items-center justify-center gap-12">
          <StepReveal visible direction="left">
            <div className="text-center">
              <div className="mb-4 text-xs font-bold uppercase tracking-wider text-accent-phase4">
                Discovery 4
              </div>
              <StatCard
                value="14%"
                label={"Left \"what's working well?\" blank"}
                color="#f43f5e"
                animate={false}
              />
            </div>
          </StepReveal>
          <StepReveal visible direction="right" delay={0.3}>
            <div className="max-w-sm space-y-4">
              <div className="rounded-xl border border-negative/30 bg-negative/5 p-5">
                <div className="text-sm text-text-secondary">
                  Non-responders&rsquo; average sentiment
                </div>
                <div className="mt-1 text-3xl font-extrabold text-negative">-1.69</div>
                <div className="mt-1 text-sm text-text-muted">
                  vs +1.44 for responders (p &lt; 0.0001)
                </div>
              </div>
              <p className="text-sm text-text-secondary">
                Highest among 20+ year tenure (22.4% blank vs 4.6% for newcomers).
              </p>
              <p className="text-sm font-medium text-text-primary">
                Silence is data. Non-response is the strongest dissatisfaction signal in the dataset.
              </p>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Step 13: Quiet dissenters */}
      {step === 13 && (
        <div className="flex h-full items-center justify-center gap-12">
          <StepReveal visible direction="left">
            <div className="text-center">
              <div className="mb-4 text-xs font-bold uppercase tracking-wider text-accent-phase4">
                Discovery 5
              </div>
              <StatCard
                value="17.6%"
                label="Use hedging language"
                sublabel={'"It\'s fine" · "Good enough" · "I guess"'}
                color="#f59e0b"
                animate={false}
              />
            </div>
          </StepReveal>
          <StepReveal visible direction="right" delay={0.3}>
            <div className="max-w-sm space-y-4">
              <div className="rounded-xl border border-neutral/30 bg-neutral/5 p-5">
                <div className="text-sm text-text-secondary">Hedging rates by position</div>
                <div className="mt-3 space-y-2">
                  {[
                    { label: "Custodial", rate: "30.3%", width: "80%" },
                    { label: "Food Service", rate: "28.9%", width: "75%" },
                    { label: "Teachers", rate: "15.2%", width: "40%" },
                    { label: "Admin", rate: "8.1%", width: "21%" },
                  ].map((r) => (
                    <div key={r.label} className="flex items-center gap-3 text-sm">
                      <span className="w-24 text-text-muted">{r.label}</span>
                      <div className="flex-1 h-4 rounded bg-bg-primary overflow-hidden">
                        <motion.div
                          className="h-full rounded bg-neutral/40"
                          initial={{ width: 0 }}
                          animate={{ width: r.width }}
                          transition={{ duration: 0.6 }}
                        />
                      </div>
                      <span className="w-12 text-right font-bold text-neutral">{r.rate}</span>
                    </div>
                  ))}
                </div>
              </div>
              <p className="text-sm text-text-secondary">
                Reclassifying hedgers from neutral to negative shifts district negative rate
                from <span className="font-bold">28.8%</span> to <span className="font-bold text-negative">34.2%</span>.
              </p>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Steps 14-15: Two Approaches Compared */}
      {step === 14 && (
        <div className="flex h-full flex-col justify-center px-8">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Two Approaches
            </div>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              Same data, same AI — different designs, different insights
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.3}>
            <ComparisonTable />
          </StepReveal>
        </div>
      )}

      {/* === LAYER 3: HUMAN IN THE LOOP === */}

      {/* Step 15: Neither replaced the human */}
      {step === 15 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <StepReveal visible direction="fade" duration={0.8}>
            <h2 className="text-3xl font-bold text-text-primary">
              Neither approach replaced the human.
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.5}>
            <div className="mt-8 grid grid-cols-2 gap-8 max-w-3xl">
              <div className="rounded-xl border border-accent-primary/20 bg-accent-primary/5 p-6">
                <h3 className="text-lg font-bold text-accent-primary">Manual Loop Found</h3>
                <ul className="mt-3 space-y-2 text-sm text-text-secondary text-left">
                  <li>• Hedging language — &ldquo;compliance without consent&rdquo;</li>
                  <li>• Riverside polarization narrative</li>
                  <li>• Qualitative depth in individual responses</li>
                </ul>
              </div>
              <div className="rounded-xl border border-accent-phase4/20 bg-accent-phase4/5 p-6">
                <h3 className="text-lg font-bold text-accent-phase4">Auto Loop Found</h3>
                <ul className="mt-3 space-y-2 text-sm text-text-secondary text-left">
                  <li>• Multivariate regression (7 independent predictors)</li>
                  <li>• Text clustering (7 respondent archetypes)</li>
                  <li>• Per-question regression (gender = training only)</li>
                </ul>
              </div>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Step 16: The human's role */}
      {step === 16 && (
        <div className="flex h-full flex-col items-center justify-center">
          <StepReveal visible>
            <h2 className="mb-8 text-center text-3xl font-bold text-text-primary">
              The human&rsquo;s role shifted — it didn&rsquo;t disappear.
            </h2>
          </StepReveal>
          <div className="grid grid-cols-2 gap-6 max-w-3xl">
            {[
              { before: "Running the analysis", after: "Designing the research system" },
              { before: "Writing Python scripts", after: "Crafting the judge rubric" },
              { before: "Reading 500 responses", after: "Choosing which patterns to investigate" },
              { before: "Computing statistics", after: "Deciding what the findings mean" },
            ].map((shift, i) => (
              <motion.div
                key={shift.after}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.12 }}
                className="flex items-center gap-4 rounded-xl border border-border-subtle bg-bg-surface p-4"
              >
                <div className="flex-1">
                  <div className="text-sm text-text-muted line-through">{shift.before}</div>
                  <div className="mt-1 text-sm font-bold text-text-primary">{shift.after}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Step 17: Human judgment quote */}
      {step === 17 && (
        <div className="flex h-full flex-col items-center justify-center max-w-3xl mx-auto">
          <StepReveal visible>
            <QuoteCard
              quote="The human brought the strategic idea: apply the auto-research pattern to qualitative research. Claude Code researched the pattern, designed the rubric, built the system. The human ran the experiment, evaluated the results, decided what to try next. Both approaches demonstrate different value — manual is like coaching a researcher; auto-research is like designing a meta-system."
              attribution="Process notes, Act 4 development"
            />
          </StepReveal>
          <StepReveal visible delay={0.5}>
            <p className="mt-8 text-lg text-text-secondary text-center">
              Design choices matter enormously: same data, same AI,{" "}
              <span className="font-bold text-text-primary">different instructions → different insights</span>.
            </p>
          </StepReveal>
        </div>
      )}

      {/* Step 18: Key findings summary */}
      {step === 18 && (
        <div className="flex h-full flex-col justify-center px-8">
          <StepReveal visible>
            <h2 className="mb-6 text-center text-2xl font-bold text-text-primary">
              8 Key Findings — Each Actionable
            </h2>
          </StepReveal>
          <div className="grid grid-cols-2 gap-3">
            {[
              { num: 1, title: "System works; process didn't", color: "#10b981" },
              { num: 2, title: "District tenure predicts satisfaction (not age)", color: "#06b6d4" },
              { num: 3, title: "Communication failed along hierarchy", color: "#f43f5e" },
              { num: 4, title: "North Wing hardware defect — facilities needed", color: "#f43f5e" },
              { num: 5, title: "Satisfaction is relative to prior experience", color: "#f59e0b" },
              { num: 6, title: "Valley High broad-based deficit", color: "#f59e0b" },
              { num: 7, title: "Riverside most polarized (not Valley High)", color: "#8b5cf6" },
              { num: 8, title: "Food service operationally harmed by bell changes", color: "#f43f5e" },
            ].map((finding, i) => (
              <motion.div
                key={finding.num}
                initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex items-center gap-4 rounded-lg border border-border-subtle bg-bg-surface px-4 py-3"
              >
                <span
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold"
                  style={{ backgroundColor: `${finding.color}15`, color: finding.color }}
                >
                  {finding.num}
                </span>
                <span className="text-sm text-text-primary">{finding.title}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Step 19: Bridge to conclusion */}
      {step === 19 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <p className="text-2xl text-text-secondary">
              From 500 raw PDFs to 8 actionable findings.
            </p>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.6 }}
              className="mt-6 text-3xl font-bold text-text-primary"
            >
              One person. One AI. One afternoon.
            </motion.p>
          </motion.div>
        </div>
      )}
    </PresentationShell>
  );
}
