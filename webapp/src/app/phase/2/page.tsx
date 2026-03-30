"use client";

import { motion } from "framer-motion";
import { PresentationShell, PhaseTitle, StepReveal, StatCard, CodeBlock, SimulatedTerminal } from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";
import { ResponseStream } from "@/components/phase2/ResponseStream";
import { TaxonomyTree } from "@/components/phase2/TaxonomyTree";

const TOTAL_STEPS = 11;

const TAGGING_CODE = `import anthropic, json

client = anthropic.Anthropic()

# The finalized taxonomy from our exploration
TAXONOMY = {
    "System Quality": ["Audio Clarity", "Reliability", "Interface"],
    "Communication": ["Timeline Gaps", "Lack of Consultation", "Info Flow"],
    "Training": ["Pace/Coverage", "Follow-up Needed", "Hands-on vs Demo"],
    "Workflow Impact": ["Daily Routines", "Bell Schedule", "Disruption"],
    "Change Management": ["Process Concerns", "Respect", "Prior Experience"],
}

def tag_response(text, taxonomy):
    """Tag a single response against the taxonomy."""
    result = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a survey analyst. Tag responses against "
               "the provided taxonomy. Return structured JSON.",
        messages=[{
            "role": "user",
            "content": f"""Tag this survey response.

Taxonomy: {json.dumps(taxonomy)}

Response: {text}

Return JSON: {{
    "themes": ["matched themes..."],
    "sub_themes": ["matched sub-themes..."],
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "key_phrases": ["relevant phrases..."]
}}"""
        }]
    )
    return json.loads(result.content[0].text)

# Apply to all 500 responses × 5 questions
for survey in surveys:
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        if survey[q]:
            survey[f"{q}_tags"] = tag_response(survey[q], TAXONOMY)`;

// Terminal conversation: initial theme discovery
const TERMINAL_DISCOVER = [
  { type: "system" as const, content: "Reading 50 sample responses to identify recurring themes..." },
  { type: "user" as const, content: "Read through a sample of 50 survey responses and identify the major themes. What are people talking about?" },
  { type: "ai" as const, content: [
    "After reading 50 responses, I've identified 6 recurring themes:",
    "",
    "  1. System Quality — audio clarity, reliability, interface usability",
    "     (~72% of responses mention this, mostly positive)",
    "",
    "  2. Communication Gaps — how the change was communicated",
    "     (~60% mention this, predominantly negative)",
    "",
    "  3. Training Experience — pace, depth, follow-up needs",
    "     (~50% mention this, mixed sentiment)",
    "",
    "  4. Workflow Disruption — impact on daily routines",
    "     (~44% mention this, varies by position)",
    "",
    "  5. Change Management — process, consultation, respect",
    "     (~38% mention this, strongly correlated with tenure)",
    "",
    "  6. Safety & Emergency — emergency alert features",
    "     (~15% mention this, almost exclusively counselors)",
  ]},
];

// Terminal conversation: drilling into communication sub-themes
const TERMINAL_DRILL = [
  ...TERMINAL_DISCOVER,
  { type: "user" as const, content: "Interesting. Break down \"Communication Gaps\" — what specific sub-themes are people raising?" },
  { type: "ai" as const, content: [
    "Breaking down Communication Gaps into sub-themes:",
    "",
    "  Timeline Gaps (134 mentions)",
    "    \"We got a general announcement... then not much until it was happening\"",
    "    Staff learned about changes too late to prepare",
    "",
    "  Lack of Consultation (89 mentions)",
    "    \"I would have appreciated being consulted or at least informed\"",
    "    Long-tenured staff especially expected to be asked for input",
    "",
    "  Information Flow / Hierarchy (75 mentions)",
    "    \"Nobody told the aides anything\" — info stopped at teachers",
    "    Classified staff (custodial, food service) systematically left out",
    "",
    "  Notable: 0% of custodial and food service staff described",
    "  communication as adequate. This is a complete breakdown, not a gap.",
  ]},
];

// Terminal conversation: user brings their own category
const TERMINAL_EXPLORE = [
  ...TERMINAL_DRILL,
  { type: "user" as const, content: "What about operational impacts? Are there cases where the installation actually disrupted people's ability to do their jobs?" },
  { type: "ai" as const, content: [
    "Yes — and this is concentrated in specific positions:",
    "",
    "  Food Service (critical):",
    "    \"The bell schedule kept changing during the install and it threw",
    "    off our whole lunch service\" — affects student nutrition timing,",
    "    kitchen prep schedules. Multiple sites affected.",
    "",
    "  Counselors (safety concern):",
    "    \"I've had students completely shut down after an interruption\"",
    "    — intercom announcements interrupt sensitive sessions.",
    "    They want a 'do not disturb' mode.",
    "",
    "  Teachers at Valley High:",
    "    \"Installers showed up and I hadn't been told they'd be in my area\"",
    "    — lost instructional time during installation.",
    "",
    "  I'd recommend adding \"Operational Impact\" as a top-level theme",
    "  with sub-themes: Bell Schedule Disruption, Confidentiality",
    "  Conflicts, Installation Disruption.",
  ]},
];

export default function Phase2Page() {
  const { step, isVisible, totalSteps } = usePresentation({
    totalSteps: TOTAL_STEPS,
  });

  return (
    <PresentationShell currentStep={step} totalSteps={totalSteps}>
      {/* Step 0: Phase title */}
      {step === 0 && (
        <PhaseTitle
          phaseNumber={2}
          title="Tagging"
          subtitle="Text → Sentiment + Themes"
          accentColor="#8b5cf6"
        />
      )}

      {/* Step 1: Raw response wall — overwhelming */}
      {step === 1 && (
        <div className="flex h-full flex-col">
          <StepReveal visible>
            <h2 className="mb-2 text-3xl font-bold text-text-primary">
              500 open-ended responses
            </h2>
            <p className="mb-4 text-lg text-text-secondary">
              How do you find the signal in all this text?
            </p>
          </StepReveal>
          <div className="flex-1 overflow-hidden">
            <ResponseStream showSentiment={false} />
          </div>
        </div>
      )}

      {/* Step 2: Sentiment colors wash over */}
      {step === 2 && (
        <div className="flex h-full flex-col">
          <StepReveal visible>
            <h2 className="mb-2 text-3xl font-bold text-text-primary">
              AI tags each response for sentiment
            </h2>
            <p className="mb-4 text-lg text-text-secondary">
              <span className="text-positive">Positive</span> ·{" "}
              <span className="text-neutral">Neutral</span> ·{" "}
              <span className="text-negative">Negative</span> — patterns become visible instantly.
            </p>
          </StepReveal>
          <div className="flex-1 overflow-hidden">
            <ResponseStream showSentiment={true} />
          </div>
        </div>
      )}

      {/* Step 3: Eduardo's response before/after */}
      {step === 3 && (
        <div className="flex h-full items-center justify-center gap-8">
          <StepReveal visible direction="left">
            <div className="w-[480px] rounded-xl border border-border-subtle bg-bg-surface p-6">
              <div className="mb-3 text-xs font-medium text-text-muted">Raw Response — Eduardo G., Q1</div>
              <p className="text-base leading-relaxed text-text-secondary">
                &ldquo;Honestly, the transition has been smoother than I expected. The new system
                hasn&rsquo;t really disrupted my routines much — if anything, the intercom is a
                little easier to use than the old one. I still get my announcements when I need
                them, and the bell schedule has been consistent for me.&rdquo;
              </p>
            </div>
          </StepReveal>
          <StepReveal visible direction="right" delay={0.3}>
            <div className="w-[480px] rounded-xl border border-positive/30 bg-positive/5 p-6">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs font-medium text-text-muted">Tagged Response</span>
                <span className="rounded-full bg-positive/20 px-3 py-1 text-xs font-bold text-positive">
                  POSITIVE — 0.82
                </span>
              </div>
              <p className="text-base leading-relaxed text-text-secondary">
                &ldquo;Honestly, the transition has been{" "}
                <span className="rounded bg-positive/15 px-1 font-medium text-positive">smoother than I expected</span>.
                The new system hasn&rsquo;t really disrupted my routines much — if anything, the intercom is{" "}
                <span className="rounded bg-positive/15 px-1 font-medium text-positive">a little easier to use</span>{" "}
                than the old one.&rdquo;
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded bg-bg-surface px-2 py-1 text-xs text-text-muted">System Quality</span>
                <span className="rounded bg-bg-surface px-2 py-1 text-xs text-text-muted">Workflow Impact</span>
                <span className="rounded bg-bg-surface px-2 py-1 text-xs text-text-muted">Positive Transition</span>
              </div>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Step 4: Transition — sentiment isn't enough */}
      {step === 4 && (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <StepReveal visible direction="fade" duration={0.8}>
            <h2 className="text-3xl font-bold text-text-primary">
              Sentiment tells you <em>how</em> people feel.
            </h2>
            <motion.p
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="mt-4 text-2xl text-accent-phase2"
            >
              But not <em>what</em> they&rsquo;re talking about.
            </motion.p>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
              className="mt-8 max-w-xl text-lg text-text-secondary"
            >
              You need a taxonomy — categories to sort responses into.
              You can start with your own, let AI discover them, or both.
            </motion.p>
          </StepReveal>
        </div>
      )}

      {/* Step 5: Terminal — initial theme discovery */}
      {step === 5 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Theme Discovery: Let AI read a sample first
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <SimulatedTerminal messages={TERMINAL_DISCOVER} />
          </StepReveal>
        </div>
      )}

      {/* Step 6: Terminal — drilling into sub-themes */}
      {step === 6 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Drill deeper: break themes into sub-themes
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.1}>
            <SimulatedTerminal messages={TERMINAL_DRILL} />
          </StepReveal>
        </div>
      )}

      {/* Step 7: Terminal — user brings their own lens */}
      {step === 7 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-4 text-2xl font-bold text-text-primary">
              Bring your own questions — the human guides the exploration
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.1}>
            <SimulatedTerminal messages={TERMINAL_EXPLORE} />
          </StepReveal>
        </div>
      )}

      {/* Step 8: Taxonomy tree — the result */}
      {step === 8 && (
        <div className="flex h-full flex-col">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              The result: a human-refined taxonomy
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              AI discovered the themes. The human validated, merged, and structured them.
            </p>
          </StepReveal>
          <div className="flex-1">
            <TaxonomyTree revealLevel={2} />
          </div>
        </div>
      )}

      {/* Step 9: Code — applying tags at scale */}
      {step === 9 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              Now apply the taxonomy at scale
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              With the taxonomy finalized, loop through all 500 responses and tag each one.
            </p>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <CodeBlock
              code={TAGGING_CODE}
              language="python"
              title="tag_responses.py"
              highlightLines={[6, 7, 8, 9, 10, 11, 12, 13, 39, 40, 41, 42]}
            />
          </StepReveal>
        </div>
      )}

      {/* Step 10: Result stat */}
      {step === 10 && (
        <div className="flex h-full flex-col items-center justify-center">
          <StepReveal visible direction="fade">
            <StatCard
              value="2,500"
              label="Tagged Data Points"
              sublabel="500 responses × 5 questions — each with sentiment, themes, sub-themes, and key phrases"
              color="#8b5cf6"
              animate={false}
            />
          </StepReveal>
        </div>
      )}
    </PresentationShell>
  );
}
