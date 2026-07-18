/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
    css: false,
    coverage: {
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/__tests__/**', 'src/test-setup.ts', 'src/vite-env.d.ts'],
      reporter: ['text', 'lcov'],
    },
  },
})
