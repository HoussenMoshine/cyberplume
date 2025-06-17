import { ref } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

/**
 * Composable pour gérer les interactions avec l'API IA.
 * @param {import('vue').Ref<import('@tiptap/vue-3').Editor|null>} editorRef
 * @param {import('vue').Ref<object|null>} selectedAiParamsRef
 * @param {import('vue').Ref<Array<object>|null>} relevantCharactersRef
 * @param {Function} insertAITextFunction - La fonction pour insérer le texte dans l'éditeur.
 */
export function useAIActions(editorRef, selectedAiParamsRef, relevantCharactersRef, insertAITextFunction) {
  // --- State ---
  const isGenerating = ref(false);
  const isAnalyzing = ref(false);
  const generationError = ref(null);
  const suggestions = ref([]);
  const currentAction = ref(null);
  const activeAbortController = ref(null);

  // --- Helper Functions ---

  function getContextText(actionType) {
    if (!editorRef.value) return { text: '', isEmpty: true };
    const { from, to, empty } = editorRef.value.state.selection;
    let text = '';
    if (!empty && ['reformulate', 'shorten', 'expand', 'dialogue'].includes(actionType)) {
      text = editorRef.value.state.doc.textBetween(from, to, ' ');
    } else {
      const fullText = editorRef.value.getText();
      if (actionType === 'continue') {
        const maxWords = 500;
        const words = fullText.split(/\s+/);
        text = words.slice(-maxWords).join(' ');
      } else {
        text = fullText;
      }
    }
    return { text: text.trim(), isEmpty: !text.trim() };
  }

   function getApiAction(action) {
    if (action === 'expand') return 'développer';
    if (action === 'continue') return 'continuer';
    if (action === 'dialogue') return 'generer_dialogue';
    if (action === 'shorten') return 'raccourcir';
    if (action === 'reformulate') return 'reformuler';
    return action;
  }

  // --- Core API Call Function ---

  async function triggerAIAction(action, customPrompt = null) {
    if (!editorRef.value) {
        generationError.value = "L'éditeur n'est pas initialisé.";
        return;
    }
    if (typeof insertAITextFunction !== 'function') {
        generationError.value = "Une erreur interne empêche l'insertion de texte (code: IA-FN-MISSING).";
        return;
    }
    if (!selectedAiParamsRef.value || !selectedAiParamsRef.value.provider || !selectedAiParamsRef.value.model || !selectedAiParamsRef.value.style) {
        generationError.value = "Veuillez sélectionner un fournisseur, un modèle et un style IA.";
        return;
    }
    let promptTextForApi;
    if (customPrompt) {
      promptTextForApi = customPrompt;
    } else {
      const context = getContextText(action);
      promptTextForApi = context.text;
      if (context.isEmpty && ['continue', 'reformulate', 'shorten', 'expand'].includes(action) && !customPrompt) {
          generationError.value = `L'action "${action}" nécessite du texte (sélectionné ou complet).`;
          return;
      }
    }
    if (!promptTextForApi && !['suggest'].includes(action)) {
        generationError.value = `L'action "${action}" n'a pas pu déterminer de texte de prompt.`;
        return;
    }

    if (activeAbortController.value) {
        activeAbortController.value.abort();
    }

    const controller = new AbortController();
    activeAbortController.value = controller;

    const apiAction = getApiAction(action);
    const { provider, model, style } = selectedAiParamsRef.value;
    const customStyleDescription = selectedAiParamsRef.value.customStyleDescription || null;
    let characterContextPayload = null;
    const actionsUsingCharacterContext = ['suggest', 'continue', 'dialogue', 'reformulate', 'shorten', 'expand'];
    if (relevantCharactersRef && relevantCharactersRef.value && actionsUsingCharacterContext.includes(action)) {
        if (Array.isArray(relevantCharactersRef.value) && relevantCharactersRef.value.length > 0) {
             characterContextPayload = relevantCharactersRef.value;
        }
    }

    isGenerating.value = true;
    currentAction.value = action;
    generationError.value = null;
    if (action === 'suggest') suggestions.value = [];

    try {
      const response = await fetch(`/api/generate/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        signal: controller.signal,
        body: JSON.stringify({
          provider, model, prompt: promptTextForApi, action: apiAction, style,
          custom_style_description: customStyleDescription,
          character_context: characterContextPayload
        })
      });

      if (!response.ok) {
        let errorBody = null;
        try { errorBody = await response.json(); } catch (e) { /* Ignorer */ }
        const error = new Error(`HTTP error! status: ${response.status}`);
        error.response = { status: response.status, data: errorBody };
        throw error;
      }

      const data = await response.json();

      if (data && data.generated_text) {
        handleAISuccess(action, data.generated_text);
      } else {
        throw new Error("La réponse de l'API ne contient pas le texte généré attendu.");
      }

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log(`AI action "${action}" was cancelled.`);
      } else {
        const userMessage = handleApiError(error, `action IA "${action}"`);
        generationError.value = userMessage;
        if (action === 'suggest') suggestions.value = [];
      }
    } finally {
      isGenerating.value = false;
      currentAction.value = null;
      if (activeAbortController.value === controller) {
          activeAbortController.value = null;
      }
    }
  }

  // --- Success Handler ---
  function handleAISuccess(action, generatedText) {
    if (!editorRef.value) return;

    console.log(`AI action '${action}' successful.`);
    generationError.value = null;

    switch (action) {
      case 'suggest':
        suggestions.value = [generatedText];
        break;
      case 'continue':
      case 'dialogue':
      case 'reformulate':
      case 'shorten':
      case 'expand':
        insertAITextFunction(generatedText);
        break;
      default:
        console.warn(`Action IA inconnue ou non gérée: ${action}`);
    }
  }

  // ... (le reste du fichier, analyzeStyleUpload, etc. reste identique)
  async function analyzeStyleUpload(file) {
    if (!file) {
      generationError.value = "Aucun fichier sélectionné pour l'analyse de style.";
      return null;
    }
    if (!selectedAiParamsRef.value || !selectedAiParamsRef.value.provider || !selectedAiParamsRef.value.model) {
        generationError.value = "Veuillez sélectionner un fournisseur et un modèle IA pour l'analyse.";
        return null;
    }

    console.log("useAIActions: analyzeStyleUpload - Starting analysis for file:", file.name);
    isAnalyzing.value = true;
    generationError.value = null;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('provider', selectedAiParamsRef.value.provider);
    formData.append('model', selectedAiParamsRef.value.model);

    try {
      const response = await fetch(`/api/style/analyze-upload`, {
        method: 'POST',
        headers: { 'x-api-key': config.apiKey },
        body: formData
      });

      if (!response.ok) {
        let errorBody = null;
        try { errorBody = await response.json(); } catch (e) { /* Ignorer */ }
        const error = new Error(`HTTP error! status: ${response.status}`);
        error.response = { status: response.status, data: errorBody };
        throw error;
      }

      const data = await response.json();
      console.log("useAIActions: analyzeStyleUpload - Analysis successful:", data);
      return data.style_description;

    } catch (error) {
      const userMessage = handleApiError(error, "analyse de style du fichier");
      generationError.value = userMessage;
      return null;
    } finally {
      isAnalyzing.value = false;
    }
  }

  function cancelCurrentAction() {
    if (activeAbortController.value) {
      activeAbortController.value.abort();
    }
  }

  return {
    isAIGenerating: isGenerating,
    isAnalyzing,
    generationError,
    suggestions,
    currentAction,
    triggerAIAction,
    analyzeStyleUpload,
    cancelCurrentAction,
    getContextText
  };
}