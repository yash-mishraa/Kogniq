import type { NextConfig } from "next";
import path from "node:path";

const backendUrl = (
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // This repository coexists with unrelated local Node workspaces. Keep tracing
  // inside this application instead of letting Next walk up to a parent lockfile.
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`, // Proxy to Backend (local or remote)
      },
    ];
  },
};

export default nextConfig;
