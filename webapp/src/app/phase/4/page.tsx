"use client";

import { motion } from "framer-motion";
import {
  PresentationShell,
  PhaseTitle,
  StepReveal,
  StatCard,
  QuoteCard,
  CodeBlock,
  SimulatedTerminal,
} from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";
import { LoopDiagram } from "@/components/phase4/LoopDiagram";
import { ScoreTrajectory } from "@/components/phase4/ScoreTrajectory";
import { BuildingMap } from "@/components/phase4/BuildingMap";
import { TransferGradient } from "@/components/phase4/TransferGradient";
import { SimpsonParadox } from "@/components/phase4/SimpsonParadox";
import { ComparisonTable } from "@/components/phase4/ComparisonTable";

const TOTAL_STEPS = 24;

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

// Round 1: broad exploration
const ROUND1_AGENT = [
  { type: "system" as const, content: "Round 1 — No prior findings. Starting broad exploration." },
  { type: "user" as const, content: "Hypotheses: (1) Sentiment varies by site (2) Varies by position (3) HR fields like transfer status and building wing affect sentiment (4) Tenure and age correlate with sentiment" },
  { type: "ai" as const, content: [
    "Launching 4 parallel sub-agents to investigate...",
    "",
    "  Agent 1 (sites): Valley High lowest (+0.095), Riverside highest",
    "    (+0.201). Gap persists within same positions.",
    "",
    "  Agent 2 (positions): Food Service only negative group (-0.032).",
    "    District Office most positive (+0.418).",
    "",
    "  Agent 3 (HR fields): Transfers +0.334 vs non-transfers +0.119.",
    "    Origin system quality creates 0.48 spread. North Wing at",
    "    Hillcrest (n=30) is net negative — possible hardware issue.",
    "",
    "  Agent 4 (tenure/age): District tenure r=-0.24 (strong).",
    "    Age r=+0.057 (essentially zero). It's institutional",
    "    attachment, not age resistance.",
    "",
    "  Writing research memo and invoking judge...",
  ]},
];

const ROUND1_JUDGE = [
  { type: "system" as const, content: "Judge evaluation — Round 1" },
  { type: "ai" as const, content: [
    "  ┌─────────────────────┬───────┐",
    "  │ Dimension           │ Score │",
    "  ├─────────────────────┼───────┤",
    "  │ Breadth             │   7   │",
    "  │ Depth               │   6   │",
    "  │ Evidence Quality     │   7   │",
    "  │ Rigor               │   5   │",
    "  │ Actionability       │   8   │",
    "  │ Intellectual Honesty │   7   │",
    "  ├─────────────────────┼───────┤",
    "  │ Overall             │  6.7  │",
    "  └─────────────────────┴───────┘",
    "",
    "  Gaps identified by judge:",
    "  • Is the tenure effect confounded with position type?",
    "  • Is the gender gap the same at every site?",
    "  • North Wing issue: physical or demographic?",
    "  • Sentiment scorer has not been validated",
    "  • No interaction testing (A×B effects)",
  ]},
];

// Round 2: addressing the critique
const ROUND2_AGENT = [
  { type: "system" as const, content: "Round 2 — Addressing judge critique from Round 1" },
  { type: "user" as const, content: "Hypotheses: (1) Tenure effect holds after controlling for position (2) Gender gap differs by site (3) North Wing is physical, not demographic (4) Validate sentiment scorer against manual reading" },
  { type: "ai" as const, content: [
    "Launching 4 parallel sub-agents...",
    "",
    "  Agent 1 (confounders): Tenure effect holds across ALL 8",
    "    position types. Not confounded. Partial r after controls: -0.21",
    "",
    "  Agent 2 (gender×site): Males +0.253 at Riverside but",
    "    -0.154 at Valley High — a 0.407-point SWING. Overall",
    "    correlation near zero was masking opposite effects.",
    "",
    "  Agent 3 (North Wing): 100% of 30 staff mention audio",
    "    problems. Demographics match rest of Hillcrest.",
    "    Physical installation defect, not morale issue.",
    "",
    "  Agent 4 (validation): Scored 50 responses manually.",
    "    95% agreement with automated scorer. No direction flips.",
    "    Scorer is reliable.",
    "",
    "  Writing research memo and invoking judge...",
  ]},
];

const ROUND2_JUDGE = [
  { type: "system" as const, content: "Judge evaluation — Round 2" },
  { type: "ai" as const, content: [
    "  ┌─────────────────────┬───────┐",
    "  │ Dimension           │ Score │",
    "  ├─────────────────────┼───────┤",
    "  │ Breadth             │   8   │",
    "  │ Depth               │   7   │",
    "  │ Evidence Quality     │   8   │",
    "  │ Rigor               │   7   │",
    "  │ Actionability       │   8   │",
    "  │ Intellectual Honesty │   8   │",
    "  ├─────────────────────┼───────┤",
    "  │ Overall             │  7.7  │",
    "  └─────────────────────┴───────┘",
    "",
    "  Strengths: Confounder testing, scorer validation, finding",
    "  the gender×site interaction — good instinct.",
    "",
    "  Gaps:",
    "  • Need multivariate regression to isolate independent effects",
    "  • Per-question analysis missing (is Q2 different from Q5?)",
    "  • Haven't tested significance — are these real or noise?",
    "  • No text-level analysis beyond keyword counting",
  ]},
];

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

      {/* === LAYER 1.5: THE ROUNDS IN ACTION === */}

      {/* Step 5: Round 1 — agent investigates */}
      {step === 5 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <div className="mb-1 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Round 1 · Score: ???
            </div>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Agent starts broad: test the obvious variables
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimulatedTerminal
              messages={ROUND1_AGENT}
              accentColor="#f43f5e"
              title="claude-code — auto-research / round 1"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 6: Round 1 — judge scores */}
      {step === 6 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <div className="mb-1 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Round 1 · Score: 6.7
            </div>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Judge: &ldquo;Good start — but you haven&rsquo;t tested interactions&rdquo;
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimulatedTerminal
              messages={ROUND1_JUDGE}
              accentColor="#f59e0b"
              title="judge — evaluation / round 1"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 7: Round 2 — agent addresses critique */}
      {step === 7 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <div className="mb-1 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Round 2 · Score: ???
            </div>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Agent responds to critique: test confounders, validate scorer
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimulatedTerminal
              messages={ROUND2_AGENT}
              accentColor="#f43f5e"
              title="claude-code — auto-research / round 2"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 8: Round 2 — judge scores again */}
      {step === 8 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <div className="mb-1 text-xs font-bold uppercase tracking-wider text-accent-phase4">
              Round 2 · Score: 7.7
            </div>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Judge: &ldquo;Better — now run a regression and analyze the text&rdquo;
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimulatedTerminal
              messages={ROUND2_JUDGE}
              accentColor="#f59e0b"
              title="judge — evaluation / round 2"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 9: Rounds 3-4 summary + trajectory */}
      {step === 9 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-center text-2xl font-bold text-text-primary">
              The pattern continues: critique drives deeper investigation
            </h2>
            <p className="mb-4 text-center text-lg text-text-secondary">
              Round 3: multivariate regression, per-question analysis → <span className="font-bold text-accent-phase4">8.8</span>
              <br />
              Round 4: text clustering, non-response patterns → <span className="font-bold text-positive">9.0 — threshold reached</span>
            </p>
          </StepReveal>
          <StepReveal visible delay={0.3}>
            <ScoreTrajectory revealedPoints={4} />
          </StepReveal>
        </div>
      )}

      {/* Step 10: Transition to discoveries */}
      {step === 10 && (
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

      {/* Steps 11-12: North Wing */}
      {step === 11 && (
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

      {step === 12 && (
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

      {/* Step 13: Transfer Paradox */}
      {step === 13 && (
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

      {/* Steps 14-15: Simpson's Paradox — THE flagship moment */}
      {step === 14 && (
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

      {step === 15 && (
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

      {/* Step 16: Q4 Non-response */}
      {step === 16 && (
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

      {/* Step 17: Quiet dissenters */}
      {step === 17 && (
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

      {/* Step 18: Two Approaches Compared */}
      {step === 18 && (
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

      {/* Step 19: Neither replaced the human */}
      {step === 19 && (
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

      {/* Step 20: The human's role */}
      {step === 20 && (
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

      {/* Step 21: Human judgment quote */}
      {step === 21 && (
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

      {/* Step 22: Key findings summary */}
      {step === 22 && (
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

      {/* Step 23: Bridge to conclusion */}
      {step === 23 && (
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
