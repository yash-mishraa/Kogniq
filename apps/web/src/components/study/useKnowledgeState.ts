import { useState, useEffect } from "react";
import { serviceProvider } from "@/lib/providers";
import type { KnowledgeState } from "@/lib/services/interfaces/IStudentService";

export function useKnowledgeState(resourceId: string | null) {
  const [knowledgeState, setKnowledgeState] = useState<KnowledgeState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!resourceId) {
      setKnowledgeState(null);
      setError(null);
      return;
    }

    const abortController = new AbortController();

    async function fetchKnowledgeState() {
      setIsLoading(true);
      setError(null);
      try {
        const state = await serviceProvider.getProvider().student.getKnowledgeState(
          resourceId!,
          abortController.signal
        );
        setKnowledgeState(state);
      } catch (err: any) {
        if (err.name === "AbortError" || err.code === "ERR_CANCELED") {
          return;
        }
        // If 404, we just leave it as null
        if (err.response?.status === 404 || err.status === 404) {
          setKnowledgeState(null);
        } else {
          setError(err instanceof Error ? err : new Error(err?.message || "Unknown error"));
          setKnowledgeState(null);
        }
      } finally {
        setIsLoading(false);
      }
    }

    fetchKnowledgeState();

    return () => {
      abortController.abort();
    };
  }, [resourceId]);

  return { knowledgeState, isLoading, error };
}
