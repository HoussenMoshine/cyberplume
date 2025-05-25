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
  // NOUVEAU: State pour stocker les personnages de toutes les scènes du chapitre chargé
  const loadedChapterCharacters = ref([]);


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
      const response = await fetch(`/api/chapters/${chapterId}/`, {
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

      // NOUVEAU: Extraire les personnages de toutes les scènes du chapitre
      const charactersFromScenes = new Map(); // Utiliser une Map pour garantir l'unicité par ID
      if (chapterData.scenes && Array.isArray(chapterData.scenes)) {
          chapterData.scenes.forEach(scene => {
              if (scene.characters && Array.isArray(scene.characters)) {
                  scene.characters.forEach(char => {
                      if (!charactersFromScenes.has(char.id)) {
                          charactersFromScenes.set(char.id, char);
                      }
                  });
              }
          });
      }
      loadedChapterCharacters.value = Array.from(charactersFromScenes.values()); // Convertir la Map en tableau
      


      
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
      const response = await fetch(`/api/chapters/${chapterId}/`, {
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

    // 1. Sauvegarder l'ancien chapitre si nécessaire (et s'il était chargé par ce composable)
    if (oldId && oldId === lastLoadedChapterId.value) { // S'assurer qu'on sauvegarde le bon
      
      const saved = await saveCurrentChapterIfNeeded(); // Tenter de sauvegarder
      if (!saved) {
        // Gérer l'échec de la sauvegarde si nécessaire (ex: notifier l'utilisateur)
        console.warn(`useChapterContent: Failed to save chapter ${oldId} before switching. Changes might be lost.`);
        // Optionnel: Demander confirmation avant de changer si la sauvegarde échoue ?
      }
    }

    // 2. Charger le nouveau chapitre
    if (newId) {
      await fetchChapterContent(newId);
    } else {
      // Si newId est null (aucun chapitre sélectionné), effacer l'éditeur
      fetchChapterContent(null); // Appeler avec null pour réinitialiser
    }
  }, { immediate: false }); // Ne pas exécuter immédiatement au montage, attendre une sélection

  // NOUVEAU: Fonction pour appliquer une suggestion au contenu du chapitre
  // (Cette fonction est un exemple et pourrait nécessiter des ajustements)
  function applySuggestionToChapter(chapterId, suggestionData) {
    if (selectedChapterIdRef.value !== chapterId || !editorRef.value) {
      console.warn("Tentative d'appliquer une suggestion à un chapitre non sélectionné ou éditeur non prêt.");
      return;
    }

    // Exemple: Insérer la suggestion à la fin du contenu actuel
    // Vous devrez adapter cela en fonction de la structure de suggestionData
    // et de la manière dont vous souhaitez que les suggestions soient appliquées.
    if (suggestionData && suggestionData.text_to_insert) {
      editorRef.value.chain().focus().insertContent(` ${suggestionData.text_to_insert}`).run();
      // Optionnel: Sauvegarder immédiatement après l'application
      // saveCurrentChapterIfNeeded(true);
    } else {
      console.warn("Données de suggestion invalides pour l'application.", suggestionData);
    }
  }


  // --- Return ---
  return {
    currentChapterTitle,
    currentChapterProjectId,
    lastSavedContent,
    isLoading,
    isSaving,
    loadingError,
    savingError,
    hasUnsavedChanges,
    loadedChapterCharacters, // Exposer les personnages chargés

    fetchChapterContent,
    saveChapterContent,
    saveCurrentChapterIfNeeded,
    applySuggestionToChapter, // Exposer la nouvelle fonction
  };
}