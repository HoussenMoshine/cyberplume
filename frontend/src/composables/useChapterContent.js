import { ref, watch, computed } from 'vue';
import { config } from '@/config.js'; // config.apiKey est toujours utilisé
import { handleApiError } from '@/utils/errorHandler.js';

/**
 * Composable pour gérer le chargement et la sauvegarde du contenu d'un chapitre.
 * @param {import('vue').Ref<number|string|null>} selectedChapterIdRef - Référence à l'ID du chapitre sélectionné.
 * @param {import('vue').Ref<import('@tiptap/vue-3').Editor|null>} editorRef - Référence à l'instance de l'éditeur TipTap.
 */
export function useChapterContent(selectedChapterIdRef, editorRef) {
  // --- State ---
  const currentChapterTitle = ref(null);
  const currentChapterProjectId = ref(null);
  const lastSavedContent = ref('');
  const isLoading = ref(false);
  const isSaving = ref(false);
  const loadingError = ref(null);
  const savingError = ref(null);
  const lastLoadedChapterId = ref(null); // Pour gérer la sauvegarde avant changement
  const loadedChapterCharacters = ref([]); // Gardé, mais ne sera plus peuplé par les scènes


  const hasUnsavedChanges = computed(() => {
    if (!editorRef.value || !selectedChapterIdRef.value) {
      return false;
    }
    const currentContent = editorRef.value.getHTML();
    return currentContent !== lastSavedContent.value;
  });

  // --- API Functions ---

  async function fetchChapterContent(chapterId) {
    // --- DEBUG LOG ---
    
    // --- END DEBUG LOG ---

    if (chapterId === null) {
      editorRef.value?.commands.setContent('<p>Aucun chapitre sélectionné.</p>');
      lastSavedContent.value = '';
      currentChapterTitle.value = null;
      currentChapterProjectId.value = null;
      loadingError.value = null;
      lastLoadedChapterId.value = null;
      loadedChapterCharacters.value = []; // Réinitialiser les personnages
      return null; // Retourner null si aucun chapitre n'est sélectionné
    }

    
    isLoading.value = true;
    loadingError.value = null;
    loadedChapterCharacters.value = []; // Réinitialiser avant chargement
    editorRef.value?.commands.setContent(`<p>Chargement du chapitre ${chapterId}...</p>`); // Feedback visuel

    try {

      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await fetch(`/api/chapters/${chapterId}`, {
        headers: { 'x-api-key': config.apiKey }
      });

      if (!response.ok) {
        let errorBody = null;
        try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
        const error = new Error(`HTTP error! status: ${response.status}`);
        error.response = { status: response.status, data: errorBody };
        throw error;
      }

      const chapterData = await response.json();
      const contentToLoad = chapterData.content || '<p>Ce chapitre est vide.</p>';

      editorRef.value?.commands.setContent(contentToLoad);
      lastSavedContent.value = contentToLoad;
      currentChapterTitle.value = chapterData.title;
      currentChapterProjectId.value = chapterData.project_id;
      lastLoadedChapterId.value = chapterId; // Mémoriser l'ID chargé

      // La logique d'extraction des personnages des scènes a été supprimée ici.
      // Si les personnages sont directement liés aux chapitres dans le backend,
      // cette partie devrait être adaptée pour les charger depuis chapterData.characters (par exemple).
      // Pour l'instant, loadedChapterCharacters restera vide ou sera peuplé par une autre source.
      if (chapterData.characters && Array.isArray(chapterData.characters)) {
        loadedChapterCharacters.value = chapterData.characters;
      } else {
        loadedChapterCharacters.value = [];
      }
      

      
      return chapterData; // Retourner les données chargées

    } catch (error) {
      const userMessage = handleApiError(error, `chargement du chapitre ${chapterId}`);
      loadingError.value = userMessage;
      editorRef.value?.commands.setContent(`<p>Erreur lors du chargement du chapitre ${chapterId}.</p>`);
      lastSavedContent.value = '';
      currentChapterTitle.value = null;
      currentChapterProjectId.value = null;
      lastLoadedChapterId.value = null;
      loadedChapterCharacters.value = []; // Réinitialiser en cas d'erreur
      console.error(`useChapterContent: Failed to load chapter ${chapterId}:`, error);
      return null; // Retourner null en cas d'erreur
    } finally {
      isLoading.value = false;
    }
  }

  async function saveChapterContent(chapterId, content, title, projectId, isManualSave = false) {
    if (!chapterId || !editorRef.value || isSaving.value) {
      
      return false;
    }
     // Vérifier si le titre ou project_id sont disponibles, sinon logguer une alerte
     if (!title || !projectId) {
        console.warn(`useChapterContent: Attempting to save chapter ${chapterId} without title or project_id. This might fail if the backend requires them.`);
        // On pourrait choisir de bloquer ici, mais pour l'instant on tente la sauvegarde partielle
      }


    
    isSaving.value = true;
    savingError.value = null;

    try {
      const bodyData = {
        // Inclure title et project_id seulement s'ils sont définis
        ...(title && { title }),
        ...(projectId && { project_id: projectId }),
        content: content,
      };

      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await fetch(`/api/chapters/${chapterId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey
        },
        body: JSON.stringify(bodyData)
      });

      if (!response.ok) {
        let errorBody = null;
        try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
        const error = new Error(`HTTP error! status: ${response.status}`);
        error.response = { status: response.status, data: errorBody };
        throw error;
      }

      lastSavedContent.value = content; // Mettre à jour le contenu sauvegardé
      
      return true; // Indiquer le succès

    } catch (error) {
      const userMessage = handleApiError(error, `sauvegarde du chapitre ${chapterId}`);
      savingError.value = userMessage;
      console.error(`useChapterContent: Failed to save chapter ${chapterId}:`, error);
      return false; // Indiquer l'échec
    } finally {
      isSaving.value = false;
    }
  }

  // Fonction pour sauvegarder si nécessaire (appelée par onBlur ou manuellement)
  async function saveCurrentChapterIfNeeded(forceSave = false) {
    const chapterId = selectedChapterIdRef.value; // Utiliser la valeur actuelle de la ref
    if (!chapterId || !editorRef.value || isSaving.value) {
      return false;
    }

    const currentContent = editorRef.value.getHTML();
    if (forceSave || currentContent !== lastSavedContent.value) {
      
      // Utiliser les métadonnées actuelles pour la sauvegarde
      return await saveChapterContent(
        chapterId,
        currentContent,
        currentChapterTitle.value,
        currentChapterProjectId.value,
        forceSave // Indiquer si c'est une sauvegarde manuelle/forcée
      );
    } else {
      
      return true; // Considéré comme un succès car aucune action n'était requise
    }
  }

  // --- Watcher ---
  watch(selectedChapterIdRef, async (newId, oldId) => {
    // --- DEBUG LOG ---
    
    // --- END DEBUG LOG ---
    if (newId === oldId) {
      
      return; // Ne rien faire si l'ID n'a pas changé
    }

    // Sauvegarder l'ancien contenu avant de charger le nouveau, s'il y a des changements non sauvegardés
    if (oldId !== null && editorRef.value && hasUnsavedChanges.value) {
      
      const success = await saveCurrentChapterIfNeeded(false); // false car ce n'est pas une sauvegarde manuelle forcée
      if (!success) {
        // Gérer l'échec de la sauvegarde ? Peut-être afficher un message à l'utilisateur.
        // Pour l'instant, on continue le chargement du nouveau chapitre.
        console.warn(`useChapterContent: Failed to auto-save chapter ${oldId} before switching.`);
      }
    }
    
    // Charger le nouveau contenu
    await fetchChapterContent(newId);
  }, { immediate: false }); // immediate: false car le chargement initial est géré par EditorComponent via onMounted


  // --- Helper pour effacer l'erreur de chargement ---
  const clearLoadingError = () => {
    loadingError.value = null;
  };

  // --- Fonction pour appliquer une suggestion ---
  // Modifiée pour mettre à jour directement le contenu de l'éditeur et marquer comme non sauvegardé
  function applySuggestionToChapter(chapterId, suggestionData) {
    if (selectedChapterIdRef.value === chapterId && editorRef.value) {
        const currentPosition = editorRef.value.state.selection.to;
        
        // Insérer la suggestion. Si du texte est sélectionné, il sera remplacé.
        // Sinon, la suggestion est insérée à la position du curseur.
        editorRef.value.chain().focus().insertContentAt(currentPosition, suggestionData).run();
        
        // Mettre à jour lastSavedContent pour refléter que le contenu a changé et nécessite une sauvegarde.
        // On ne met PAS à jour lastSavedContent avec le nouveau contenu, car cela indiquerait faussement
        // que le contenu est "sauvegardé" alors qu'il vient d'être modifié par la suggestion.
        // hasUnsavedChanges deviendra true.
        // La sauvegarde se fera via le mécanisme normal (blur, manuel, changement de chapitre).
        
        // Optionnel: forcer la détection de changement si TipTap ne le fait pas assez vite
        // editorRef.value.emit('update'); 
        return true;
    }
    return false;
  }


  // --- Retourner les refs et fonctions ---
  return {
    currentChapterTitle: computed(() => currentChapterTitle.value),
    currentChapterProjectId: computed(() => currentChapterProjectId.value),
    content: lastSavedContent, // Exposer le contenu sauvegardé (ou le contenu actuel si on le souhaite)
    isLoading: computed(() => isLoading.value),
    isSaving: computed(() => isSaving.value),
    loadingError: computed(() => loadingError.value),
    savingError: computed(() => savingError.value),
    hasUnsavedChanges,
    loadedChapterCharacters: computed(() => loadedChapterCharacters.value), // Personnages du chapitre

    loadChapterContent: fetchChapterContent,
    saveCurrentChapterIfNeeded,
    applySuggestionToChapter, // Exposer la fonction modifiée
    clearLoadingError,
  };
}