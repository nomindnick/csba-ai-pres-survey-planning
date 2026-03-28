"use client";

import { Highlight, themes } from "prism-react-renderer";
import { motion } from "framer-motion";

interface CodeBlockProps {
  code: string;
  language?: string;
  highlightLines?: number[];
  title?: string;
  className?: string;
}

export function CodeBlock({
  code,
  language = "python",
  highlightLines = [],
  title,
  className = "",
}: CodeBlockProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`overflow-hidden rounded-xl border border-border-subtle bg-bg-surface ${className}`}
    >
      {title && (
        <div className="border-b border-border-subtle px-5 py-3 text-sm font-medium text-text-secondary">
          {title}
        </div>
      )}
      <Highlight theme={themes.nightOwl} code={code.trim()} language={language}>
        {({ tokens, getLineProps, getTokenProps }) => (
          <pre className="overflow-x-auto p-5 text-[16px] leading-relaxed">
            {tokens.map((line, i) => {
              const { key: _lineKey, ...lineProps } = getLineProps({ line });
              const isHighlighted = highlightLines.includes(i + 1);
              return (
                <div
                  key={i}
                  {...lineProps}
                  className={`${lineProps.className || ""} ${
                    isHighlighted
                      ? "bg-accent-primary/10 -mx-5 border-l-2 border-accent-primary px-[18px]"
                      : ""
                  }`}
                >
                  <span className="mr-4 inline-block w-8 select-none text-right text-text-muted opacity-50">
                    {i + 1}
                  </span>
                  {line.map((token, j) => {
                    const { key: _tokenKey, ...tokenProps } = getTokenProps({ token });
                    return <span key={j} {...tokenProps} />;
                  })}
                </div>
              );
            })}
          </pre>
        )}
      </Highlight>
    </motion.div>
  );
}
