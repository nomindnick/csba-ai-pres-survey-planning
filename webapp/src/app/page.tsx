"use client";

import { motion } from "framer-motion";
import { PresentationShell, StepReveal } from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";

const TOTAL_STEPS = 4;

export default function LandingPage() {
  const { step, isVisible, totalSteps } = usePresentation({
    totalSteps: TOTAL_STEPS,
  });

  return (
    <PresentationShell currentStep={step} totalSteps={totalSteps}>
      <div className="flex h-full flex-col items-center justify-center text-center">
        {/* Title */}
        <StepReveal visible={isVisible(0)} direction="fade" duration={1}>
          <motion.h1
            className="text-[64px] font-bold leading-tight tracking-tight"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.25, 0.4, 0.25, 1] }}
          >
            <span className="text-text-primary">AI-Powered</span>{" "}
            <span className="text-accent-primary">Survey Analysis</span>
          </motion.h1>
        </StepReveal>

        {/* Subtitle */}
        <StepReveal visible={isVisible(1)} delay={0.1}>
          <p className="mt-6 max-w-2xl text-2xl leading-relaxed text-text-secondary">
            How one person with AI can do the work of an entire research team
          </p>
        </StepReveal>

        {/* Context */}
        <StepReveal visible={isVisible(2)} delay={0.1}>
          <div className="mt-12 rounded-2xl border border-border-subtle bg-bg-surface px-10 py-8">
            <p className="text-xl text-text-secondary">
              <span className="font-semibold text-text-primary">
                Tri-Valley Unified School District
              </span>
            </p>
            <p className="mt-2 text-lg text-text-muted">
              500 staff survey responses about a new communications system installation
            </p>
          </div>
        </StepReveal>

        {/* Scene-setting */}
        <StepReveal visible={isVisible(3)} delay={0.1}>
          <p className="mt-10 text-xl italic text-text-muted">
            &ldquo;You&rsquo;re a school business official. 500 surveys just landed on your desk.
            <br />
            The board wants a report. Where do you start?&rdquo;
          </p>
        </StepReveal>

        {/* CASBO branding */}
        <StepReveal visible={isVisible(0)} direction="fade" delay={0.5}>
          <p className="fixed bottom-16 text-sm text-text-muted">
            CASBO 2026 Annual Conference
          </p>
        </StepReveal>
      </div>
    </PresentationShell>
  );
}
