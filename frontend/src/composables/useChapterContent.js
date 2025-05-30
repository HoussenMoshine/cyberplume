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
  const loadedChapterCharacters = ref([]); 

  // Variable pour suivre l'ID en cours de fetch et éviter les doublons
  let currentlyFetchingId = null; 

  const hasUnsavedChanges = computed(() => {
    if (!editorRef.value || !selectedChapterIdRef.value) {
      return false;
    }
    const currentContent = editorRef.value.getHTML();
    return currentContent !== lastSavedContent.value;
  });

  // --- API Functions ---

  async function fetchChapterContent(chapterId) {
    console.log(`useChapterContent: Attempting to fetch chapter ${chapterId}. Currently fetching: ${currentlyFetchingId}, isLoading: ${isLoading.value}`);
    
    if (isLoading.value && currentlyFetchingId === chapterId) {
      console.warn(`useChapterContent: Already fetching chapter ${chapterId}. Aborting duplicate call.`);
      return; 
    }

    if (chapterId === null) {
      editorRef.value?.commands.setContent('<p style="color: grey; text-align: center;">Sélectionnez un chapitre pour commencer l\'édition.</p>');
      lastSavedContent.value = '';
      currentChapterTitle.value = null;
      currentChapterProjectId.value = null;
      loadingError.value = null;
      lastLoadedChapterId.value = null;
      loadedChapterCharacters.value = [];
      if (isLoading.value && currentlyFetchingId === null) isLoading.value = false; // Si on annulait un chargement de "null"
      currentlyFetchingId = null;
      return null; 
    }
    
    currentlyFetchingId = chapterId; // Mémoriser l'ID qu'on commence à fetcher
    isLoading.value = true;
    loadingError.value = null;
    loadedChapterCharacters.value = []; 
    editorRef.value?.commands.setContent(`<p>Chargement du chapitre ${chapterId}...</p>`); 

    try {
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
      // Vérifier si l'ID a changé pendant le chargement (cas d'un clic rapide sur un autre chapitre)
      if (selectedChapterIdRef.value !== chapterId) {
          console.warn(`useChapterContent: Chapter ID changed during fetch. Requested ${chapterId}, current is ${selectedChapterIdRef.value}. Discarding fetched data for ${chapterId}.`);
          // Ne pas réinitialiser currentlyFetchingId ici, car un autre fetch est peut-être déjà en cours pour le nouvel ID.
          // isLoading sera géré par le fetch du nouvel ID.
          return null; 
      }

      const contentToLoad = chapterData.content || '<p>Ce chapitre est vide.</p>';
      editorRef.value?.commands.setContent(contentToLoad);
      lastSavedContent.value = contentToLoad;
      currentChapterTitle.value = chapterData.title;
      currentChapterProjectId.value = chapterData.project_id;
      lastLoadedChapterId.value = chapterId; 

      if (chapterData.characters && Array.isArray(chapterData.characters)) {
        loadedChapterCharacters.value = chapterData.characters;
      } else {
        loadedChapterCharacters.value = [];
      }
      
      return chapterData; 

    } catch (error) {
      const userMessage = handleApiError(error, `chargement du chapitre ${chapterId}`);
      loadingError.value = userMessage;
      // Ne mettre à jour l'éditeur que si l'erreur concerne le chapitre actuellement sélectionné
      if (selectedChapterIdRef.value === chapterId) {
        editorRef.value?.commands.setContent(`<p>Erreur lors du chargement du chapitre ${chapterId}.</p>`);
        lastSavedContent.value = '';
        currentChapterTitle.value = null;
        currentChapterProjectId.value = null;
        lastLoadedChapterId.value = null;
        loadedChapterCharacters.value = [];
      }
      console.error(`useChapterContent: Failed to load chapter ${chapterId}:`, error);
      return null; 
    } finally {
      // Ne mettre isLoading à false et réinitialiser currentlyFetchingId que si ce fetch est celui qui était attendu
      if (currentlyFetchingId === chapterId) {
        isLoading.value = false;
        currentlyFetchingId = null;
      }
    }
  }

  async function saveChapterContent(chapterId, content, title, projectId, isManualSave = false) {
    if (!chapterId || !editorRef.value || isSaving.value) {
      return false;
    }
     if (!title || !projectId) {
        console.warn(`useChapterContent: Attempting to save chapter ${chapterId} without title or project_id. This might fail if the backend requires them.`);
      }
    
    isSaving.value = true;
    savingError.value = null;

    try {
      const bodyData = {
        ...(title && { title }),
        ...(projectId && { project_id: projectId }),
        content: content,
      };

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

      lastSavedContent.value = content; 
      return true; 

    } catch (error) {
      const userMessage = handleApiError(error, `sauvegarde du chapitre ${chapterId}`);
      savingError.value = userMessage;
      console.error(`useChapterContent: Failed to save chapter ${chapterId}:`, error);
      return false; 
    } finally {
      isSaving.value = false;
    }
  }

  async function saveCurrentChapterIfNeeded(forceSave = false) {
    const chapterId = selectedChapterIdRef.value; 
    if (!chapterId || !editorRef.value || isSaving.value) {
      return false;
    }

    const currentContent = editorRef.value.getHTML();
    if (forceSave || currentContent !== lastSavedContent.value) {
      return await saveChapterContent(
        chapterId,
        currentContent,
        currentChapterTitle.value,
        currentChapterProjectId.value,
        forceSave 
      );
    } else {
      return true; 
    }
  }

  watch(selectedChapterIdRef, async (newId, oldId) => {
    console.log(`useChapterContent WATCH selectedChapterIdRef: old=${oldId}, new=${newId}, isLoading=${isLoading.value}, currentlyFetching=${currentlyFetchingId}`);

    if (newId === oldId && oldId !== undefined) { 
      console.log('useChapterContent WATCH: newId === oldId and oldId is defined, returning.');
      return; 
    }

    if (oldId !== null && oldId !== undefined && editorRef.value && hasUnsavedChanges.value) {
      console.log(`useChapterContent WATCH: Attempting to auto-save chapter ${oldId}`);
      const success = await saveCurrentChapterIfNeeded(false); 
      if (!success) {
        console.warn(`useChapterContent WATCH: Failed to auto-save chapter ${oldId} before switching.`);
      }
    }
    
    console.log(`useChapterContent WATCH: Calling fetchChapterContent for newId: ${newId}`);
    await fetchChapterContent(newId); 
  }, { immediate: true }); // Exécuter immédiatement pour gérer le chargement initial

  const clearLoadingError = () => {
    loadingError.value = null;
  };

  function applySuggestionToChapter(chapterId, suggestionData) {
    if (selectedChapterIdRef.value === chapterId && editorRef.value) {
        const currentPosition = editorRef.value.state.selection.to;
        editorRef.value.chain().focus().insertContentAt(currentPosition, suggestionData).run();
        // La sauvegarde se fera via le mécanisme normal (blur, manuel, changement de chapitre).
        return true;
    }
    return false;
  }

  return {
    currentChapterTitle: computed(() => currentChapterTitle.value),
    currentChapterProjectId: computed(() => currentChapterProjectId.value),
    content: lastSavedContent, 
    isLoading: computed(() => isLoading.value),
    isSaving: computed(() => isSaving.value),
    loadingError: computed(() => loadingError.value),
    savingError: computed(() => savingError.value),
    hasUnsavedChanges,
    loadedChapterCharacters: computed(() => loadedChapterCharacters.value), 

    loadChapterContent: fetchChapterContent,
    saveCurrentChapterIfNeeded,
    applySuggestionToChapter, 
    clearLoadingError,
  };
}