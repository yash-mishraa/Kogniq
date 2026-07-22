import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // This repository coexists with unrelated local Node workspaces. Keep tracing
  // inside this application instead of letting Next walk up to a parent lockfile.
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
