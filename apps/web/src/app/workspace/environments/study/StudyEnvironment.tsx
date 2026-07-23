"use client";

import { useStudy, StudyProvider } from "./StudyContext";
import { StudySurface, StudyEmptyState, StudyPerspective, StudyTimeline, StudyNavigator, StudyContextPanel } from "@/components/study";

import { useEffect } from "react";
import { serviceProvider } from "@/lib/providers";

function StudyEnvironmentBody() {
  const { state, dispatch } = useStudy();

  useEffect(() => {
    if (state.isStudying) {
      let isMounted = true;
      const controller = new AbortController();
      
      async function hydrate() {
        const currentRequestId = crypto.randomUUID();
        dispatch({ type: "START_HYDRATION", payload: { requestId: currentRequestId } });
        try {
          const data = await serviceProvider.getProvider().study.generateMaterial({
            topicId: "transformer-architecture", // Mock ID for now
            signal: controller.signal
          });
          if (isMounted) {
            dispatch({ type: "START_STUDY", payload: { status: "ready", data, error: null, requestId: currentRequestId } });
          }
        } catch (err: unknown) {
          if (isMounted) {
            if (err instanceof Error && err.name === "AbortError") return;
            dispatch({ type: "START_STUDY", payload: { status: "error", data: null, error: err as Error, requestId: currentRequestId } });
          }
        }
      }
      
      hydrate();
      return () => {
        isMounted = false;
        controller.abort();
      };
    }
    
  }, [state.isStudying, dispatch]);

  if (!state.isStudying) {
    return (
      <StudySurface>
        <StudyEmptyState />
      </StudySurface>
    );
  }

  if (state.material.status === "loading") {
    return (
      <StudySurface>
        <div className="flex-1 flex items-center justify-center h-full">
          <p className="text-secondary text-lg">Preparing study material...</p>
        </div>
      </StudySurface>
    );
  }

  if (state.material.status === "error") {
    return (
      <StudySurface>
        <div className="flex-1 flex items-center justify-center h-full">
          <p className="text-secondary text-lg">Unable to generate study material right now.</p>
        </div>
      </StudySurface>
    );
  }

  if (!state.material.data) return null;

  return (
    <StudySurface>
      <div className="flex w-full h-full">
        {/* Left Panel: The Learning Context */}
        <div className="w-64 flex-shrink-0 pt-12 pr-8 hidden md:block">
          <StudyContextPanel concept={state.material.data.concept} />
        </div>

        {/* Center Canvas: The Learning Content */}
        <div className="flex-1 flex flex-col pt-12 max-w-3xl relative">
          <StudyTimeline activeMode={state.activeMode} />
          
          <div className="flex-1 mt-12 pb-32">
            <StudyPerspective state={state} />
          </div>

          {/* Bottom Fixed Navigator */}
          <div className="fixed bottom-0 left-0 right-0 py-6 bg-gradient-to-t from-canvas via-canvas to-transparent flex justify-center pointer-events-none">
            <div className="w-full max-w-5xl px-6 lg:px-12 flex justify-end md:justify-center md:pl-64 pointer-events-auto">
              <StudyNavigator />
            </div>
          </div>
        </div>
      </div>
    </StudySurface>
  );
}

export function StudyEnvironment() {
  return (
    <StudyProvider>
      <StudyEnvironmentBody />
    </StudyProvider>
  );
}
