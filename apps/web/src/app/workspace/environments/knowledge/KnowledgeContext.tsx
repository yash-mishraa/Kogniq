"use client";

import { createContext, useContext, useReducer, type ReactNode } from "react";
import type { KnowledgeState, KnowledgeAction } from "./KnowledgeState";
import { MOCK_TRANSFORMER_GRAPH } from "./KnowledgeState";

const initialState: KnowledgeState = {
  graph: MOCK_TRANSFORMER_GRAPH,
  activeConceptId: null,
  trail: [],
};

function knowledgeReducer(state: KnowledgeState, action: KnowledgeAction): KnowledgeState {
  switch (action.type) {
    case "SET_GRAPH":
      return { ...state, graph: action.payload, activeConceptId: null, trail: [] };
    case "SELECT_CONCEPT": {
      const newConceptId = action.payload;
      
      // If deselecting, or selecting same
      if (newConceptId === null || newConceptId === state.activeConceptId) {
        return { ...state, activeConceptId: null, trail: [] }; // Reset trail on deselect
      }

      // If selecting a new concept, add to trail
      const newTrail = [...state.trail];
      if (!newTrail.includes(newConceptId)) {
        newTrail.push(newConceptId);
      } else {
        // If it's already in the trail, maybe we truncate the trail up to this point?
        // For now, let's just truncate up to the clicked concept to allow "going back" up the trail
        const idx = newTrail.indexOf(newConceptId);
        newTrail.length = idx + 1;
      }

      return {
        ...state,
        activeConceptId: newConceptId,
        trail: newTrail,
      };
    }
    default:
      return state;
  }
}

const KnowledgeContext = createContext<{
  state: KnowledgeState;
  dispatch: React.Dispatch<KnowledgeAction>;
} | null>(null);

export function KnowledgeProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(knowledgeReducer, initialState);
  return <KnowledgeContext.Provider value={{ state, dispatch }}>{children}</KnowledgeContext.Provider>;
}

export function useKnowledge() {
  const context = useContext(KnowledgeContext);
  if (!context) throw new Error("useKnowledge must be used within KnowledgeProvider");
  return context;
}
