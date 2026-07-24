import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // This repository coexists with unrelated local Node workspaces. Keep tracing
  // inside this application instead of letting Next walk up to a parent lockfile.
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*", // Proxy to Backend
      },
    ];
  },
};

export default nextConfig;
