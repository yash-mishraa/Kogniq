"use client";

import { StudioProvider } from "./StudioContext";
import { StudioEditor } from "@/components/studio/StudioEditor";
import { StudioSidebar } from "@/components/studio/StudioSidebar";

export function StudioEnvironment() {
  return (
    <StudioProvider>
      <div className="flex h-full w-full overflow-hidden">
        <StudioEditor />
        <StudioSidebar />
      </div>
    </StudioProvider>
  );
}
