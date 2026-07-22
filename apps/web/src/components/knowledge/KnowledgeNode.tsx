"use client";

import { useKnowledge } from "@/app/workspace/environments/knowledge/KnowledgeContext";
import type { KnowledgeConcept } from "@/app/workspace/environments/knowledge/KnowledgeTypes";

export function KnowledgeNode({ concept, isSelected }: { concept: KnowledgeConcept; isSelected: boolean }) {
  const { dispatch } = useKnowledge();

  // Typography-first design based on importance
  const typographyClasses = {
    primary: "text-2xl font-serif tracking-tight leading-tight",
    secondary: "text-lg font-serif tracking-tight",
    tertiary: "text-[15px] font-sans tracking-wide",
  }[concept.importance];

  const colorClasses = isSelected 
    ? "text-ink font-medium" 
    : "text-ink/60 hover:text-ink/90";

  return (
    <button
      onClick={() => dispatch({ type: "SELECT_CONCEPT", payload: concept.id })}
      className={`relative flex items-center justify-center p-4 transition-colors duration-300 outline-none group
        ${typographyClasses} ${colorClasses}
      `}
    >
      <span className="relative z-10 whitespace-nowrap">
        {concept.label}
      </span>
      
      {/* Subtle interaction feedback instead of heavy badges/bubbles */}
      {isSelected && (
        <span className="absolute inset-x-2 -bottom-1 h-[2px] bg-ink/10 rounded-full" />
      )}
    </button>
  );
}
