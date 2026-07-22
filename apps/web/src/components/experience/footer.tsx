export function Footline({ night = false }: { night?: boolean }) {
  const tone = night ? "text-[hsl(var(--night-muted))]" : "text-muted";
  const hover = night ? "hover:text-[hsl(var(--night-ink))]" : "hover:text-ink";
  return <footer className={`flex flex-wrap gap-x-3 gap-y-1 font-mono text-[10px] leading-5 ${tone}`}><a href="#privacy" className={`transition-colors ${hover}`}>Privacy Policy</a><a href="#terms" className={`transition-colors ${hover}`}>Terms</a><a href="#documentation" className={`transition-colors ${hover}`}>Documentation</a><a href="#api" className={`transition-colors ${hover}`}>API</a><a href="#status" className={`transition-colors ${hover}`}>Status</a><a href="#security" className={`transition-colors ${hover}`}>Security</a><a href="https://github.com/yash-mishraa" target="_blank" rel="noreferrer" className={`transition-colors ${hover}`}>Built by Yash</a></footer>;
}
