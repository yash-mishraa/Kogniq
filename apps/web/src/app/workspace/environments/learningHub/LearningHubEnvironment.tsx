"use client";

import { useEffect, useMemo, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLearningHub, LearningHubProvider } from "./LearningHubContext";
import { serviceProvider } from "@/lib/providers";
import type { ResourceChunk } from "@/lib/services/interfaces/IResourceService";
import { RecommendationsList } from "./RecommendationsList";

function ResourceList() {
  const { state, dispatch } = useLearningHub();
  const { resources, activeResourceId } = state;

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    async function fetchResources() {
      if (resources.data !== null && resources.status !== "error") return;
      
      dispatch({ type: "LOAD_RESOURCES_START" });
      try {
        const data = await serviceProvider.getProvider().resources.listResources(resources.limit, resources.offset, controller.signal);
        if (isMounted) {
          dispatch({ type: "LOAD_RESOURCES_SUCCESS", payload: { data, offset: resources.offset, hasMore: data.length === resources.limit } });
        }
      } catch (err: unknown) {
        if (isMounted && !(err instanceof DOMException && err.name === "AbortError")) {
          dispatch({ type: "LOAD_RESOURCES_ERROR", payload: err as Error });
        }
      }
    }

    fetchResources();
    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [dispatch, resources.limit, resources.offset, resources.data, resources.status]);

  if (resources.status === "loading" && !resources.data) {
    return (
      <div className="flex-1 flex items-center justify-center pt-24">
        <p className="text-secondary text-lg">Loading resources...</p>
      </div>
    );
  }

  if (resources.status === "error" && !resources.data) {
    return (
      <div className="flex-1 flex items-center justify-center pt-24">
        <p className="text-red-500 text-lg">Failed to load resources.</p>
      </div>
    );
  }

  if (resources.data && resources.data.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center pt-32 space-y-4">
        <h3 className="text-2xl font-serif text-ink">No Resources Found</h3>
        <p className="text-ink/60">Upload documents to generate content intelligence resources.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-shrink-0 overflow-y-auto transition-all w-full pt-12 px-6 lg:px-12 bg-transparent pb-24">
      <RecommendationsList />
      <h2 className="text-xl font-serif text-ink tracking-tight mb-8">Content Intelligence Hub</h2>
      <ul className="flex flex-col gap-2">
        {resources.data?.map(resource => (
          <li key={resource.id}>
            <button
              onClick={() => {
                console.log("BUTTON CLICKED FOR RESOURCE:", resource.id, "CURRENT ACTIVE:", activeResourceId);
                dispatch({ type: "SELECT_RESOURCE", payload: activeResourceId === resource.id ? null : resource.id });
              }}
              className={`w-full text-left px-6 py-5 rounded-lg border transition-all ${
                activeResourceId === resource.id
                  ? "bg-white border-ink/20 shadow-sm"
                  : "bg-white/40 border-ink/5 hover:bg-white/80 hover:border-ink/10"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-ink text-lg mb-1">{resource.title}</h3>
                  <p className="text-sm text-ink/60 capitalize">{resource.resource_type}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full uppercase tracking-wider ${
                  resource.status === "completed" ? "bg-emerald-100 text-emerald-800" :
                  resource.status === "failed" ? "bg-red-100 text-red-800" :
                  "bg-amber-100 text-amber-800"
                }`}>
                  {resource.status}
                </span>
              </div>
            </button>
          </li>
        ))}
      </ul>
      
      {resources.hasMore && (
        <button 
          className="mt-8 text-sm text-ink/60 hover:text-ink transition-colors"
          onClick={() => {
            // we would implement pagination here by incrementing offset and loading more
          }}
        >
          Load more...
        </button>
      )}
    </div>
  );
}

export function TrackedChunk({ chunk, onTracked }: { chunk: ResourceChunk; onTracked: (chunkId: string) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const tracked = useRef(false);

  useEffect(() => {
    if (tracked.current || !ref.current) return;

    let timer: NodeJS.Timeout | null = null;

    const observer = new IntersectionObserver(([entry]) => {
      // Explicit 0.5 ratio validation to prevent browser rounding inaccuracies
      if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
        if (!timer) {
          timer = setTimeout(() => {
            tracked.current = true;
            onTracked(chunk.id);
            observer.disconnect();
          }, 1500);
        }
      } else {
        if (timer) {
          clearTimeout(timer);
          timer = null;
        }
      }
    }, { threshold: 0.5 }); 

    observer.observe(ref.current);

    return () => {
      observer.disconnect();
      if (timer) clearTimeout(timer);
    };
  }, [chunk.id, onTracked]);

  return (
    <div ref={ref} className="text-ink/80 leading-relaxed bg-ink/[0.02] p-4 rounded-r-lg">
      {chunk.text}
    </div>
  );
}

function ResourceDetailView() {
  const { state, dispatch } = useLearningHub();
  const { activeResourceId, activeResourceDetails, resources } = state;
  const activeResource = useMemo(() => resources.data?.find(r => r.id === activeResourceId), [resources.data, activeResourceId]);
  const trackedResources = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!activeResourceId) return;
    if (trackedResources.current.has(activeResourceId)) return;
    
    const recordView = async () => {
      trackedResources.current.add(activeResourceId);
      try {
        await serviceProvider.getProvider().analytics.recordEventsBatch([{
          event_id: crypto.randomUUID(),
          event_type: "resource_viewed",
          resource_id: activeResourceId,
          data: {},
          idempotency_key: `view_${activeResourceId}`
        }]);
      } catch (err) {
        trackedResources.current.delete(activeResourceId);
        console.error("Failed to record resource view analytics", err);
      }
    };
    
    // Fire and forget to not block UI
    recordView();
  }, [activeResourceId]);

  useEffect(() => {
    if (!activeResourceId) return;
    
    let isMounted = true;
    const controller = new AbortController();

    async function fetchDetails() {
      dispatch({ type: "LOAD_RESOURCE_DETAILS_START" });
      try {
        const [sections, chunks, statistics, progress] = await Promise.all([
          serviceProvider.getProvider().resources.getResourceSections(activeResourceId!, controller.signal),
          serviceProvider.getProvider().resources.getResourceChunks(activeResourceId!, 100, 0, controller.signal),
          serviceProvider.getProvider().resources.getResourceStatistics(activeResourceId!, controller.signal),
          serviceProvider.getProvider().analytics.getResourceProgress(activeResourceId!, controller.signal).catch(e => {
            console.error("Failed to load progress", e);
            return null;
          }),
        ]);
        
        if (isMounted) {
          dispatch({ 
            type: "LOAD_RESOURCE_DETAILS_SUCCESS", 
            payload: { 
              sections, 
              chunks, 
              statistics,
              progress,
              hasMoreChunks: chunks.length === 100,
              chunkOffset: 0
            } 
          });
        }
      } catch (err: unknown) {
        if (isMounted && !(err instanceof DOMException && err.name === "AbortError")) {
          dispatch({ type: "LOAD_RESOURCE_DETAILS_ERROR", payload: err as Error });
        }
      }
    }

    fetchDetails();
    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [activeResourceId, dispatch]);

  const loadMoreChunks = async () => {
    if (!activeResourceId || activeResourceDetails.isLoadingMoreChunks || !activeResourceDetails.hasMoreChunks) return;
    
    dispatch({ type: "LOAD_MORE_CHUNKS_START" });
    const nextOffset = activeResourceDetails.chunkOffset + activeResourceDetails.chunkLimit;
    
    try {
      const chunks = await serviceProvider.getProvider().resources.getResourceChunks(
        activeResourceId,
        activeResourceDetails.chunkLimit,
        nextOffset
      );
      dispatch({
        type: "LOAD_MORE_CHUNKS_SUCCESS",
        payload: {
          chunks,
          hasMoreChunks: chunks.length === activeResourceDetails.chunkLimit,
          chunkOffset: nextOffset
        }
      });
    } catch (err: unknown) {
      dispatch({ type: "LOAD_MORE_CHUNKS_ERROR", payload: err as Error });
    }
  };

  const handleChunkTracked = useCallback((chunkId: string, sectionId: string | null) => {
    if (!activeResourceId) return;
    const currentResourceId = activeResourceId;
    
    // Create the event and instantly push to AnalyticsDeliveryQueue
    serviceProvider.getProvider().analytics.enqueueBatchEvent({
      event_id: crypto.randomUUID(),
      event_type: "chunk_viewed",
      resource_id: currentResourceId,
      section_id: sectionId,
      chunk_id: chunkId,
      data: {},
      idempotency_key: `chunk_view_${currentResourceId}_${chunkId}`
    });
    
    // Refresh progress after a delay
    setTimeout(() => {
      serviceProvider.getProvider().analytics.getResourceProgress(currentResourceId)
        .then(progress => {
          if (activeResourceId === currentResourceId) {
            dispatch({ type: "UPDATE_PROGRESS", payload: progress });
          }
        }).catch(console.error);
    }, 4000);
  }, [activeResourceId, dispatch]);

  if (!activeResource) return null;

  return (
    <motion.article
      layout
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="flex-1 flex flex-col bg-white overflow-y-auto px-12 lg:px-24 py-16"
      style={{ boxShadow: "-12px 0 32px rgba(0, 0, 0, 0.02)" }}
    >
      <div className="max-w-[800px] mx-auto w-full">
        <header className="mb-12">
          <h1 className="text-4xl font-serif text-ink mb-4">{activeResource.title}</h1>
          <div className="flex flex-wrap gap-4 text-sm text-ink/60">
            <span>{new Date(activeResource.created_at).toLocaleDateString()}</span>
            <span>&bull;</span>
            <span className="uppercase tracking-wider">{activeResource.resource_type}</span>
            <span>&bull;</span>
            <span className="capitalize">{activeResource.status}</span>
          </div>
        </header>

        {activeResourceDetails.status === "loading" && (
          <p className="text-ink/60 animate-pulse">Loading intelligence details...</p>
        )}

        {activeResourceDetails.status === "error" && (
          <p className="text-red-500">Failed to load resource details.</p>
        )}

        {activeResourceDetails.status === "ready" && (
          <div className="space-y-12">
            {activeResourceDetails.statistics && (
              <section className="grid grid-cols-3 gap-6">
                <div className="bg-ink/5 p-6 rounded-xl">
                  <p className="text-sm uppercase tracking-widest text-ink/60 mb-2">Sections</p>
                  <p className="text-3xl font-serif text-ink">{activeResourceDetails.statistics.section_count}</p>
                </div>
                <div className="bg-ink/5 p-6 rounded-xl">
                  <p className="text-sm uppercase tracking-widest text-ink/60 mb-2">Chunks</p>
                  <p className="text-3xl font-serif text-ink">{activeResourceDetails.statistics.chunk_count}</p>
                </div>
                <div className="bg-ink/5 p-6 rounded-xl">
                  <p className="text-sm uppercase tracking-widest text-ink/60 mb-2">Tokens</p>
                  <p className="text-3xl font-serif text-ink">{activeResourceDetails.statistics.total_tokens.toLocaleString()}</p>
                </div>
              </section>
            )}

            {activeResourceDetails.progress && (
              <section className="bg-white border border-ink/10 rounded-xl p-6 shadow-sm">
                <h3 className="text-lg font-medium text-ink mb-4">Reading Progress</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-ink/60">Sections Viewed</span>
                      <span className="font-medium text-ink">{activeResourceDetails.progress.viewed_sections} / {activeResourceDetails.progress.total_sections}</span>
                    </div>
                    <div className="w-full bg-ink/5 rounded-full h-2">
                      <div className="bg-emerald-500 h-2 rounded-full transition-all duration-500" style={{ width: `${(activeResourceDetails.progress.total_sections > 0 ? (activeResourceDetails.progress.viewed_sections / activeResourceDetails.progress.total_sections) * 100 : 0)}%` }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-ink/60">Chunks Viewed</span>
                      <span className="font-medium text-ink">{activeResourceDetails.progress.viewed_chunks} / {activeResourceDetails.progress.total_chunks}</span>
                    </div>
                    <div className="w-full bg-ink/5 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full transition-all duration-500" style={{ width: `${(activeResourceDetails.progress.total_chunks > 0 ? (activeResourceDetails.progress.viewed_chunks / activeResourceDetails.progress.total_chunks) * 100 : 0)}%` }}></div>
                    </div>
                  </div>
                </div>
              </section>
            )}

            <section>
              <h2 className="text-2xl font-serif text-ink mb-6 border-b border-ink/10 pb-4">Extracted Content</h2>
              
              {activeResourceDetails.sections.length === 0 && (
                <p className="text-ink/60 italic">No structured sections were extracted for this resource.</p>
              )}

              <div className="space-y-8">
                {activeResourceDetails.sections.sort((a, b) => a.order - b.order).map(section => {
                  const sectionChunks = activeResourceDetails.chunks
                    .filter(c => c.section_id === section.id)
                    .sort((a, b) => a.order - b.order);

                  return (
                    <div key={section.id} className="space-y-4">
                      <h3 className="text-xl font-medium text-ink sticky top-0 bg-white py-2 z-10">{section.title}</h3>
                      {sectionChunks.length === 0 ? (
                        <p className="text-sm text-ink/40 italic pl-4">No content chunks associated with this section.</p>
                      ) : (
                        <div className="space-y-3 pl-4 border-l-2 border-ink/5">
                          {sectionChunks.map(chunk => (
                            <TrackedChunk 
                              key={chunk.id} 
                              chunk={chunk} 
                              onTracked={(chunkId) => handleChunkTracked(chunkId, section.id)} 
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              
              {activeResourceDetails.hasMoreChunks && (
                <div className="mt-8 flex justify-center">
                  <button
                    onClick={loadMoreChunks}
                    disabled={activeResourceDetails.isLoadingMoreChunks}
                    className="px-6 py-2 bg-ink/5 hover:bg-ink/10 text-ink rounded-full transition-colors disabled:opacity-50"
                  >
                    {activeResourceDetails.isLoadingMoreChunks ? "Loading more..." : "Load more chunks"}
                  </button>
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </motion.article>
  );
}

function LearningHubEnvironmentBody() {
  const { state } = useLearningHub();
  const hasActiveResource = state.activeResourceId !== null;

  return (
    <div className="flex w-full h-full relative overflow-hidden bg-[hsl(var(--sand))]">
      <div 
        className="flex-shrink-0 h-full overflow-hidden transition-all duration-500 flex flex-col relative z-10"
        style={{ 
          width: hasActiveResource ? "420px" : "100%",
          maxWidth: hasActiveResource ? "420px" : "800px",
          margin: hasActiveResource ? "0" : "0 auto"
        }}
      >
        <ResourceList />
      </div>
      <AnimatePresence>
        {hasActiveResource && <ResourceDetailView />}
      </AnimatePresence>
    </div>
  );
}

export function LearningHubEnvironment() {
  return (
    <LearningHubProvider>
      <LearningHubEnvironmentBody />
    </LearningHubProvider>
  );
}
