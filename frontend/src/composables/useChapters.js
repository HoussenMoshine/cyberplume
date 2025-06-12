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
  const generatingSummaryChapterId = ref(null); // NOUVEAU: Pour le chargement de la génération de résumé
  const errorOnAddChapter = ref(null); // Pour les erreurs spécifiques à l'ajout de chapitre

  const fetchChaptersForProject = async (projectId) => {
    if (!projectId) return [];
    loadingChapters[projectId] = true;
    errorChapters[projectId] = null;
    chapterError.value = null; // Réinitialiser l'erreur générale
    try {
      const response = await fetch(`/api/projects/${projectId}/chapters`, { headers: { 'x-api-key': config.apiKey } });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      const data = await response.json();
      chaptersByProjectId[projectId] = data; 
      return data;
    } catch (error) {
      const errorMessage = handleApiError(error, `Erreur chargement chapitres (Projet ${projectId})`);
      errorChapters[projectId] = errorMessage;
      chapterError.value = errorMessage; 
      chaptersByProjectId[projectId] = []; 
      return [];
    } finally {
      if (loadingChapters[projectId] !== undefined) {
          loadingChapters[projectId] = false;
      }
    }
  };

  const addChapter = async (projectId, title) => {
    // Assurer que le titre est une chaîne de caractères valide, sinon utiliser un titre par défaut.
    const chapterTitle = (typeof title === 'string' && title.trim() !== '') ? title : 'Nouveau Chapitre';

    if (!projectId) return null;
    submittingChapter.value = true;
    chapterError.value = null; 
    errorOnAddChapter.value = null; // Réinitialiser l'erreur spécifique à l'ajout 
    let newChapterResponse = null; // Renommé pour clarté
    try {
      const response = await fetch(`/api/projects/${projectId}/chapters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        // Utiliser le titre validé
        body: JSON.stringify({ title: chapterTitle, content: '' }), 
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      newChapterResponse = await response.json(); // Le chapitre créé par l'API

      // Re-fetch la liste des chapitres pour assurer la réactivité et l'ordre correct
      await fetchChaptersForProject(projectId); 

      if (showSnackbar) showSnackbar('Chapitre ajouté avec succès');
    } catch (error) {
      const errorMessage = handleApiError(error, "Erreur ajout chapitre");
      chapterError.value = errorMessage; // Conserver pour l'erreur générale si besoin
      errorOnAddChapter.value = errorMessage; // Assigner l'erreur spécifique à l'ajout 
      if (showSnackbar) showSnackbar(errorMessage, 'error');
      return null; 
    } finally {
      submittingChapter.value = false;
    }
    return newChapterResponse; // Retourner le chapitre créé par l'API
  };

  const updateChapter = async (chapterId, updateData) => {
     if (!chapterId || !updateData) return false;
     submittingChapter.value = true;
     chapterError.value = null; 
     let success = false;
     let projectIdToUpdate = null;
     try {
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
       
       // Trouver le projectId pour re-fetch
       for (const pid in chaptersByProjectId) {
         if (chaptersByProjectId[pid]?.some(c => c.id === chapterId)) {
           projectIdToUpdate = pid;
           break;
         }
       }

       if (projectIdToUpdate) {
         await fetchChaptersForProject(projectIdToUpdate); // Re-fetch pour mettre à jour
       } else { 
         // Fallback si projectId n'est pas trouvé (moins idéal, mais met à jour localement)
          for (const projectId_loop in chaptersByProjectId) { // Renommer la variable de boucle pour éviter conflit
            const index = chaptersByProjectId[projectId_loop]?.findIndex(c => c.id === chapterId);
            if (index !== -1 && chaptersByProjectId[projectId_loop]) {
              chaptersByProjectId[projectId_loop][index] = { ...chaptersByProjectId[projectId_loop][index], ...updatedChapter };
              break;
            }
          }
       }

       if (showSnackbar) showSnackbar('Chapitre mis à jour');
       success = true;
     } catch (error) {
       const errorMessage = handleApiError(error, 'Erreur MAJ chapitre');
       chapterError.value = errorMessage; 
       if (showSnackbar) showSnackbar(errorMessage, 'error');
     } finally {
       submittingChapter.value = false;
     }
     return success;
  };

  // MODIFIÉ: La fonction accepte maintenant projectId pour un re-fetch fiable
  const deleteChapter = async (projectId, chapterId) => {
    if (!projectId || !chapterId) return false;
    deletingChapterItem.value = true;
    chapterError.value = null; 
    let success = false;
    
    try {
      const response = await fetch(`/api/chapters/${chapterId}`, {
        method: 'DELETE',
        headers: { 'x-api-key': config.apiKey },
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      
      // Utiliser le projectId fourni pour un re-fetch fiable
      await fetchChaptersForProject(projectId); 
      
      if (showSnackbar) showSnackbar('Chapitre supprimé');
      success = true;
    } catch (error) {
      const errorMessage = handleApiError(error, 'Erreur suppression chapitre');
      chapterError.value = errorMessage; 
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      deletingChapterItem.value = false;
    }
    return { success, projectId: projectId }; 
  };

  const exportChapter = async (chapterId, format) => {
    if (!chapterId || !format) return;
    exportingChapterId.value = chapterId;
    chapterError.value = null; 
    if (showSnackbar) showSnackbar(`Export du chapitre en ${format.toUpperCase()}...`, 'info');
    try {
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
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
      if (showSnackbar) showSnackbar('Export terminé', 'success');
    } catch (error) {
      const errorMessage = handleApiError(error, `Erreur export (${format})`);
      chapterError.value = errorMessage; 
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      exportingChapterId.value = null;
    }
  };

  // NOUVEAU: Génération de résumé de chapitre
  const generateChapterSummary = async (projectId, chapterId) => {
    if (!chapterId) return;
    generatingSummaryChapterId.value = chapterId;
    chapterError.value = null;
    try {
      // Note: Le corps de la requête est vide car le backend a déjà tout ce dont il a besoin.
      const response = await fetch(`/api/chapters/${chapterId}/generate-summary`, {
        method: 'POST',
        headers: { 'x-api-key': config.apiKey },
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      // Re-fetch les chapitres pour mettre à jour la liste avec le nouveau résumé
      await fetchChaptersForProject(projectId);
      if (showSnackbar) showSnackbar('Résumé généré avec succès', 'success');
    } catch (error) {
      const errorMessage = handleApiError(error, 'Erreur génération résumé');
      chapterError.value = errorMessage;
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      generatingSummaryChapterId.value = null;
    }
  };

  // NOUVEAU: Fonction pour vider les chapitres d'un projet (utile lors de la suppression de projet)
  const clearChaptersForProject = (projectId) => {
    if (chaptersByProjectId[projectId]) {
      delete chaptersByProjectId[projectId];
    }
  };

  // NOUVEAU: Réordonnancement des chapitres
  const reorderChapters = async (projectId, orderedIds) => {
    if (!projectId || !orderedIds) return;
    // Optimistic update: Mettre à jour l'état local immédiatement
    const originalOrder = [...chaptersByProjectId[projectId]];
    const reordered = orderedIds.map(id => originalOrder.find(c => c.id === id)).filter(Boolean);
    chaptersByProjectId[projectId] = reordered;

    try {
      const response = await fetch(`/api/projects/${projectId}/chapters/reorder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        body: JSON.stringify({ ordered_ids: orderedIds }),
      });
      if (!response.ok) {
        // Si l'API échoue, revenir à l'état précédent
        chaptersByProjectId[projectId] = originalOrder;
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      // Pas besoin de re-fetch, l'état est déjà à jour
      if (showSnackbar) showSnackbar('Ordre des chapitres sauvegardé', 'success');
    } catch (error) {
      // Assurer le retour à l'état précédent en cas d'erreur
      chaptersByProjectId[projectId] = originalOrder;
      const errorMessage = handleApiError(error, 'Erreur réorganisation chapitres');
      chapterError.value = errorMessage;
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    }
  };


  return {
    chaptersByProjectId,
    loadingChapters,
    errorChapters,
    chapterError,
    submittingChapter,
    deletingChapterItem,
    exportingChapterId,
    generatingSummaryChapterId,
    errorOnAddChapter,
    fetchChaptersForProject,
    addChapter,
    updateChapter,
    deleteChapter,
    exportChapter,
    generateChapterSummary,
    clearChaptersForProject,
    reorderChapters,
  };
}