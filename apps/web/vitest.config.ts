import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

const directory = path.dirname(fileURLToPath(import.meta.url));
export default defineConfig({ plugins: [react()], test: { environment: "jsdom", setupFiles: ["./src/test/setup.ts"] }, resolve: { alias: { "@": path.join(directory, "src") } } });
