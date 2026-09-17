"use client";

import { useEffect, useState } from "react";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";

interface Metrics {
  quizzes_completed: number;
  average_quiz_accuracy: number;
}

export function LearningHub({ documentId, status }: { documentId: string, status?: string }) {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [nextAction, setNextAction] = useState<string | null>(null);
  const { switchEnvironment } = useWorkspace();

  useEffect(() => {
    let isMounted = true;
    
    async function fetchData() {
      try {
        const [metricsRes, nextActionRes] = await Promise.all([
          fetch(`/api/v1/analytics?document_id=${documentId}`),
          fetch(`/api/v1/learning/${documentId}/next-action`)
        ]);
        
        if (metricsRes.ok && isMounted) setMetrics(await metricsRes.json());
        if (nextActionRes.ok && isMounted) {
          const actionData = await nextActionRes.json();
          setNextAction(actionData.action);
        }
      } catch (e) {
        console.error("Failed to fetch learning hub data", e);
      }
    }
    
    // Auto-refresh when processing
    fetchData();
    let interval: ReturnType<typeof setInterval> | undefined;
    if (status === "Processing" || status === "Uploaded") {
      interval = setInterval(fetchData, 3000);
    }
    
    return () => {
      isMounted = false;
      if (interval) clearInterval(interval);
    }
  }, [documentId, status]);

  const handleActionClick = () => {
    if (nextAction === "study") switchEnvironment("study");
    else if (nextAction === "quiz") switchEnvironment("quiz");
    else if (nextAction === "flashcards") switchEnvironment("flashcards");
    else if (nextAction === "review") switchEnvironment("study");
  };

  return (
    <div className="mt-12 border-t border-ink/10 pt-12">
      <h2 className="text-2xl font-serif text-ink mb-6">Learning Hub</h2>
      
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-ink/5 p-6 rounded-lg">
          <p className="text-sm uppercase tracking-widest text-ink/60 mb-2">Processing State</p>
          <p className="text-xl font-serif text-ink">{status}</p>
        </div>
        {metrics && (
          <>
            <div className="bg-ink/5 p-6 rounded-lg">
              <p className="text-sm uppercase tracking-widest text-ink/60 mb-2">Quizzes Completed</p>
              <p className="text-xl font-serif text-ink">{metrics.quizzes_completed}</p>
            </div>
            <div className="bg-ink/5 p-6 rounded-lg">
              <p className="text-sm uppercase tracking-widest text-ink/60 mb-2">Average Accuracy</p>
              <p className="text-xl font-serif text-ink">{Math.round(metrics.average_quiz_accuracy * 100)}%</p>
            </div>
          </>
        )}
      </div>

      {nextAction && nextAction !== "processing" && (
        <div className="bg-emerald-500/10 p-6 rounded-lg flex items-center justify-between border-l-4 border-emerald-500">
          <div>
            <p className="text-sm uppercase tracking-widest text-emerald-900/60 mb-1">Recommended Next Action</p>
            <p className="text-xl font-serif text-emerald-900 capitalize">{nextAction}</p>
          </div>
          <button
            onClick={handleActionClick}
            className="px-6 py-3 bg-emerald-600 text-white font-mono text-sm uppercase tracking-widest hover:bg-emerald-700 transition-colors rounded shadow-sm"
          >
            Start
          </button>
        </div>
      )}
    </div>
  );
}
