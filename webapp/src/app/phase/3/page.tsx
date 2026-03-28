"use client";

import { motion } from "framer-motion";
import { PresentationShell, PhaseTitle, StepReveal, QuoteCard, StatCard } from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";
import { DataJoinAnimation } from "@/components/phase3/DataJoinAnimation";
import {
  HBarChart,
  SITE_DATA,
  TENURE_DATA,
  POSITION_DATA,
  FOOD_SERVICE_BY_SITE,
  CounselorSplitChart,
} from "@/components/phase3/AnalysisCharts";

const TOTAL_STEPS = 11;

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
          title="Analysis"
          subtitle="Demographics Unlock Hidden Patterns"
          accentColor="#f59e0b"
        />
      )}

      {/* Step 1: Data join — separated */}
      {step === 1 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-center text-2xl font-bold text-text-primary">
              Step 1: Join survey responses with HR demographics
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

      {/* Step 3: Site comparison */}
      {step === 3 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase3">
              Obvious Pattern
            </div>
            <HBarChart
              data={SITE_DATA}
              title="Sentiment by Site"
              subtitle="Valley High trails — but why?"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 4: Tenure trend */}
      {step === 4 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase3">
              Obvious Pattern
            </div>
            <HBarChart
              data={TENURE_DATA}
              title="Sentiment by District Tenure"
              subtitle="Monotonic decline — the longer you've been here, the less satisfied you are."
            />
          </StepReveal>
          <StepReveal visible delay={0.5}>
            <div className="mt-6 rounded-lg border border-border-subtle bg-bg-surface px-5 py-4">
              <p className="text-sm text-text-secondary">
                <span className="font-bold text-text-primary">Key insight:</span> It&rsquo;s{" "}
                <em>district tenure</em>, not age (r=+0.057). A 55-year-old new to the district
                is just as positive as a 25-year-old newcomer.
              </p>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Step 5: Position chart */}
      {step === 5 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase3">
              Obvious Pattern
            </div>
            <HBarChart
              data={POSITION_DATA}
              title="Sentiment by Position"
              subtitle="Food Service is the only group with negative overall sentiment."
            />
          </StepReveal>
        </div>
      )}

      {/* Step 6: Food service cross-tab */}
      {step === 6 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase3">
              Intermediate Pattern
            </div>
            <HBarChart
              data={FOOD_SERVICE_BY_SITE}
              title="Food Service Sentiment by Site"
              subtitle="Bell schedule changes disrupted lunch service at every site — worst at Valley High."
            />
          </StepReveal>
          <StepReveal visible delay={0.4}>
            <QuoteCard
              quote="The bell schedule kept changing during the install and it threw off our whole lunch service. We had kids showing up early, showing up late, nobody knew what was going on."
              attribution="Food Service Staff, Valley High"
              className="mt-6"
            />
          </StepReveal>
        </div>
      )}

      {/* Step 7: Counselor split */}
      {step === 7 && (
        <div className="flex h-full flex-col justify-center px-12">
          <StepReveal visible>
            <div className="mb-4 text-xs font-bold uppercase tracking-wider text-accent-phase3">
              Intermediate Pattern
            </div>
            <CounselorSplitChart />
          </StepReveal>
        </div>
      )}

      {/* Step 8: District office */}
      {step === 8 && (
        <div className="flex h-full items-center justify-center gap-12">
          <StepReveal visible direction="left">
            <div className="text-center">
              <div className="mb-2 text-xs font-bold uppercase tracking-wider text-accent-phase3">
                Intermediate Pattern
              </div>
              <StatCard
                value="+0.418"
                label="District Office Sentiment"
                sublabel="Most positive group — they were involved in vendor selection"
                color="#10b981"
                animate={false}
              />
            </div>
          </StepReveal>
          <StepReveal visible direction="right" delay={0.3}>
            <div className="max-w-sm rounded-xl border border-border-subtle bg-bg-surface p-6">
              <h4 className="text-lg font-bold text-text-primary">Why so positive?</h4>
              <ul className="mt-3 space-y-2 text-sm text-text-secondary">
                <li>• Participated in vendor evaluation</li>
                <li>• Had earliest access to information</li>
                <li>• Understood the rationale for the change</li>
                <li>• Felt ownership in the decision</li>
              </ul>
              <p className="mt-4 text-xs italic text-text-muted">
                Involvement → understanding → satisfaction
              </p>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Step 9: Dramatic pause — teaser */}
      {step === 9 && (
        <div className="flex h-full flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.5 }}
            className="text-center"
          >
            <p className="text-3xl font-bold text-text-primary">
              But there are patterns these charts can&rsquo;t show you.
            </p>
          </motion.div>
        </div>
      )}

      {/* Step 10: Teaser question */}
      {step === 10 && (
        <div className="flex h-full flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center max-w-2xl"
          >
            <p className="text-2xl text-text-secondary leading-relaxed">
              What if a variable looks <span className="font-bold text-text-primary">completely irrelevant</span> because
              it&rsquo;s hiding <span className="font-bold text-accent-phase4">opposite effects</span> in different subgroups?
            </p>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.8 }}
              className="mt-8 text-lg text-text-muted"
            >
              To find out, we need to go deeper...
            </motion.p>
          </motion.div>
        </div>
      )}
    </PresentationShell>
  );
}
