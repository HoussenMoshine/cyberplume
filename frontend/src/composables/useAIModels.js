import { ref, reactive } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

// Données statiques (peuvent rester ici ou être importées si définies ailleurs)
const providerInfo = {
  gemini: { title: 'Google Gemini', description: 'Modèle avancé de Google' },
  mistral: { title: 'Mistral AI', description: 'Modèles open-source performants' },
  openrouter: { title: 'OpenRouter', description: 'Accès unifié à plusieurs modèles' },
};

// MODIFIÉ: Ajout des nouveaux styles et EXPORTATION directe
export const writingStyles = [
  { text: 'Normal', value: 'normal' }, { text: 'Formel', value: 'formel' },
  { text: 'Créatif', value: 'creatif' }, { text: 'Technique', value: 'technique' },
  { text: 'Humoristique', value: 'humoristique' }, { text: 'Poétique', value: 'poetique' },
  { text: 'Sarcastique', value: 'sarcastique' }, // NOUVEAU
  { text: 'Adulte', value: 'adulte' },
  { text: 'Langage cru', value: 'langage_cru' }, // NOUVEAU
];


export function useAIModels(showSnackbar) {
  const providers = ref(Object.entries(providerInfo).map(([value, info]) => ({ ...info, value })));
  const availableModels = reactive({}); // { provider: [models] }
  const loadingModels = ref(false);
  const errorLoadingModels = ref(false);

  const fetchModels = async (provider) => {
    if (!provider || availableModels[provider]?.length > 0) { // Ne recharge pas si déjà chargé
        // Si déjà chargé, s'assurer que l'état de chargement est correct
        const isLoading = loadingModels.value;
        // Ne pas remettre loadingModels à false ici, car un autre fetch pourrait être en cours pour un autre provider
        // loadingModels.value = false;
        return !isLoading; // Retourne true si ce n'était pas déjà en chargement pour ce provider
    }

    loadingModels.value = true;
    errorLoadingModels.value = false; // Reset l'erreur globale avant de fetch
    console.log(`useAIModels: Fetching models for ${provider}...`);
    try {
      const url = `${config.apiUrl}/models/${provider}`;
      const headers = { 'x-api-key': config.apiKey };
      const response = await fetch(url, { headers });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      const data = await response.json();
      if (data && data.models) {
        const normalizedModels = data.models.map(model => {
          try {
            const baseModel = typeof model === 'string' ? { id: model, name: model } : { ...model };
            const name = baseModel.name?.toString() || baseModel.id?.toString() || '';
            const formattedName = (provider === 'openrouter' && name.includes('/')) ? name : name.replace(/^models\//, '');
            const normalized = {
              id: baseModel.id?.toString() || '',
              name: name,
              description: baseModel.description?.toString() || 'Aucune description',
              formattedName: formattedName
            };
            return normalized.id ? normalized : null;
          } catch (e) { console.error("Erreur normalisation modèle:", e, model); return null; }
        }).filter(m => m !== null);
        availableModels[provider] = normalizedModels;
        console.log(`useAIModels: Models fetched for ${provider}:`, normalizedModels.length);
        return true; // Succès
      } else {
        throw new Error('Réponse API invalide.');
      }
    } catch (error) {
      if (showSnackbar) showSnackbar(handleApiError(error, `chargement des modèles pour ${providerInfo[provider]?.title || provider}`), 'error', 6000);
      availableModels[provider] = []; // Vide en cas d'erreur
      errorLoadingModels.value = true; // Indique une erreur globale de chargement
      return false; // Échec
    } finally {
      loadingModels.value = false; // Mettre à false seulement à la fin du fetch
    }
  };

  const selectDefaultModel = (provider) => {
    const models = availableModels[provider] || [];
    const defaultModelIdShort = config.providers[provider]?.defaultModel;
    const foundDefault = defaultModelIdShort ? models.find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
    return foundDefault ? foundDefault.id : (models.length > 0 ? models[0].id : null);
  };

  return {
    // Données statiques exportées pour être utilisées par les composants
    providerInfo,
    // writingStyles, // Ne plus retourner ici
    providers, // La liste formatée pour les selects

    // État réactif
    availableModels,
    loadingModels,
    errorLoadingModels,

    // Méthodes
    fetchModels,
    selectDefaultModel,
  };
}