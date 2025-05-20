export const config = {
  apiKey: import.meta.env.VITE_API_KEY,
  apiUrl: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8080',
  defaultProvider: 'gemini',
  providers: {
    gemini: {
      defaultModel: 'gemini-1.5-flash-latest' // Mis à jour vers un modèle plus récent et recommandé
    },
    mistral: {
      defaultModel: 'mistral-medium'
    },
    openrouter: {
      defaultModel: 'anthropic/claude-3-opus-20240229'
    }
  }
};