import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/admin': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/memory-game': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/abecedario': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/paseo': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/train': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/users': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
