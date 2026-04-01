import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Same-origin in dev → avoids CORS when Vite uses 5174, 5175, etc.
      "/api/voice": {
        target: "http://localhost:3001",
        changeOrigin: true,
      },
    },
  },
});
