type FootlineItem = { label: string; href?: string };

const ITEMS: FootlineItem[] = [
  { label: "Privacy Policy" },
  { label: "Terms" },
  { label: "Documentation", href: "https://github.com/yash-mishraa/Kogniq#readme" },
  { label: "API", href: "https://github.com/yash-mishraa/Kogniq/tree/main/apps/api" },
  { label: "Status" },
  { label: "Security" },
  { label: "Built by Yash", href: "https://github.com/yash-mishraa" },
];

/**
 * Recovered from `1ee97ad:apps/web/src/components/experience/footer.tsx`.
 * Items without a published destination stay as quiet metadata instead of
 * pretending to be links; the visual line and type treatment are unchanged.
 */
export function Footline({ night = false }: { night?: boolean }) {
  const tone = night ? "text-[hsl(var(--night-muted))]" : "text-muted";
  const hover = night ? "hover:text-[hsl(var(--night-ink))]" : "hover:text-ink";
  return (
    <footer className={`flex flex-wrap gap-x-3 gap-y-1 font-mono text-[10px] leading-5 ${tone}`}>
      {ITEMS.map((item) =>
        item.href ? (
          <a
            key={item.label}
            href={item.href}
            target="_blank"
            rel="noreferrer"
            className={`transition-colors ${hover}`}
          >
            {item.label}
          </a>
        ) : (
          <span key={item.label} title="Not published in this build">
            {item.label}
          </span>
        ),
      )}
    </footer>
  );
}
