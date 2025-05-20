import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import path from 'path' // Importer le module path de Node.js

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'), // Définir l'alias @ pour pointer vers src/
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080', // Utiliser le port 8080 pour le backend FastAPI
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '') // CORRIGÉ: Supprimer /api du chemin
        // secure: false, // Décommentez si votre backend est en HTTP et non HTTPS pendant le développement
      }
    }
  }
})