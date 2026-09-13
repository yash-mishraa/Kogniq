"use client";

import { useFlashcards, FlashcardsProvider } from "./FlashcardsContext";
import { 
  FlashcardsSurface, 
  FlashcardItem, 
  FlashcardsNavigator, 
  FlashcardsControls, 
  FlashcardsEmptyState 
} from "@/components/flashcards";

import { useEffect, useRef } from "react";
import { serviceProvider } from "@/lib/providers";
import { useWorkspace } from "../../WorkspaceContext";

function FlashcardsEnvironmentBody() {
  const { state, dispatch } = useFlashcards();
  const { memory } = useWorkspace();
  const documentId = memory.documents?.openedDocument;
  
  // Track previous documentId to know when it actually changes
  const previousDocumentId = useRef<string | undefined>(undefined);

  useEffect(() => {
    // Document changed or was cleared
    if (documentId !== previousDocumentId.current) {
      if (documentId) {
        dispatch({ type: "START_LOAD", payload: { requestId: crypto.randomUUID() } });
      } else {
        dispatch({ type: "RESET_ENVIRONMENT" });
      }
      previousDocumentId.current = documentId;
    }
  }, [documentId, dispatch]);

  useEffect(() => {
    if (state.status === "loading" && documentId) {
      let isMounted = true;
      const controller = new AbortController();
      const currentRequestId = state.requestId!;
      
      async function hydrate() {
        try {
          const cards = await serviceProvider.getProvider().flashcards.getFlashcards({
            documentId: documentId as string,
            signal: controller.signal
          });
          if (isMounted) {
            if (cards.length > 0) {
              dispatch({ type: "LOAD_SUCCESS", payload: { cards, requestId: currentRequestId } });
            } else {
              dispatch({ type: "LOAD_EMPTY", payload: { requestId: currentRequestId } });
            }
          }
        } catch (err: unknown) {
          if (isMounted) {
            if (err instanceof Error && err.name === "AbortError") return;
            dispatch({ type: "LOAD_ERROR", payload: { error: err as Error, requestId: currentRequestId } });
          }
        }
      }
      
      hydrate();
      return () => {
        isMounted = false;
        controller.abort();
      };
    }
    
  }, [state.status, state.requestId, dispatch, documentId]);

  const syncedResponses = useRef<Record<string, string>>({});
  useEffect(() => {
    if (!state.requestId || !documentId) return;
    
    for (const [cardId, difficulty] of Object.entries(state.responses)) {
      if (syncedResponses.current[cardId] !== difficulty) {
        syncedResponses.current[cardId] = difficulty;
        serviceProvider.getProvider().analytics.recordEvent({
          event_id: `${state.requestId}-${cardId}`,
          event_type: "flashcard_reviewed",
          document_id: documentId,
          data: { card_id: cardId, difficulty }
        }).catch(err => console.error("Failed to record analytics", err));
      }
    }
  }, [state.responses, state.requestId, documentId]);

  if (state.status === "idle" || state.status === "empty") {
    return (
      <FlashcardsSurface>
        <FlashcardsEmptyState />
      </FlashcardsSurface>
    );
  }

  if (state.status === "loading") {
    return (
      <FlashcardsSurface>
        <div className="flex-1 flex items-center justify-center h-full">
          <p className="text-secondary text-lg">Preparing flashcards...</p>
        </div>
      </FlashcardsSurface>
    );
  }

  if (state.status === "error") {
    return (
      <FlashcardsSurface>
        <div className="flex-1 flex items-center justify-center h-full text-center">
          <p className="text-red-500 text-lg">Unable to load flashcards right now.</p>
        </div>
      </FlashcardsSurface>
    );
  }

  const { cards, order, currentIndex, isFlipped } = state;
  const currentCard = cards[order[currentIndex]];

  if (!currentCard) return null;

  return (
    <FlashcardsSurface>
      <div className="flex flex-col w-full h-full max-w-3xl mx-auto pt-12 relative">
        <div className="flex-1 flex flex-col items-center justify-center pb-24">
          <FlashcardItem 
            card={currentCard} 
            isFlipped={isFlipped} 
            onFlip={() => dispatch({ type: "FLIP_CARD" })} 
          />
          <FlashcardsControls />
        </div>

        {/* Bottom Fixed Navigator */}
        <div className="fixed bottom-0 left-0 right-0 py-6 bg-gradient-to-t from-canvas via-canvas to-transparent flex justify-center pointer-events-none z-10">
          <div className="pointer-events-auto">
            <FlashcardsNavigator />
          </div>
        </div>
      </div>
    </FlashcardsSurface>
  );
}

export function FlashcardsEnvironment() {
  return (
    <FlashcardsProvider>
      <FlashcardsEnvironmentBody />
    </FlashcardsProvider>
  );
}
