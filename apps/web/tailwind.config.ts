import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      colors: {
        canvas: "hsl(var(--canvas))",
        surface: "hsl(var(--surface))",
        raised: "hsl(var(--raised))",
        ink: "hsl(var(--ink))",
        muted: "hsl(var(--muted))",
        line: "hsl(var(--line))",
        accent: "hsl(var(--accent))",
        "accent-ink": "hsl(var(--accent-ink))",
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        danger: "hsl(var(--danger))",
      },
      borderRadius: { xs: "var(--radius-xs)", sm: "var(--radius-sm)", md: "var(--radius-md)" },
      boxShadow: { panel: "var(--shadow-panel)", overlay: "var(--shadow-overlay)" },
    },
  },
  plugins: [],
};

export default config;
