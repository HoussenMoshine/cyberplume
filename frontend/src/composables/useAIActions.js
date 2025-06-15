import { ref } from 'vue';
import { config } from '@/config.js'; // config.apiKey est toujours utilisé
import { handleApiError } from '@/utils/errorHandler.js';

/**
 * Composable pour gérer les interactions avec l'API IA pour la génération de texte et l'analyse de style.
 * @param {import('vue').Ref<import('@tiptap/vue-3').Editor|null>} editorRef - Référence à l'instance de l'éditeur TipTap.
 * @param {import('vue').Ref<object|null>} selectedAiParamsRef - Référence aux paramètres IA sélectionnés { provider, model, style, customStyleDescription }.
 * @param {import('vue').Ref<Array<object>|null>} relevantCharactersRef - Référence à la liste des personnages pertinents [{id, name, description, backstory}].
 */
export function useAIActions(editorRef, selectedAiParamsRef, relevantCharactersRef) {
  // --- State ---
  const isGenerating = ref(false);
  const isAnalyzing = ref(false);
  const generationError = ref(null);
  const suggestions = ref([]);
  const currentAction = ref(null);
  // NOUVEAU: Référence pour stocker l'AbortController actif
  const activeAbortController = ref(null);

  // --- Helper Functions ---

  /**
   * Formate une chaîne de texte brut en HTML avec des paragraphes.
   * Si la chaîne contient déjà du HTML, elle est retournée telle quelle.
   * @param {string} text - Le texte à formater.
   * @returns {string} Le texte formaté en HTML.
   */
  function formatTextToHtml(text) {
    if (!text) return '';
    // Détection simple de HTML. Si on trouve des balises, on suppose que c'est déjà formaté.
    const isHtml = /<[a-z][\s\S]*>/i.test(text);
    if (isHtml) {
      return text;
    }
    // Sinon, on transforme les sauts de ligne en paragraphes.
    return text.split('\n').filter(p => p.trim() !== '').map(p => `<p>${p.trim()}</p>`).join('');
  }

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

   // MODIFIÉ: Ajout de la traduction pour 'continue' et 'dialogue'
   function getApiAction(action) {
    if (action === 'expand') return 'développer';
    if (action === 'continue') return 'continuer'; // Traduction ajoutée
    if (action === 'dialogue') return 'generer_dialogue'; // Traduction ajoutée
    if (action === 'shorten') return 'raccourcir'; // Traduction ajoutée (pour cohérence)
    if (action === 'reformulate') return 'reformuler'; // Traduction ajoutée (pour cohérence)
    // 'suggest' n'a pas besoin de traduction pour l'instant
    return action; // Retourne l'action originale si aucune traduction n'est nécessaire
  }


  // --- Core API Call Function ---

  async function triggerAIAction(action, customPrompt = null) {
    
    
    

    // Vérifications initiales (éditeur, paramètres IA, contexte)
    if (!editorRef.value) {
        console.warn("useAIActions: Editor reference is not available.");
        generationError.value = "L'éditeur n'est pas initialisé.";
        return;
    }
    if (!selectedAiParamsRef.value || !selectedAiParamsRef.value.provider || !selectedAiParamsRef.value.model || !selectedAiParamsRef.value.style) {
        console.warn("useAIActions: AI parameters (provider, model, style) are not fully selected.");
        generationError.value = "Veuillez sélectionner un fournisseur, un modèle et un style IA.";
        return;
    }
    let promptTextForApi;
    if (customPrompt) {
      promptTextForApi = customPrompt;
    } else {
      const context = getContextText(action);
      promptTextForApi = context.text;
      if (context.isEmpty && ['continue', 'reformulate', 'shorten', 'expand'].includes(action) && !customPrompt) { // Vérifier customPrompt ici aussi
          console.warn(`useAIActions: Action '${action}' requires text context, but it's empty.`);
          generationError.value = `L'action "${action}" nécessite du texte (sélectionné ou complet).`;
          return;
      }
    }
    if (!promptTextForApi && !['suggest'].includes(action)) { // 'suggest' peut fonctionner sans prompt initial si le backend le gère
        console.warn(`useAIActions: Action '${action}' ended up with no prompt text.`);
        generationError.value = `L'action "${action}" n'a pas pu déterminer de texte de prompt.`;
        return;
    }

    // Annuler toute action précédente si elle est encore en cours (sécurité)
    if (activeAbortController.value) {
        console.warn("useAIActions: Aborting previous ongoing action before starting a new one.");
        activeAbortController.value.abort();
    }

    // NOUVEAU: Créer et stocker l'AbortController
    const controller = new AbortController();
    activeAbortController.value = controller;

    const apiAction = getApiAction(action); // Utilise la fonction modifiée
    const { provider, model, style } = selectedAiParamsRef.value;
    const customStyleDescription = selectedAiParamsRef.value.customStyleDescription || null;
    let characterContextPayload = null;
    // MODIFIÉ: Utiliser les noms d'action frontend ici pour la logique
    const actionsUsingCharacterContext = ['suggest', 'continue', 'dialogue', 'reformulate', 'shorten', 'expand'];
    if (relevantCharactersRef && relevantCharactersRef.value && actionsUsingCharacterContext.includes(action)) {
        if (Array.isArray(relevantCharactersRef.value) && relevantCharactersRef.value.length > 0) {
             characterContextPayload = relevantCharactersRef.value;
        }
    }

    console.log(`useAIActions: Calling backend for action: ${apiAction} (original: ${action})`, { provider, model, style, customStyleDescription, characterContextPayload, promptLength: promptTextForApi.length }); // Log amélioré
    
    isGenerating.value = true;
    
    currentAction.value = action;
    generationError.value = null;
    if (action === 'suggest') suggestions.value = [];

    try {
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await fetch(`/api/generate/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey // config.apiKey est toujours utilisé
        },
        // NOUVEAU: Passer le signal de l'AbortController
        signal: controller.signal,
        body: JSON.stringify({
          provider: provider,
          model: model,
          prompt: promptTextForApi,
          action: apiAction, // Envoie l'action traduite
          style: style,
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
        console.error("useAIActions: Réponse API invalide:", data);
        throw new Error("La réponse de l'API ne contient pas le texte généré attendu.");
      }

    } catch (error) {
      // NOUVEAU: Gérer l'erreur d'annulation spécifiquement
      if (error.name === 'AbortError') {
        console.log(`useAIActions: AI action "${action}" was cancelled by the user.`);
        // Ne pas définir generationError pour une annulation manuelle
        // On pourrait afficher un message spécifique si besoin
      } else {
        // Gérer les autres erreurs comme avant
        const userMessage = handleApiError(error, `action IA "${action}"`);
        generationError.value = userMessage;
        console.error(`useAIActions: Failed AI action "${action}":`, error);
        if (action === 'suggest') suggestions.value = [];
      }
    } finally {
      
      isGenerating.value = false;
      
      currentAction.value = null;
      // NOUVEAU: Nettoyer l'AbortController
      if (activeAbortController.value === controller) { // S'assurer qu'on nettoie le bon contrôleur
          activeAbortController.value = null;
      }
    }
  }

  // --- Success Handler ---
  function handleAISuccess(action, generatedText) {
    if (!editorRef.value) return;
    // Vérifier si l'action n'a pas été annulée juste avant le succès (peu probable mais possible)
    if (!isGenerating.value && !activeAbortController.value) {
        console.log(`useAIActions: AI action '${action}' succeeded but was likely cancelled just before completion.`);
        return; // Ne pas traiter le résultat si annulé
    }

    console.log(`useAIActions: AI action '${action}' successful.`);
    generationError.value = null;

    const formattedText = formatTextToHtml(generatedText);

    switch (action) {
      case 'suggest':
        // Pour les suggestions, on garde le texte brut, car il est affiché dans une liste et non dans l'éditeur.
        suggestions.value = [generatedText];
        break;
      case 'continue':
      case 'dialogue':
        editorRef.value.chain().focus().insertContent(" " + formattedText).run();
        break;
      case 'reformulate':
      case 'shorten':
      case 'expand':
        if (!editorRef.value.state.selection.empty) {
          editorRef.value.chain().focus().deleteSelection().insertContent(formattedText).run();
        } else {
          editorRef.value.chain().focus().insertContent(formattedText).run();
          console.warn(`useAIActions: Action '${action}' a été exécutée sans sélection. Le texte a été inséré.`);
        }
        break;
      default:
        console.warn(`useAIActions: Action IA inconnue ou non gérée dans le succès: ${action}`);
    }
  }


  // --- Style Analysis ---
  // TODO: Intégrer la logique d'analyse de style ici si elle doit partager l'état isAnalyzing, etc.
  // Pour l'instant, elle est séparée dans useAnalysis.js mais pourrait être fusionnée
  // si les indicateurs de chargement doivent être unifiés.

  /**
   * Gère le téléversement et l'analyse d'un fichier pour le style.
   * @param {File} file - Le fichier à analyser.
   */
  async function analyzeStyleUpload(file) { // file ici devrait être un objet File
    if (!file) {
      generationError.value = "Aucun fichier sélectionné pour l'analyse de style.";
      return null;
    }
    if (!selectedAiParamsRef.value || !selectedAiParamsRef.value.provider || !selectedAiParamsRef.value.model) {
        generationError.value = "Veuillez sélectionner un fournisseur et un modèle IA pour l'analyse.";
        return null;
    }

    console.log("useAIActions: analyzeStyleUpload - Starting analysis for file:", file.name);
    isAnalyzing.value = true; // Utiliser isAnalyzing pour cette opération
    generationError.value = null; // Réinitialiser les erreurs précédentes

    const formData = new FormData();
    formData.append('file', file);
    formData.append('provider', selectedAiParamsRef.value.provider);
    formData.append('model', selectedAiParamsRef.value.model);

    try {
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await fetch(`/api/style/analyze-upload`, {
        method: 'POST',
        headers: {
          // 'Content-Type': 'multipart/form-data' est automatiquement défini par le navigateur pour FormData
          'x-api-key': config.apiKey
        },
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
      // Retourner la description de style pour que le composant appelant puisse la gérer
      // (par exemple, la stocker dans selectedAiParamsRef.value.customStyleDescription)
      return data.style_description;

    } catch (error) {
      const userMessage = handleApiError(error, "analyse de style du fichier");
      generationError.value = userMessage;
      console.error("useAIActions: analyzeStyleUpload - Failed:", error);
      return null; // Retourner null en cas d'erreur
    } finally {
      isAnalyzing.value = false;
      console.log("useAIActions: analyzeStyleUpload - Finished analysis attempt for file:", file.name);
    }
  }


  // NOUVEAU: Fonction pour annuler l'action en cours
  /**
   * Annule l'action IA actuellement en cours.
   */
  function cancelCurrentAction() {
    if (activeAbortController.value) {
      console.log("useAIActions: User requested cancellation of current AI action.");
      activeAbortController.value.abort(); // Déclenche l'AbortError
      // Le reste de la gestion (isGenerating = false, etc.) se fait dans le bloc finally de triggerAIAction
    } else {
      console.log("useAIActions: No active AI action to cancel.");
    }
  }


  // --- Exposed ---
  // Retourner isGenerating sous le nom isAIGenerating pour correspondre à l'usage dans EditorComponent
  // et pour éviter la confusion avec une potentielle variable locale isGenerating dans le composant.
  // Cependant, pour la cohérence interne du composable, on garde isGenerating.
  // L'EditorComponent s'attend à `isAIGenerating`.
  // On va renommer ici pour la clarté de ce que le composable expose.
  // **Correction**: Le plan mentionne `isAIGenerating` comme venant de `useAIActions`.
  // Donc, il faut que ce composable expose `isAIGenerating`.
  // La variable interne est `isGenerating`. On va la retourner en tant que `isAIGenerating`.

  return {
    isAIGenerating: isGenerating, // Exposer isGenerating en tant que isAIGenerating
    isAnalyzing, // Pour l'analyse de style si on l'utilise
    generationError,
    suggestions,
    currentAction,
    triggerAIAction,
    analyzeStyleUpload,
    cancelCurrentAction, // Exposer la fonction d'annulation
    getContextText // Exposer pour d'éventuels tests ou usages externes directs
  };
}