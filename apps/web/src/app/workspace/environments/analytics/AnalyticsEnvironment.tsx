"use client";

import { useEffect } from "react";
import { AnalyticsProvider, useAnalytics } from "./AnalyticsContext";
import { serviceProvider } from "@/lib/providers";

function AnalyticsSurface({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-full h-full flex flex-col bg-canvas text-primary p-8 overflow-y-auto">
      <h1 className="text-3xl font-bold mb-8">Learning Analytics</h1>
      {children}
    </div>
  );
}

function AnalyticsEnvironmentBody() {
  const { state, dispatch } = useAnalytics();

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    dispatch({ type: "START_LOAD" });
    serviceProvider.getProvider().analytics.getMetrics(state.timeRange, { signal: controller.signal })
      .then((metrics) => {
        if (isMounted) dispatch({ type: "LOAD_SUCCESS", payload: metrics });
      })
      .catch((error) => {
        if (isMounted && error.name !== "AbortError") {
          dispatch({ type: "LOAD_ERROR", payload: error });
        }
      });

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [state.timeRange, dispatch]);

  return (
    <AnalyticsSurface>
      <div className="flex space-x-4 mb-8">
        {(["7d", "30d", "all"] as const).map((range) => (
          <button
            key={range}
            onClick={() => dispatch({ type: "SET_TIME_RANGE", payload: range })}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              state.timeRange === range
                ? "bg-accent text-accent-foreground"
                : "bg-surface text-secondary hover:bg-surface-hover hover:text-primary"
            }`}
          >
            {range === "7d" ? "Last 7 Days" : range === "30d" ? "Last 30 Days" : "All Time"}
          </button>
        ))}
      </div>

      {state.status === "loading" && (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-secondary text-lg animate-pulse">Loading analytics...</p>
        </div>
      )}

      {state.status === "error" && (
        <div className="flex-1 flex flex-col items-center justify-center text-center">
          <p className="text-red-500 mb-2">Unable to load analytics.</p>
          <p className="text-secondary text-sm">{state.error?.message}</p>
        </div>
      )}

      {state.status === "ready" && state.metrics && (
        state.metrics.quizzes_completed === 0 && state.metrics.flashcards_reviewed === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center border-2 border-dashed border-border rounded-xl p-12">
            <h3 className="text-xl font-semibold mb-2">No learning activity found yet</h3>
            <p className="text-secondary">Complete a quiz or review flashcards to see your statistics here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-surface rounded-xl p-6 border border-border shadow-sm">
              <h3 className="text-sm font-medium text-secondary mb-2">Quizzes Completed</h3>
              <p className="text-4xl font-bold">{state.metrics.quizzes_completed}</p>
            </div>
            
            <div className="bg-surface rounded-xl p-6 border border-border shadow-sm">
              <h3 className="text-sm font-medium text-secondary mb-2">Average Quiz Accuracy</h3>
              <p className="text-4xl font-bold">
                {Math.round(state.metrics.average_quiz_accuracy * 100)}%
              </p>
              <div className="w-full bg-border h-2 mt-4 rounded-full overflow-hidden">
                <div 
                  className="bg-accent h-full rounded-full" 
                  style={{ width: `${Math.round(state.metrics.average_quiz_accuracy * 100)}%` }} 
                />
              </div>
            </div>

            <div className="bg-surface rounded-xl p-6 border border-border shadow-sm">
              <h3 className="text-sm font-medium text-secondary mb-2">Flashcards Reviewed</h3>
              <p className="text-4xl font-bold">{state.metrics.flashcards_reviewed}</p>
            </div>
          </div>
        )
      )}
    </AnalyticsSurface>
  );
}

export function AnalyticsEnvironment() {
  return (
    <AnalyticsProvider>
      <AnalyticsEnvironmentBody />
    </AnalyticsProvider>
  );
}
