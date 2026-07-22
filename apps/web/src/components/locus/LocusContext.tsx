"use client";

import { createContext, useContext } from "react";

export interface LocusContextValue { placeholder: string; environmentTitle: string; }
export const LocusContext = createContext<LocusContextValue | null>(null);
export function useLocusContext() { const value = useContext(LocusContext); if (!value) throw new Error("useLocusContext must be used inside LocusContext."); return value; }
