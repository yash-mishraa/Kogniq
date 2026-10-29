import type { Metadata, Viewport } from "next";
import "@fontsource-variable/instrument-sans";
import { GeistMono } from "geist/font/mono";
import "katex/dist/katex.min.css";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = { title: "Kogniq", description: "An instrument for thinking" };

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" suppressHydrationWarning><body className={GeistMono.variable}><Providers>{children}</Providers></body></html>;
}
