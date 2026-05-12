import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],

  server: {
    host: true, // required for docker (0.0.0.0)
    port: 5173,
    watch: {
      usePolling: true, // required for Windows + Docker
    },
    strictPort: true,
    allowedHosts: true,
  },
});
