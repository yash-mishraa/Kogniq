"use client";

import { useStudy, StudyProvider } from "./StudyContext";
import { StudySurface, StudyEmptyState, StudyPerspective, StudyTimeline, StudyNavigator, StudyContextPanel } from "@/components/study";

function StudyEnvironmentBody() {
  const { state } = useStudy();

  if (!state.isStudying || !state.material) {
    return (
      <StudySurface>
        <StudyEmptyState />
      </StudySurface>
    );
  }

  return (
    <StudySurface>
      <div className="flex w-full h-full">
        {/* Left Panel: The Learning Context */}
        <div className="w-64 flex-shrink-0 pt-12 pr-8 hidden md:block">
          <StudyContextPanel concept={state.material.concept} />
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
