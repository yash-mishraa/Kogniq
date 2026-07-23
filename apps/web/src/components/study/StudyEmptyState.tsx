"use client";

import { useStudy } from "@/app/workspace/environments/study/StudyContext";
import { Locus } from "@/components/locus";
import { MOCK_STUDY_MATERIAL } from "@/app/workspace/environments/study/StudyState";

export function StudyEmptyState() {
  const { dispatch } = useStudy();

  const handleSelect = () => {
    // In a real app, this would load the specific context
    dispatch({ type: "START_STUDY", payload: MOCK_STUDY_MATERIAL });
  };

  const suggestions = [
    { label: "Continue from Transformer Architecture", detail: "Last studied 2 hours ago" },
    { label: "Resume yesterday's study", detail: "Self-Attention" },
    { label: "Continue Database Normalization", detail: "Last studied yesterday" },
    { label: "Review today's concepts", detail: "3 items ready" },
  ];

  return (
    <section aria-label="Study starting point" className="flex flex-col flex-1 items-start justify-center pb-32 w-full max-w-3xl mx-auto">
      <div className="w-full">
        <Locus 
          environmentTitle="Study" 
          placeholder="│ Continue learning..."
          mode="suggestion"
          suggestions={suggestions}
          onSelect={handleSelect}
          autoFocus 
        />
      </div>
    </section>
  );
}
