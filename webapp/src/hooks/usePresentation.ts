"use client";

import { useState, useEffect, useCallback } from "react";

interface UsePresentationOptions {
  totalSteps: number;
  onNext?: () => void;
  onPrev?: () => void;
}

export function usePresentation({ totalSteps, onNext, onPrev }: UsePresentationOptions) {
  const [step, setStep] = useState(0);

  const next = useCallback(() => {
    setStep((s) => {
      if (s < totalSteps - 1) {
        onNext?.();
        return s + 1;
      }
      return s;
    });
  }, [totalSteps, onNext]);

  const prev = useCallback(() => {
    setStep((s) => {
      if (s > 0) {
        onPrev?.();
        return s - 1;
      }
      return s;
    });
  }, [onPrev]);

  const goTo = useCallback(
    (n: number) => setStep(Math.max(0, Math.min(n, totalSteps - 1))),
    [totalSteps]
  );

  const isVisible = useCallback((n: number) => step >= n, [step]);
  const isActive = useCallback((n: number) => step === n, [step]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      )
        return;

      switch (e.key) {
        case "ArrowRight":
        case "ArrowDown":
        case " ":
        case "Enter":
          e.preventDefault();
          next();
          break;
        case "ArrowLeft":
        case "ArrowUp":
          e.preventDefault();
          prev();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [next, prev]);

  return { step, next, prev, goTo, isVisible, isActive, totalSteps };
}
