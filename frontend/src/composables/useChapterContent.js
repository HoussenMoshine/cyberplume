import { ref, watch, computed } from 'vue';
import { config } from '@/config.js';
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

      const response = await fetch(`${config.apiUrl}/api/chapters/${chapterId}/`, {
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

      const response = await fetch(`${config.apiUrl}/api/chapters/${chapterId}/`, {
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
    if (oldId !== null && oldId === lastLoadedChapterId.value && editorRef.value && !isSaving.value) {
      const previousContent = editorRef.value.getHTML(); // Obtenir le contenu avant de potentiellement le changer
      if (previousContent !== lastSavedContent.value) {
          
          // Utiliser les métadonnées de l'ancien chapitre
          await saveChapterContent(oldId, previousContent, currentChapterTitle.value, currentChapterProjectId.value);
          // Ne pas bloquer le chargement même si la sauvegarde échoue, mais l'erreur sera dans savingError
      } else {
          
      }
    } else if (oldId !== null && oldId !== lastLoadedChapterId.value) {
        
    }

    // 2. Charger le nouveau chapitre
    await fetchChapterContent(newId);
  }, { immediate: false }); // Ne pas exécuter immédiatement, attendre le premier changement

  // AJOUT: Fonction pour appliquer une suggestion
  function applySuggestionToChapter(chapterId, suggestionData) {
    // chapterId n'est pas utilisé ici car on opère sur l'éditeur actif,
    // qui est déjà lié au selectedChapterIdRef.
    // On pourrait ajouter une vérification si chapterId === selectedChapterIdRef.value
    if (editorRef.value && suggestionData) {
      const { startIndex, endIndex, suggestedText } = suggestionData;
      // Assurer que les indices sont des nombres valides
      // TipTap utilise des positions 1-based pour la longueur du document,
      // mais 0-based pour les transactions si on utilise `replaceRange`.
      // `setTextSelection` attend `from` et `to` qui sont des positions.
      // Les indices de l'API sont probablement 0-based pour le début et exclusif pour la fin,
      // ou 0-based pour le début et inclusif pour la fin.
      // Supposons que startIndex est 0-based inclusif et endIndex est 0-based exclusif (comme slice)
      // ou que les deux sont 0-based et inclusifs.
      // Pour TipTap, `from` est la position de départ (0-based) et `to` est la position de fin (0-based).
      // Si les indices de l'API sont 0-based:
      const from = Number(startIndex);
      const to = Number(endIndex); // Si endIndex est exclusif, c'est bon. Si inclusif, to = Number(endIndex) + 1 pour certaines commandes.
                                  // Pour setTextSelection, `to` est la position *après* le dernier caractère.

      if (!isNaN(from) && !isNaN(to) && suggestedText !== undefined && from <= to) {
        console.log(`useChapterContent: Applying suggestion. From: ${from}, To: ${to}, Text: "${suggestedText}"`);
        editorRef.value.chain().focus().setTextSelection({ from, to }).deleteSelection().insertContent(suggestedText).run();
        // Mettre à jour lastSavedContent pour refléter le changement et éviter une sauvegarde inutile immédiate
        // ou pour que hasUnsavedChanges soit correct.
        lastSavedContent.value = editorRef.value.getHTML();
      } else {
        console.error('useChapterContent: Données de suggestion invalides ou incohérentes.', { from, to, suggestedText, suggestionData });
      }
    } else {
      console.error('useChapterContent: Editor reference or suggestionData is missing for applySuggestionToChapter.');
    }
  }


  // --- Exposed Methods & State ---
  return {
    currentChapterTitle,
    currentChapterProjectId,
    lastSavedContent,
    isLoading,
    isSaving,
    loadingError,
    savingError,
    hasUnsavedChanges,
    loadedChapterCharacters: computed(() => loadedChapterCharacters.value), // NOUVEAU: Exposer les personnages chargés

    loadChapterContent: fetchChapterContent, // Exposer sous le nom attendu par EditorComponent
    saveCurrentChapterIfNeeded, // Pour le déclenchement manuel et onBlur
    applySuggestionToChapter, // AJOUT: Exposer la nouvelle fonction
  };
}