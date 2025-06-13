import { ref } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

/**
 * Composable de service pour gérer le chargement et la sauvegarde du contenu d'un chapitre.
 * Ce composable est sans état (stateless) concernant les données du chapitre.
 */
export function useChapterContent() {
  // --- State du service ---
  const isLoading = ref(false);
  const isSaving = ref(false);
  const loadingError = ref(null);
  const savingError = ref(null);

  // --- API Functions ---

  /**
   * Récupère les données complètes d'un chapitre depuis l'API.
   * @param {number|string} chapterId - L'ID du chapitre à récupérer.
   * @returns {Promise<Object|null>} Les données du chapitre ou null en cas d'erreur.
   */
  async function fetchChapterContent(chapterId) {
    if (isLoading.value) {
      console.warn(`useChapterContent: Déjà en cours de chargement. Annulation.`);
      return null;
    }
    if (!chapterId) {
        console.warn("useChapterContent: fetchChapterContent appelé sans chapterId.");
        return null;
    }

    isLoading.value = true;
    loadingError.value = null;

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
      return chapterData;

    } catch (error) {
      const userMessage = handleApiError(error, `chargement du chapitre ${chapterId}`);
      loadingError.value = userMessage;
      console.error(`useChapterContent: Echec du chargement du chapitre ${chapterId}:`, error);
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Sauvegarde les données d'un chapitre via l'API.
   * @param {number|string} chapterId - L'ID du chapitre à sauvegarder.
   * @param {Object} chapterData - L'objet contenant les données à sauvegarder (ex: { title, content, summary }).
   * @returns {Promise<boolean>} True si la sauvegarde a réussi, false sinon.
   */
  async function saveChapterContent(chapterId, chapterData) {
    if (!chapterId) {
      console.error("useChapterContent: saveChapterContent appelé sans chapterId.");
      return false;
    }
     if (!chapterData) {
        console.error(`useChapterContent: Tentative de sauvegarde du chapitre ${chapterId} sans données.`);
        return false;
      }
    
    isSaving.value = true;
    savingError.value = null;

    try {
      const response = await fetch(`/api/chapters/${chapterId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey
        },
        body: JSON.stringify(chapterData)
      });

      if (!response.ok) {
        let errorBody = null;
        try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
        const error = new Error(`HTTP error! status: ${response.status}`);
        error.response = { status: response.status, data: errorBody };
        throw error;
      }

      return true;

    } catch (error) {
      const userMessage = handleApiError(error, `sauvegarde du chapitre ${chapterId}`);
      savingError.value = userMessage;
      console.error(`useChapterContent: Echec de la sauvegarde du chapitre ${chapterId}:`, error);
      return false;
    } finally {
      isSaving.value = false;
    }
  }

  return {
    // États du service
    isLoading,
    isSaving,
    loadingError,
    savingError,

    // Fonctions de service
    fetchChapterContent,
    saveChapterContent,
  };
}