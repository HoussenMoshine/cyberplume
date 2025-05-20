import { reactive, ref } from 'vue';
import { config } from '@/config.js';
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
      const response = await fetch(`${config.apiUrl}/api/projects/${projectId}/chapters/`, { headers: { 'x-api-key': config.apiKey } });
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
      const response = await fetch(`${config.apiUrl}/api/projects/${projectId}/chapters/`, {
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
       const response = await fetch(`${config.apiUrl}/api/chapters/${chapterId}`, {
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
      const response = await fetch(`${config.apiUrl}/api/chapters/${chapterId}`, {
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
      const url = `${config.apiUrl}/api/chapters/${chapterId}/export/${format}`;
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

  const clearChaptersForProject = (projectId) => {
      if (chaptersByProjectId[projectId]) {
          // logChapterState(projectId, 'clearChaptersForProject - Before Delete'); // Log nettoyé
          delete chaptersByProjectId[projectId]; // Modification
          // logChapterState(projectId, 'clearChaptersForProject - After Delete'); // Log nettoyé
          delete loadingChapters[projectId];
          delete errorChapters[projectId];
          // console.log(`useChapters: Cleared chapter state for deleted project ${projectId}`); // Log nettoyé
      }
  };

  const reorderChapters = async (projectId, orderedIds) => {
      if (!projectId || !Array.isArray(orderedIds)) return false;
      // Optimistic update
      const originalChapters = chaptersByProjectId[projectId] ? [...chaptersByProjectId[projectId]] : [];
      // logChapterState(projectId, 'reorderChapters - Before Optimistic Update'); // Log nettoyé
      // Créer une map pour un accès rapide
      const chapterMap = new Map(originalChapters.map(chapter => [chapter.id, chapter]));
      // Créer le nouveau tableau ordonné
      const reorderedChapters = orderedIds.map(id => chapterMap.get(id)).filter(Boolean); // filter(Boolean) pour enlever les undefined si un ID n'existe pas

      if (reorderedChapters.length !== originalChapters.length) {
          console.error("[useChapters - reorderChapters] Mismatch in chapter count after reordering. Aborting optimistic update.");
          return false; // Sécurité: ne pas mettre à jour si les comptes ne correspondent pas
      }

      chaptersByProjectId[projectId] = reorderedChapters; // Modification (Optimistic)
      // logChapterState(projectId, 'reorderChapters - After Optimistic Update'); // Log nettoyé

      try {
          const response = await fetch(`${config.apiUrl}/api/projects/${projectId}/chapters/reorder`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
              body: JSON.stringify({ ordered_chapter_ids: orderedIds }),
          });
          if (!response.ok) {
              const error = new Error(`HTTP error! status: ${response.status}`);
              try { error.data = await response.json(); } catch (e) { /* ignore */ }
              throw error;
          }
          // Pas besoin de re-fetch, l'update optimiste est confirmé
          if (showSnackbar) showSnackbar('Ordre des chapitres sauvegardé');
          return true;
      } catch (error) {
          // Rollback optimistic update
          // logChapterState(projectId, 'reorderChapters - Before Rollback'); // Log nettoyé
          chaptersByProjectId[projectId] = originalChapters; // Modification (Rollback)
          // logChapterState(projectId, 'reorderChapters - After Rollback'); // Log nettoyé
          const errorMessage = handleApiError(error, 'Erreur réorganisation chapitres');
          chapterError.value = errorMessage;
          if (showSnackbar) showSnackbar(errorMessage, 'error');
          return false;
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
    reorderChapters
  };
}