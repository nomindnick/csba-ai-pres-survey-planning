"use client";

import { PresentationShell, PhaseTitle, StepReveal, StatCard, CodeBlock } from "@/components/shared";
import { usePresentation } from "@/hooks/usePresentation";
import { PdfWall } from "@/components/phase1/PdfWall";
import { RegexAnimation } from "@/components/phase1/RegexAnimation";
import { ExtractionSplitView } from "@/components/phase1/ExtractionSplitView";
import Image from "next/image";

const TOTAL_STEPS = 10;

const EXTRACTION_CODE = `import anthropic
from pdf2image import convert_from_path

client = anthropic.Anthropic()

def extract_survey(pdf_path):
    """Convert PDF to image, send to Claude, get structured JSON."""
    # Convert PDF page to an image
    image = convert_from_path(pdf_path)[0]
    image_data = encode_image(image)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a data extraction assistant. Extract survey "
               "responses into clean, structured JSON.",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": "Extract these fields as JSON: "
                            "name, site, position, "
                            "years_at_district_band, "
                            "years_in_profession_band, "
                            "q1, q2, q3, q4, q5"
                }
            ]
        }]
    )
    return json.loads(response.content[0].text)`;

export default function Phase1Page() {
  const { step, isVisible, totalSteps } = usePresentation({
    totalSteps: TOTAL_STEPS,
  });

  return (
    <PresentationShell currentStep={step} totalSteps={totalSteps}>
      {/* Step 0: Phase title */}
      {step === 0 && (
        <PhaseTitle
          phaseNumber={1}
          title="Extraction"
          subtitle="500 PDFs → Structured Data"
          accentColor="#06b6d4"
        />
      )}

      {/* Step 1: PDF Wall — the cascade */}
      {step === 1 && (
        <div className="flex h-full flex-col">
          <StepReveal visible direction="fade">
            <h2 className="mb-4 text-3xl font-bold text-text-primary">
              500 survey responses arrived as PDFs
            </h2>
            <p className="mb-4 text-lg text-text-secondary">
              Mixed fonts, handwriting styles, varied layouts — real-world messiness.
            </p>
          </StepReveal>
          <div className="flex-1 overflow-hidden">
            <PdfWall />
          </div>
        </div>
      )}

      {/* Step 2: Zoom into one PDF */}
      {step === 2 && (
        <div className="flex h-full items-center justify-center gap-8">
          <StepReveal visible direction="left">
            <div className="overflow-hidden rounded-xl border border-border-subtle bg-white shadow-2xl">
              <Image
                src="/pdfs/full_01.png"
                alt="Survey 001 — Eduardo Gutierrez"
                width={500}
                height={700}
                className="h-auto w-[500px]"
              />
            </div>
          </StepReveal>
          <StepReveal visible direction="right" delay={0.3}>
            <div className="max-w-sm">
              <h3 className="text-2xl font-bold text-accent-phase1">Meet Eduardo</h3>
              <p className="mt-3 text-lg text-text-secondary">
                Teacher at Riverside Elementary. 11-20 years at the district.
              </p>
              <p className="mt-4 text-base text-text-muted">
                We&rsquo;ll follow his survey through each phase of the analysis.
              </p>
              <div className="mt-6 rounded-lg border border-border-subtle bg-bg-surface px-4 py-3 text-sm text-text-muted">
                5 open-ended questions about the new communications system installation
              </div>
            </div>
          </StepReveal>
        </div>
      )}

      {/* Step 3: The raw text */}
      {step === 3 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              First challenge: extract structured data
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              How do you turn this into something a database can use?
            </p>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <RegexAnimation activeField={-1} />
          </StepReveal>
        </div>
      )}

      {/* Steps 4-5: Regex approach — stepping through fields */}
      {(step === 4 || step === 5) && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              {step === 4 ? "Approach 1: Regular Expressions" : "But regex breaks on messy input"}
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              {step === 4
                ? "Pattern matching — find anchors like \"Name:\" and capture what follows."
                : "Handwriting-style fonts, inconsistent spacing, missing fields..."}
            </p>
          </StepReveal>
          <StepReveal visible delay={0.1}>
            <RegexAnimation
              activeField={step === 4 ? 3 : 2}
              showFailure={step === 5}
            />
          </StepReveal>
        </div>
      )}

      {/* Step 6: LLM approach — split view */}
      {step === 6 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              Approach 2: LLM-Powered Extraction
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              Send the PDF directly to Claude. Get structured JSON back.
            </p>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <ExtractionSplitView showConnectors={false} />
          </StepReveal>
        </div>
      )}

      {/* Step 7: LLM approach — with field connectors */}
      {step === 7 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-2 text-2xl font-bold text-text-primary">
              The LLM understands context, not just patterns
            </h2>
            <p className="mb-6 text-lg text-text-secondary">
              It maps meaning from the document to structured fields — handling variations, handwriting, and edge cases.
            </p>
          </StepReveal>
          <StepReveal visible delay={0.1}>
            <ExtractionSplitView showConnectors={true} />
          </StepReveal>
        </div>
      )}

      {/* Step 8: Code snippet */}
      {step === 8 && (
        <div className="flex h-full flex-col justify-center">
          <StepReveal visible>
            <h2 className="mb-6 text-2xl font-bold text-text-primary">
              The actual code is surprisingly simple
            </h2>
          </StepReveal>
          <StepReveal visible delay={0.2}>
            <CodeBlock
              code={EXTRACTION_CODE}
              language="python"
              title="extract_survey.py"
              highlightLines={[14, 15, 16, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33]}
            />
          </StepReveal>
        </div>
      )}

      {/* Step 9: Result stat */}
      {step === 9 && (
        <div className="flex h-full flex-col items-center justify-center">
          <StepReveal visible direction="fade">
            <StatCard
              value={500}
              label="PDFs → Clean JSON Records"
              sublabel="Including 75 handwriting-style surveys with zero extraction errors"
              color="#06b6d4"
            />
          </StepReveal>
        </div>
      )}
    </PresentationShell>
  );
}
