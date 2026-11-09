import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api/vehicles": {
        target: "http://localhost:8001",
        rewrite: (p) => p.replace("/api/vehicles", ""),
      },
      "/api/tickets": {
        target: "http://localhost:8002",
        rewrite: (p) => p.replace("/api/tickets", ""),
      },
    },
  },
});
