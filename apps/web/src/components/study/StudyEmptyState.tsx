"use client";

import { useStudy } from "@/app/workspace/environments/study/StudyContext";
import { Locus } from "@/components/locus";

export function StudyEmptyState() {
  const { dispatch } = useStudy();

  const handleSelect = () => {
    // In a real app, this would load the specific context
    dispatch({ 
      type: "START_STUDY", 
      payload: { status: "idle", data: null, error: null } 
    });
  };

  const suggestions = [
    { label: "Resume yesterday's study", detail: "Recent concepts" },
    { label: "Review your saved notes", detail: "Last studied yesterday" },
    { label: "Start a new session", detail: "Ready to study" },
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
