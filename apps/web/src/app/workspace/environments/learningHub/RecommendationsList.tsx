"use client";

import { useEffect, useState } from "react";
import { serviceProvider } from "@/lib/providers";
import { useWorkspace } from "../../WorkspaceContext";
import type { LearnerRecommendation } from "@/lib/services/interfaces/IStudentService";

export function RecommendationsList() {
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [recommendations, setRecommendations] = useState<LearnerRecommendation[]>([]);
  const { switchEnvironment, remember } = useWorkspace();

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    async function load() {
      setStatus("loading");
      try {
        const data = await serviceProvider.getProvider().student.getRecommendations(4, controller.signal);
        if (isMounted) {
          setRecommendations(data.recommendations);
          setStatus("ready");
        }
      } catch (err: unknown) {
        if (isMounted && !(err instanceof DOMException && err.name === "AbortError")) {
          setStatus("error");
        }
      }
    }

    load();
    return () => {
      isMounted = false;
      controller.abort();
    };
  }, []);

  if (status === "loading") {
    return (
      <div className="mb-12 animate-pulse">
        <h2 className="text-xl font-serif text-ink tracking-tight mb-4">Up Next For You</h2>
        <div className="flex flex-col gap-4">
          <div className="h-32 w-full bg-ink/5 rounded-lg border border-ink/5"></div>
          <div className="h-32 w-full bg-ink/5 rounded-lg border border-ink/5"></div>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="mb-12">
        <h2 className="text-xl font-serif text-ink tracking-tight mb-4">Up Next For You</h2>
        <div className="p-6 bg-red-50/50 border border-red-100 rounded-lg">
          <h3 className="text-red-800 font-medium mb-2">Unable to load recommendations</h3>
          <p className="text-sm text-red-600/80">We couldn&apos;t connect to the learning intelligence service. Please try again later.</p>
        </div>
      </div>
    );
  }

  if (status === "ready" && recommendations.length === 0) {
    return (
      <div className="mb-12">
        <h2 className="text-xl font-serif text-ink tracking-tight mb-4">Up Next For You</h2>
        <div className="p-8 bg-white/50 border border-ink/5 rounded-lg text-center">
          <p className="text-ink/60">You&apos;re all caught up! No active recommendations at the moment.</p>
        </div>
      </div>
    );
  }

  const handleAction = (rec: LearnerRecommendation) => {
    remember("documents", { openedDocument: rec.resource_id });
    if (rec.action_type === "new_resource") {
      switchEnvironment("documents");
    } else {
      switchEnvironment("study");
    }
  };

  const getActionLabel = (type: string) => {
    if (type === "overdue_review") return "Review Overdue";
    if (type === "upcoming_review") return "Upcoming Review";
    if (type === "low_mastery") return "Improve Mastery";
    if (type === "new_resource") return "Start Learning";
    return "Continue";
  };

  if (status !== "ready") return null;

  return (
    <div className="mb-12">
      <h2 className="text-xl font-serif text-ink tracking-tight mb-4">Up Next For You</h2>
      <div className="flex flex-col gap-4">
        {recommendations.map((rec) => (
          <div key={`${rec.resource_id}-${rec.action_type}`} className="bg-white p-5 rounded-lg border border-ink/10 shadow-sm hover:border-ink/20 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold px-2 py-1 bg-ink/5 text-ink uppercase tracking-wider rounded-full">
                  {getActionLabel(rec.action_type)}
                </span>
              </div>
              <h3 className="font-medium text-ink mb-1 line-clamp-2" title={rec.resource_title}>
                {rec.resource_title}
              </h3>
              <p className="text-sm text-ink/60 line-clamp-2 mb-4">
                {rec.reason}
              </p>
            </div>
            <button
              onClick={() => handleAction(rec)}
              className="w-full py-2.5 bg-ink text-white text-sm font-medium rounded hover:bg-ink/90 transition-colors"
            >
              {rec.action_type === "new_resource" ? "Read Document" : "Start Session"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
