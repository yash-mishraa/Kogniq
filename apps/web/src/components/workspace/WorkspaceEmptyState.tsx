"use client";

import type { EnvironmentMetadata } from "@/app/workspace/WorkspaceTypes";
import { Locus, type LocusSuggestion } from "@/components/locus";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";

export function WorkspaceEmptyState({ environment }: { environment: EnvironmentMetadata }) { const { remember } = useWorkspace(); const suggestions: readonly LocusSuggestion[] = [{ label: environment.title, detail: environment.description }, { label: "Change perspective", detail: "choose another environment" }]; return <section aria-label={`${environment.title} starting point`} className="mx-auto flex w-full max-w-6xl flex-1 items-start pt-4"><Locus environmentTitle={environment.title} placeholder={environment.locusPlaceholder} suggestions={suggestions} autoFocus onSelect={(suggestion) => remember(environment.id, { selectedContext: suggestion.label, focusTarget: "locus" })} /></section>; }
