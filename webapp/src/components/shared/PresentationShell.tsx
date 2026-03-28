"use client";

import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

const phases = [
  { path: "/", label: "Intro", accent: "#3b82f6" },
  { path: "/phase/1", label: "1", accent: "#06b6d4" },
  { path: "/phase/2", label: "2", accent: "#8b5cf6" },
  { path: "/phase/3", label: "3", accent: "#f59e0b" },
  { path: "/phase/4", label: "4", accent: "#f43f5e" },
  { path: "/conclusion", label: "End", accent: "#3b82f6" },
];

interface PresentationShellProps {
  children: React.ReactNode;
  currentStep?: number;
  totalSteps?: number;
}

export function PresentationShell({
  children,
  currentStep = 0,
  totalSteps = 1,
}: PresentationShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [showHelp, setShowHelp] = useState(false);

  const currentPhaseIndex = phases.findIndex((p) => p.path === pathname);
  const currentAccent =
    phases[currentPhaseIndex]?.accent ?? "#3b82f6";

  // Navigate between phases
  const goToNextPhase = useCallback(() => {
    const next = phases[currentPhaseIndex + 1];
    if (next) router.push(next.path);
  }, [currentPhaseIndex, router]);

  const goToPrevPhase = useCallback(() => {
    const prev = phases[currentPhaseIndex - 1];
    if (prev) router.push(prev.path);
  }, [currentPhaseIndex, router]);

  // Help overlay toggle
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "h" || e.key === "H") {
        if (
          !(e.target instanceof HTMLInputElement) &&
          !(e.target instanceof HTMLTextAreaElement)
        ) {
          setShowHelp((v) => !v);
        }
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  const progress = totalSteps > 1 ? (currentStep / (totalSteps - 1)) * 100 : 100;

  return (
    <div className="relative flex h-screen w-screen flex-col overflow-hidden bg-bg-primary">
      {/* Main content */}
      <div className="flex-1 overflow-hidden">
        <div className="mx-auto h-full max-w-[1200px] px-20 py-12">
          {children}
        </div>
      </div>

      {/* Bottom bar */}
      <div className="relative flex h-12 items-center justify-between px-6">
        {/* Phase nav dots */}
        <div className="flex items-center gap-2">
          {phases.map((phase, i) => (
            <button
              key={phase.path}
              onClick={() => router.push(phase.path)}
              className="flex h-7 min-w-7 items-center justify-center rounded-full px-2 text-xs font-medium transition-all"
              style={{
                backgroundColor:
                  i === currentPhaseIndex
                    ? phase.accent
                    : "transparent",
                color:
                  i === currentPhaseIndex
                    ? "#0f1117"
                    : i < currentPhaseIndex
                    ? phase.accent
                    : "#565a6e",
                border:
                  i === currentPhaseIndex
                    ? "none"
                    : `1px solid ${i < currentPhaseIndex ? phase.accent + "40" : "#2a2d3a"}`,
              }}
            >
              {phase.label}
            </button>
          ))}
        </div>

        {/* Step progress */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-text-muted">
            {currentStep + 1} / {totalSteps}
          </span>
          <div className="h-1 w-32 overflow-hidden rounded-full bg-border-subtle">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: currentAccent }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Phase nav arrows */}
        <div className="flex items-center gap-2">
          <button
            onClick={goToPrevPhase}
            disabled={currentPhaseIndex <= 0}
            className="rounded p-1 text-text-muted transition hover:text-text-primary disabled:opacity-30"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M12 15L7 10L12 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <button
            onClick={goToNextPhase}
            disabled={currentPhaseIndex >= phases.length - 1}
            className="rounded p-1 text-text-muted transition hover:text-text-primary disabled:opacity-30"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M8 5L13 10L8 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Progress bar at very bottom */}
      <div className="h-[2px] w-full bg-border-subtle/50">
        <motion.div
          className="h-full"
          style={{ backgroundColor: currentAccent }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>

      {/* Help overlay */}
      <AnimatePresence>
        {showHelp && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
            onClick={() => setShowHelp(false)}
          >
            <div className="rounded-2xl bg-bg-surface p-8 text-lg">
              <h3 className="mb-4 text-xl font-bold">Keyboard Shortcuts</h3>
              <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                <kbd className="text-text-secondary">→ ↓ Space Enter</kbd>
                <span>Next step</span>
                <kbd className="text-text-secondary">← ↑</kbd>
                <span>Previous step</span>
                <kbd className="text-text-secondary">H</kbd>
                <span>Toggle this help</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
