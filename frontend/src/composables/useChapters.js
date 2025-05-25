import { reactive, ref } from 'vue';
import { config } from '@/config.js'; // config.apiKey est toujours utilisé
import { handleApiError } from '@/utils/errorHandler.js';

export function useChapters(showSnackbar) {
  const chaptersByProjectId = reactive({});
  const loadingChapters = reactive({});
  const errorChapters = reactive({});
  const chapterError = ref(null); // Définition de la variable d'erreur générale

  const submittingChapter = ref(false);
  const deletingChapterItem = ref(false);
  const exportingChapterId = ref(null);

  const fetchChaptersForProject = async (projectId) => {
    if (!projectId) return [];
    loadingChapters[projectId] = true;
    errorChapters[projectId] = null;
    chapterError.value = null; // Réinitialiser l'erreur générale
    // console.log(`useChapters: Fetching chapters for project ${projectId}...`); // Log nettoyé
    try {
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await fetch(`/api/projects/${projectId}/chapters/`, { headers: { 'x-api-key': config.apiKey } });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      const data = await response.json();
      // console.log(`[useChapters LOG - fetchChaptersForProject] Received ${data.length} chapters from API for project ${projectId}. Assigning...`); // Log nettoyé
      chaptersByProjectId[projectId] = data; // Assignation
      // logChapterState(projectId, 'fetchChaptersForProject - After Assign'); // Log nettoyé
      return data;
    } catch (error) {
      const errorMessage = handleApiError(error, `Erreur chargement chapitres (Projet ${projectId})`);
      errorChapters[projectId] = errorMessage;
      chapterError.value = errorMessage; // Mettre à jour l'erreur générale
      // console.log(`[useChapters LOG - fetchChaptersForProject] Error fetching. Assigning empty array for project ${projectId}.`); // Log nettoyé
      chaptersByProjectId[projectId] = []; // Assignation en cas d'erreur
      // logChapterState(projectId, 'fetchChaptersForProject - After Error Assign'); // Log nettoyé
      return [];
    } finally {
      if (loadingChapters[projectId] !== undefined) {
          loadingChapters[projectId] = false;
      }
    }
  };

  const addChapter = async (projectId, title) => {
    if (!projectId || !title) return null;
    submittingChapter.value = true;
    chapterError.value = null; // Réinitialiser l'erreur générale
    let newChapter = null;
    try {
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await fetch(`/api/projects/${projectId}/chapters/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        body: JSON.stringify({ title: title, content: '' }),
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      newChapter = await response.json();
      if (!chaptersByProjectId[projectId]) {
        // console.log(`[useChapters LOG - addChapter] chaptersByProjectId[${projectId}] was undefined. Initializing.`); // Log nettoyé
        chaptersByProjectId[projectId] = [];
      }
      // logChapterState(projectId, 'addChapter - Before Add'); // Log nettoyé
      chaptersByProjectId[projectId] = [...chaptersByProjectId[projectId], newChapter]; // Modification
      // logChapterState(projectId, 'addChapter - After Add'); // Log nettoyé
      if (showSnackbar) showSnackbar('Chapitre ajouté avec succès');
    } catch (error) {
      const errorMessage = handleApiError(error, "Erreur ajout chapitre");
      chapterError.value = errorMessage; // Mettre à jour l'erreur générale
      if (showSnackbar) showSnackbar(errorMessage, 'error');
      return null; // Indiquer l'échec
    } finally {
      submittingChapter.value = false;
    }
    return newChapter; // Retourner le chapitre créé en cas de succès
  };

  const updateChapter = async (chapterId, updateData) => {
     if (!chapterId || !updateData) return false;
     submittingChapter.value = true;
     chapterError.value = null; // Réinitialiser l'erreur générale
     let success = false;
     let targetProjectId = null; // Pour logger
     try {
       // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
       const response = await fetch(`/api/chapters/${chapterId}`, {
         method: 'PUT',
         headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
         body: JSON.stringify(updateData),
       });
       if (!response.ok) {
         const error = new Error(`HTTP error! status: ${response.status}`);
         try { error.data = await response.json(); } catch (e) { /* ignore */ }
         throw error;
       }
       const updatedChapter = await response.json();
       for (const projectId in chaptersByProjectId) {
         const index = chaptersByProjectId[projectId]?.findIndex(c => c.id === chapterId);
         if (index !== -1) {
           targetProjectId = projectId; // Trouvé
           // logChapterState(projectId, `updateChapter - Before Update (Index ${index})`); // Log nettoyé
           chaptersByProjectId[projectId][index] = { ...chaptersByProjectId[projectId][index], ...updatedChapter }; // Modification
           // logChapterState(projectId, `updateChapter - After Update (Index ${index})`); // Log nettoyé
           break;
         }
       }
       if (showSnackbar) showSnackbar('Chapitre mis à jour');
       success = true;
     } catch (error) {
       const errorMessage = handleApiError(error, 'Erreur MAJ chapitre');
       chapterError.value = errorMessage; // Mettre à jour l'erreur générale
       if (showSnackbar) showSnackbar(errorMessage, 'error');
     } finally {
       submittingChapter.value = false;
     }
     return success;
  };

  const deleteChapter = async (chapterId) => {
console.log(`[useChapters] deleteChapter called with chapterId: ${chapterId}`);
    if (!chapterId) return false;
    deletingChapterItem.value = true;
    chapterError.value = null; // Réinitialiser l'erreur générale
    let success = false;
    let deletedChapterProjectId = null;

    try {
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await fetch(`/api/chapters/${chapterId}`, {
        method: 'DELETE',
        headers: { 'x-api-key': config.apiKey },
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      for (const projectId in chaptersByProjectId) {
        const initialLength = chaptersByProjectId[projectId]?.length;
        if (chaptersByProjectId[projectId]?.some(c => c.id === chapterId)) { // Vérifier si le chapitre existe dans ce projet
            deletedChapterProjectId = projectId;
            // logChapterState(projectId, 'deleteChapter - Before Filter'); // Log nettoyé
            chaptersByProjectId[projectId] = chaptersByProjectId[projectId]?.filter(c => c.id !== chapterId); // Modification
            // logChapterState(projectId, 'deleteChapter - After Filter'); // Log nettoyé
            break; // Sortir une fois trouvé et filtré
        }
      }
      if (showSnackbar) showSnackbar('Chapitre supprimé');
      success = true;
    } catch (error) {
      const errorMessage = handleApiError(error, 'Erreur suppression chapitre');
      chapterError.value = errorMessage; // Mettre à jour l'erreur générale
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      deletingChapterItem.value = false;
    }
    return { success, projectId: deletedChapterProjectId };
  };

  const exportChapter = async (chapterId, format) => {
    if (!chapterId || !format) return;
    exportingChapterId.value = chapterId;
    chapterError.value = null; // Réinitialiser l'erreur générale
    if (showSnackbar) showSnackbar(`Export du chapitre en ${format.toUpperCase()}...`, 'info');
    try {
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const url = `/api/chapters/${chapterId}/export/${format}`;
      const response = await fetch(url, { headers: { 'x-api-key': config.apiKey } });
      if (!response.ok) {
        let errorBody = null; let errorText = `Erreur HTTP ${response.status}`;
        try { errorBody = await response.json(); if (errorBody && errorBody.detail) { errorText = errorBody.detail; } } catch (e) { /* Ignore */ }
        const error = new Error(errorText); error.response = { status: response.status, data: errorBody }; throw error;
      }
      const disposition = response.headers.get('content-disposition');
      let filename = `chapitre_${chapterId}.${format}`;
      if (disposition && disposition.includes('attachment')) {
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        const matches = filenameRegex.exec(disposition);
        if (matches?.[1]) { filename = matches[1].replace(/['"]/g, ''); }
      }
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
      if (showSnackbar) showSnackbar(`Chapitre exporté en ${format.toUpperCase()} : ${filename}`);
    } catch (error) {
      const errorMessage = handleApiError(error, `Erreur lors de l'export en ${format.toUpperCase()}`);
      chapterError.value = errorMessage; // Mettre à jour l'erreur générale
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      exportingChapterId.value = null;
    }
  };

  // Fonction pour vider la liste des chapitres pour un projet donné (utilisé lors de la suppression d'un projet)
  const clearChaptersForProject = (projectId) => {
    if (chaptersByProjectId[projectId]) {
      // console.log(`[useChapters LOG - clearChaptersForProject] Clearing chapters for project ${projectId}.`); // Log nettoyé
      chaptersByProjectId[projectId] = [];
      // logChapterState(projectId, 'clearChaptersForProject - After Clear'); // Log nettoyé
    }
  };

  // Fonction pour réordonner les chapitres
  const reorderChapters = async (projectId, orderedIds) => {
    if (!projectId || !Array.isArray(orderedIds)) {
      console.error("reorderChapters: projectId ou orderedIds manquant ou invalide.");
      if (showSnackbar) showSnackbar("Erreur lors de la tentative de réorganisation des chapitres.", 'error');
      return false;
    }

    // Sauvegarde optimiste de l'état actuel pour la réactivité de l'UI
    const originalOrder = chaptersByProjectId[projectId] ? [...chaptersByProjectId[projectId]] : [];
    const newOrderedChapters = [];
    const chapterMap = new Map(originalOrder.map(chap => [chap.id, chap]));

    for (const id of orderedIds) {
        const chapter = chapterMap.get(id);
        if (chapter) {
            newOrderedChapters.push(chapter);
        }
    }
    chaptersByProjectId[projectId] = newOrderedChapters;


    submittingChapter.value = true; // Utiliser un indicateur de chargement existant ou un nouveau
    chapterError.value = null;

    try {
        // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
        const response = await fetch(`/api/projects/${projectId}/chapters/reorder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
            body: JSON.stringify({ ordered_chapter_ids: orderedIds }),
        });

        if (!response.ok) {
            const error = new Error(`HTTP error! status: ${response.status}`);
            try { error.data = await response.json(); } catch (e) { /* ignore */ }
            throw error;
        }

        // La réponse du backend pourrait être les chapitres réordonnés ou juste un succès.
        // Si la réponse contient les chapitres, on pourrait les utiliser pour mettre à jour.
        // Pour l'instant, on suppose que la mise à jour optimiste est suffisante.
        // const updatedChapters = await response.json();
        // chaptersByProjectId[projectId] = updatedChapters; // Si le backend renvoie la liste mise à jour

        if (showSnackbar) showSnackbar('Ordre des chapitres sauvegardé.', 'success');
        return true;
    } catch (error) {
        const errorMessage = handleApiError(error, "Erreur lors de la réorganisation des chapitres");
        chapterError.value = errorMessage;
        if (showSnackbar) showSnackbar(errorMessage, 'error');
        // Annuler la mise à jour optimiste en cas d'erreur
        chaptersByProjectId[projectId] = originalOrder;
        return false;
    } finally {
        submittingChapter.value = false;
    }
  };


  return {
    chaptersByProjectId,
    loadingChapters,
    errorChapters,
    chapterError, // Exposer l'erreur générale
    submittingChapter,
    deletingChapterItem,
    exportingChapterId,
    fetchChaptersForProject,
    addChapter,
    updateChapter,
    deleteChapter,
    exportChapter,
    clearChaptersForProject,
    reorderChapters,
  };
}