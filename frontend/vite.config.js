import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Where the dev server forwards API calls (override with VITE_DEV_API_TARGET if port 8000 is taken).
const apiTarget = process.env.VITE_DEV_API_TARGET || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api/v1/search': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/api/v1/recommendations': {
        target: 'http://localhost:8002',
        changeOrigin: true,
      },
      '/api': {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
});

