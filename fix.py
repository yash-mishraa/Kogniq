
with open('apps/web/src/app/workspace/environments/learningHub/LearningHubEnvironment.tsx', encoding='utf-8') as f:
    code = f.read()

prefix_end = code.find('    } catch (err: unknown) {')
chunk_end = code.find('  };', prefix_end) + 4
suffix_start = code.find('function LearningHubEnvironmentBody() {')

new_middle = '''
  const chunkQueue = useRef<{chunkId: string, sectionId: string | null, resourceId: string}[]>([]);
  const batchTimer = useRef<NodeJS.Timeout | null>(null);

  const handleChunkTracked = useCallback((chunkId: string, sectionId: string | null) => {
    if (!activeResourceId) return;
    const currentResourceId = activeResourceId;
    chunkQueue.current.push({ chunkId, sectionId, resourceId: currentResourceId });
    
    if (!batchTimer.current) {
      batchTimer.current = setTimeout(async () => {
        const eventsToTrack = [...chunkQueue.current];
        chunkQueue.current = [];
        batchTimer.current = null;
        
        if (eventsToTrack.length === 0) return;
        
        try {
          const events = eventsToTrack.map(ev => ({
            event_id: crypto.randomUUID(),
            event_type: "chunk_viewed",
            resource_id: ev.resourceId,
            section_id: ev.sectionId,
            chunk_id: ev.chunkId,
            data: {},
            idempotency_key: chunk_view__
          }));
          await serviceProvider.getProvider().analytics.recordEventsBatch(events);
          
          if (activeResourceId === currentResourceId) {
            const progress = await serviceProvider.getProvider().analytics.getResourceProgress(currentResourceId);
            dispatch({ type: "UPDATE_PROGRESS", payload: progress });
          }
        } catch (err) {
          console.error("Failed to track chunk view", err);
        }
      }, 3000);
    }
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
                      <div className="bg-emerald-500 h-2 rounded-full transition-all duration-500" style={{ width: ${(activeResourceDetails.progress.total_sections > 0 ? (activeResourceDetails.progress.viewed_sections / activeResourceDetails.progress.total_sections) * 100 : 0)}% }}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-ink/60">Chunks Viewed</span>
                      <span className="font-medium text-ink">{activeResourceDetails.progress.viewed_chunks} / {activeResourceDetails.progress.total_chunks}</span>
                    </div>
                    <div className="w-full bg-ink/5 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full transition-all duration-500" style={{ width: ${(activeResourceDetails.progress.total_chunks > 0 ? (activeResourceDetails.progress.viewed_chunks / activeResourceDetails.progress.total_chunks) * 100 : 0)}% }}></div>
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
'''
with open('apps/web/src/app/workspace/environments/learningHub/LearningHubEnvironment.tsx', 'w', encoding='utf-8') as f:
    f.write(code[:chunk_end] + '\n' + new_middle + '\n' + code[suffix_start:])
