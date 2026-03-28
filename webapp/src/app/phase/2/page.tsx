"use client";

import { PresentationShell, PhaseTitle, StepReveal, StatCard, CodeBlock } from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";
import { ResponseStream } from "@/components/phase2/ResponseStream";
import { TaxonomyTree } from "@/components/phase2/TaxonomyTree";

const TOTAL_STEPS = 8;

const SENTIMENT_CODE = `import anthropic, json

client = anthropic.Anthropic()

def tag_sentiment(response_text):
    """Score one survey response for sentiment."""
    result = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": f"""Rate the sentiment of this survey response.
            Return JSON: {{
                "sentiment": "positive|negative|neutral",
                "confidence": 0.0-1.0,
                "key_phrases": ["..."]
            }}

            Response: {response_text}"""
        }]
    )
    return json.loads(result.content[0].text)

# Process all 500 responses × 5 questions
for survey in surveys:
    for q in ["q1", "q2", "q3", "q4", "q5"]:
        if survey[q]:
            survey[f"{q}_sentiment"] = tag_sentiment(survey[q])`;

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

      {/* Step 4: Code snippet */}
      {step === 4 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              Simple loop: each response through the LLM
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <CodeBlock
              code={SENTIMENT_CODE}
              language="python"
              title="tag_sentiment.py"
              highlightLines={[10, 11, 12, 13, 14, 15, 16]}
            />
          </StepReveal>
        </div>
      )}

      {/* Step 5: Taxonomy — top level */}
      {step === 5 && (
        <div className="flex h-full flex-col">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              Theme discovery: what are people talking about?
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              AI reads all responses and builds a taxonomy from the bottom up.
            </p>
          </StepReveal>
          <div className="flex-1">
            <TaxonomyTree revealLevel={1} />
          </div>
        </div>
      )}

      {/* Step 6: Taxonomy — with children */}
      {step === 6 && (
        <div className="flex h-full flex-col">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              Each theme breaks into specific sub-topics
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              From 2,500 data points, a clear picture emerges.
            </p>
          </StepReveal>
          <div className="flex-1">
            <TaxonomyTree revealLevel={2} />
          </div>
        </div>
      )}

      {/* Step 7: Result stat */}
      {step === 7 && (
        <div className="flex h-full flex-col items-center justify-center">
          <StepReveal visible direction="fade">
            <StatCard
              value="2,500"
              label="Tagged Data Points"
              sublabel="500 responses × 5 questions — each with sentiment score, confidence, key phrases, and theme tags"
              color="#8b5cf6"
              animate={false}
            />
          </StepReveal>
        </div>
      )}
    </PresentationShell>
  );
}
