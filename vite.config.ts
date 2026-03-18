import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Keep symlinked packages resolved from workspace node_modules.
  // This avoids jumping to sibling repo node_modules for transitive deps.
  resolve: {
    preserveSymlinks: true,
    alias: {
      '@lepton/core': path.resolve(__dirname, 'node_modules/@lepton/core'),
    },
  },
  // Keep linked @lepton/core out of prebundle to avoid stale cache after rebuilds.
  // CommonJS deps used inside linked packages must be prebundled for named imports.
  optimizeDeps: {
    force: true,
    exclude: ['@lepton/core'],
    include: ['@lepton/api-client', 'react-dom/client'],
  },
})
