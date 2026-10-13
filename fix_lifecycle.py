import re

with open('apps/web/src/components/documents/DocumentLifecycle.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''  return (
    <div className="flex flex-col gap-1.5 w-full">
      <div className="flex items-center gap-1.5 flex-wrap">
        {LIFECYCLE_STAGES.map((stage, i) => {
          const isPast = i < currentIndex;
          const isActive = i === currentIndex;

          return (
            <div key={stage.status} className="flex items-center gap-1.5">
              <span
                className={	ext-[11px] uppercase tracking-widest font-medium transition-colors duration-300 }
              >
                {stage.label}
                {isActive && status !== "Ready" && <span className="ml-1 inline-block animate-pulse">...</span>}
              </span>
              {i < LIFECYCLE_STAGES.length - 1 && (
                <span className={	ext-[10px] }>
                  /
                </span>
              )}
            </div>
          );
        })}
      </div>
      {status !== "Ready" && (
        <div className="w-full h-[2px] bg-gray-100 overflow-hidden relative">
          <div 
            className="h-full bg-accent transition-all duration-700 ease-in-out relative"
            style={{ width: ${Math.max(2, (currentIndex / (LIFECYCLE_STAGES.length - 1)) * 100)}% }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse" />
          </div>
        </div>
      )}
    </div>
  );'''

content = re.sub(r'  return \(\n    <div className="flex items-center gap-1\.5 flex-wrap">.*?    </div>\n  \);', replacement, content, flags=re.DOTALL)

with open('apps/web/src/components/documents/DocumentLifecycle.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
