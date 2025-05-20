import { ref, reactive } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

/**
 * Composable pour gérer les scènes d'un chapitre.
 * @param {Function} showSnackbar - Fonction pour afficher les notifications snackbar.
 */
export function useScenes(showSnackbar) {
  // --- State ---
  // Stocke les scènes par ID de chapitre
  const scenesByChapterId = reactive({});
  // Suivi de l'état de chargement par ID de chapitre
  const loadingScenes = reactive({});
  // Suivi des erreurs par ID de chapitre
  const errorScenes = reactive({});
  // État pour la soumission (ajout/modification)
  const submittingScene = ref(false);
  // État pour la suppression
  const deletingSceneId = ref(null);

  // --- Helper Functions ---
  const _findParentChapterId = (sceneId) => {
    for (const chapId in scenesByChapterId) {
      if (scenesByChapterId[chapId]?.some(s => s.id === sceneId)) {
        return parseInt(chapId, 10); // Assurer que c'est un nombre
      }
    }
    return null;
  };

  const _updateLocalSceneList = (chapterId, updatedScenes) => {
    if (chapterId !== null && scenesByChapterId.hasOwnProperty(chapterId)) {
        scenesByChapterId[chapterId] = updatedScenes.sort((a, b) => a.order - b.order);
    }
  };


  // --- API Functions ---

  async function fetchScenesForChapter(chapterId) {
    if (!chapterId) return;
    // Éviter les fetchs multiples si déjà en cours
    if (loadingScenes[chapterId]) return;

    console.log(`useScenes: Fetching scenes for chapter ${chapterId}...`);
    loadingScenes[chapterId] = true;
    errorScenes[chapterId] = null;
    try {
      const response = await fetch(`${config.apiUrl}/api/chapters/${chapterId}/scenes/`, {
        headers: { 'x-api-key': config.apiKey }
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      const scenes = await response.json();
      // Utiliser la fonction helper pour mettre à jour et trier
      _updateLocalSceneList(chapterId, scenes);
      console.log(`useScenes: Scenes fetched for chapter ${chapterId}:`, scenes.length);
    } catch (error) {
      const userMessage = handleApiError(error, `récupération des scènes du chapitre ${chapterId}`);
      errorScenes[chapterId] = userMessage;
      // Réinitialiser la liste locale en cas d'erreur pour permettre un nouveau fetch
      if (scenesByChapterId.hasOwnProperty(chapterId)) {
          scenesByChapterId[chapterId] = [];
      }
      console.error(`useScenes: Failed to fetch scenes for chapter ${chapterId}:`, error);
      if (showSnackbar) showSnackbar(userMessage, 'error');
    } finally {
      loadingScenes[chapterId] = false;
    }
  }

  async function addScene(chapterId, sceneData) {
    if (!chapterId) return null;
    console.log(`useScenes: Adding scene to chapter ${chapterId}...`, sceneData);
    submittingScene.value = true;
    errorScenes[chapterId] = null; // Réinitialiser l'erreur spécifique au chapitre
    let newScene = null;
    try {
      const response = await fetch(`${config.apiUrl}/api/chapters/${chapterId}/scenes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey
        },
        body: JSON.stringify(sceneData),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      newScene = await response.json();

      // --- Mise à jour locale optimiste ---
      if (!scenesByChapterId[chapterId]) {
        scenesByChapterId[chapterId] = [];
      }
      const updatedList = [...scenesByChapterId[chapterId], newScene];
      _updateLocalSceneList(chapterId, updatedList);
      // ------------------------------------

      console.log(`useScenes: Scene added successfully to chapter ${chapterId}.`, newScene);
      if (showSnackbar) showSnackbar('Scène ajoutée avec succès.', 'success');
      // Pas de fetch ici, on a mis à jour localement
    } catch (error) {
      const userMessage = handleApiError(error, `ajout de la scène au chapitre ${chapterId}`);
      errorScenes[chapterId] = userMessage; // Peut-être une erreur globale ?
      console.error(`useScenes: Failed to add scene to chapter ${chapterId}:`, error);
      if (showSnackbar) showSnackbar(userMessage, 'error');
      // En cas d'erreur, on pourrait vouloir re-fetcher pour corriger l'état ?
      // fetchScenesForChapter(chapterId); // Optionnel: re-synchroniser en cas d'échec
    } finally {
      submittingScene.value = false;
    }
    return newScene; // Retourner la scène ajoutée ou null
  }

  async function updateScene(sceneId, sceneUpdateData) {
    console.log(`useScenes: Updating scene ${sceneId}...`, sceneUpdateData);
    submittingScene.value = true;
    let updatedScene = null;
    const parentChapterId = _findParentChapterId(sceneId);
    if (parentChapterId !== null) {
        errorScenes[parentChapterId] = null; // Reset error for the chapter
    }

    try {
      const response = await fetch(`${config.apiUrl}/api/scenes/${sceneId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey
        },
        body: JSON.stringify(sceneUpdateData),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }
      updatedScene = await response.json();

      // --- Mise à jour locale optimiste ---
      if (parentChapterId !== null && scenesByChapterId[parentChapterId]) {
        const index = scenesByChapterId[parentChapterId].findIndex(s => s.id === sceneId);
        if (index !== -1) {
          // Créer une nouvelle liste pour la réactivité
          const updatedList = [...scenesByChapterId[parentChapterId]];
          updatedList[index] = updatedScene;
          _updateLocalSceneList(parentChapterId, updatedList);
        }
      }
      // ------------------------------------

      console.log(`useScenes: Scene ${sceneId} updated successfully.`, updatedScene);
      if (showSnackbar) showSnackbar('Scène mise à jour.', 'success');
      // Pas de fetch ici
    } catch (error) {
      const userMessage = handleApiError(error, `mise à jour de la scène ${sceneId}`);
      if (parentChapterId !== null) errorScenes[parentChapterId] = userMessage;
      console.error(`useScenes: Failed to update scene ${sceneId}:`, error);
      if (showSnackbar) showSnackbar(userMessage, 'error');
      // fetchScenesForChapter(parentChapterId); // Optionnel: re-synchroniser en cas d'échec
    } finally {
      submittingScene.value = false;
    }
    return updatedScene; // Retourner la scène mise à jour ou null
  }

  async function deleteScene(sceneId) {
    console.log(`useScenes: Deleting scene ${sceneId}...`);
    deletingSceneId.value = sceneId;
    const parentChapterId = _findParentChapterId(sceneId);
    if (parentChapterId !== null) {
        errorScenes[parentChapterId] = null; // Reset error
    }

    try {
      const response = await fetch(`${config.apiUrl}/api/scenes/${sceneId}/`, {
        method: 'DELETE',
        headers: { 'x-api-key': config.apiKey }
      });

      // --- Mise à jour locale optimiste (même si 404, on la retire) ---
      let sceneRemovedLocally = false;
      if (parentChapterId !== null && scenesByChapterId[parentChapterId]) {
          const initialLength = scenesByChapterId[parentChapterId].length;
          const updatedList = scenesByChapterId[parentChapterId].filter(s => s.id !== sceneId);
          if (updatedList.length < initialLength) {
              _updateLocalSceneList(parentChapterId, updatedList);
              sceneRemovedLocally = true;
          }
      }
      // ----------------------------------------------------------------

      if (!response.ok) {
         if (response.status === 404) {
             console.warn(`useScenes: Scene ${sceneId} not found for deletion (already removed locally?).`);
             // Considérer comme un succès si déjà retiré localement
             return sceneRemovedLocally;
         }
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }

      console.log(`useScenes: Scene ${sceneId} deleted successfully.`);
      if (showSnackbar) showSnackbar('Scène supprimée.', 'success');
      // Pas de fetch ici
      return true;
    } catch (error) {
      const userMessage = handleApiError(error, `suppression de la scène ${sceneId}`);
       if (parentChapterId !== null) errorScenes[parentChapterId] = userMessage;
      console.error(`useScenes: Failed to delete scene ${sceneId}:`, error);
      if (showSnackbar) showSnackbar(userMessage, 'error');
      // En cas d'erreur API après suppression locale, on pourrait vouloir re-fetcher
      // if (sceneRemovedLocally && parentChapterId !== null) {
      //     fetchScenesForChapter(parentChapterId);
      // }
      return false;
    } finally {
      deletingSceneId.value = null;
    }
  }

  // --- Exposed Methods & State ---
  return {
    scenesByChapterId,
    loadingScenes,
    errorScenes,
    submittingScene,
    deletingSceneId,

    fetchScenesForChapter,
    addScene,
    updateScene,
    deleteScene,
  };
}