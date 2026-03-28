"use client";

import { motion } from "framer-motion";
import { PresentationShell, StepReveal } from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";

const TOTAL_STEPS = 5;

export default function ConclusionPage() {
  const { step, isVisible, totalSteps } = usePresentation({
    totalSteps: TOTAL_STEPS,
  });

  return (
    <PresentationShell currentStep={step} totalSteps={totalSteps}>
      <div className="flex h-full flex-col items-center justify-center text-center">
        {/* Main thesis */}
        <StepReveal visible={isVisible(0)} direction="fade" duration={1}>
          <h1 className="text-[56px] font-bold leading-tight tracking-tight">
            AI doesn&rsquo;t automate &mdash;{" "}
            <span className="text-accent-primary">it amplifies.</span>
          </h1>
        </StepReveal>

        {/* Concentric circles placeholder */}
        <StepReveal visible={isVisible(1)} delay={0.2}>
          <div className="mt-12 flex items-center justify-center">
            {/* Outer ring: Data */}
            <motion.div
              className="flex items-center justify-center rounded-full border-2 border-text-muted/30"
              style={{ width: 400, height: 400 }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              <span className="absolute mt-[-180px] text-sm font-medium text-text-muted">
                DATA — 500 surveys, 20 fields
              </span>
              {/* Middle ring: AI */}
              <motion.div
                className="flex items-center justify-center rounded-full border-2 border-accent-primary/50"
                style={{ width: 260, height: 260 }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.4, ease: "easeOut" }}
              >
                <span className="absolute mt-[-110px] text-sm font-medium text-accent-primary">
                  AI — execution, pattern-finding, scale
                </span>
                {/* Inner ring: Human */}
                <motion.div
                  className="flex items-center justify-center rounded-full bg-accent-primary/10 border-2 border-accent-primary"
                  style={{ width: 120, height: 120 }}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.8, ease: "easeOut" }}
                >
                  <span className="text-xs font-bold text-accent-primary text-center leading-tight">
                    HUMAN
                    <br />
                    strategy
                    <br />
                    judgment
                  </span>
                </motion.div>
              </motion.div>
            </motion.div>
          </div>
        </StepReveal>

        {/* Force multiplier */}
        <StepReveal visible={isVisible(2)} delay={0.1}>
          <p className="mt-10 text-2xl text-text-secondary">
            One person + AI ={" "}
            <span className="font-semibold text-text-primary">
              a team of researchers
            </span>
          </p>
        </StepReveal>

        {/* Scope statement */}
        <StepReveal visible={isVisible(3)} delay={0.1}>
          <p className="mt-4 text-xl text-text-muted">
            The time isn&rsquo;t saved. The{" "}
            <span className="font-semibold text-text-primary">scope is expanded.</span>
          </p>
        </StepReveal>

        {/* Q&A */}
        <StepReveal visible={isVisible(4)} delay={0.2}>
          <div className="mt-12 text-lg text-text-muted">
            Questions &amp; Discussion
          </div>
        </StepReveal>
      </div>
    </PresentationShell>
  );
}
