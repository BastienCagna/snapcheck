import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Resolve package-style imports to the symlinked generated API sources.
      '@lepton/api-client': path.resolve(__dirname, 'src/lepton/api-client'),
    },
  },
})
