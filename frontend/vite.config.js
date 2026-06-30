import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',
  build: {
    outDir: '../static_dist',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/profile': 'http://127.0.0.1:8000',
      '/resume': 'http://127.0.0.1:8000',
    },
  },
})
