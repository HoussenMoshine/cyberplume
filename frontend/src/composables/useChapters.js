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
    if (!projectId || !title) return null;
    submittingChapter.value = true;
    chapterError.value = null; 
    let newChapterResponse = null; // Renommé pour clarté
    try {
      const response = await fetch(`/api/projects/${projectId}/chapters`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        body: JSON.stringify({ title: title, content: '' }), // Ajout de content vide par défaut si nécessaire
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      newChapterResponse = await response.json(); // Le chapitre créé par l'API

      // MODIFIÉ: Re-fetch la liste des chapitres pour assurer la réactivité et l'ordre correct
      await fetchChaptersForProject(projectId); 

      if (showSnackbar) showSnackbar('Chapitre ajouté avec succès');
    } catch (error) {
      const errorMessage = handleApiError(error, "Erreur ajout chapitre");
      chapterError.value = errorMessage; 
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

  const deleteChapter = async (chapterId) => {
    if (!chapterId) return false;
    deletingChapterItem.value = true;
    chapterError.value = null; 
    let success = false;
    let deletedChapterProjectId = null;

    // Trouver le projectId avant la suppression pour le re-fetch
    for (const pid in chaptersByProjectId) {
        if (chaptersByProjectId[pid]?.some(c => c.id === chapterId)) {
            deletedChapterProjectId = pid;
            break;
        }
    }

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
      
      if (deletedChapterProjectId) {
        await fetchChaptersForProject(deletedChapterProjectId); // Re-fetch
      } else {
        // Fallback si projectId n'a pas été trouvé (ne devrait pas arriver si le chapitre existait)
        for (const projectId_loop in chaptersByProjectId) { // Renommer la variable de boucle
          if (chaptersByProjectId[projectId_loop]?.some(c => c.id === chapterId)) { 
              chaptersByProjectId[projectId_loop] = chaptersByProjectId[projectId_loop]?.filter(c => c.id !== chapterId); 
              break; 
          }
        }
      }
      if (showSnackbar) showSnackbar('Chapitre supprimé');
      success = true;
    } catch (error) {
      const errorMessage = handleApiError(error, 'Erreur suppression chapitre');
      chapterError.value = errorMessage; 
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      deletingChapterItem.value = false;
    }
    // Retourner le projectId est toujours utile si l'appelant veut faire quelque chose avec
    return { success, projectId: deletedChapterProjectId }; 
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
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
      if (showSnackbar) showSnackbar(`Chapitre exporté en ${format.toUpperCase()} : ${filename}`);
    } catch (error) {
      const errorMessage = handleApiError(error, `Erreur lors de l'export en ${format.toUpperCase()}`);
      chapterError.value = errorMessage; 
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      exportingChapterId.value = null;
    }
  };

  // NOUVELLE FONCTION pour générer le résumé
  const generateChapterSummary = async (chapterId) => {
    if (!chapterId) return false;
    generatingSummaryChapterId.value = chapterId;
    chapterError.value = null;
    let success = false;
    let projectIdToUpdate = null;
    try {
      const response = await fetch(`/api/chapters/${chapterId}/generate-summary`, {
        method: 'POST',
        headers: { 'x-api-key': config.apiKey },
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      const summaryData = await response.json(); // Contient le chapitre mis à jour avec le résumé

      // Trouver le projectId pour re-fetch
       for (const pid in chaptersByProjectId) {
         if (chaptersByProjectId[pid]?.some(c => c.id === chapterId)) {
           projectIdToUpdate = pid;
           break;
         }
       }

      if (projectIdToUpdate) {
        await fetchChaptersForProject(projectIdToUpdate); // Re-fetch pour mettre à jour la liste
      } else {
        // Fallback: mise à jour locale si projectId non trouvé (moins idéal)
        for (const projectId_loop in chaptersByProjectId) { // Renommer la variable de boucle
            const index = chaptersByProjectId[projectId_loop]?.findIndex(c => c.id === chapterId);
            if (index !== -1 && chaptersByProjectId[projectId_loop] && summaryData) {
                // Assumer que summaryData est le chapitre mis à jour
                chaptersByProjectId[projectId_loop][index] = { ...chaptersByProjectId[projectId_loop][index], summary: summaryData.summary }; // Ne propager que le résumé pour éviter la copie de contenu
                break;
            }
        }
      }
      if (showSnackbar) showSnackbar('Résumé du chapitre généré et sauvegardé.');
      success = true;
    } catch (error) {
      const errorMessage = handleApiError(error, "Erreur génération résumé chapitre");
      chapterError.value = errorMessage;
      if (showSnackbar) showSnackbar(errorMessage, 'error');
    } finally {
      generatingSummaryChapterId.value = null;
    }
    return success;
  };


  const clearChaptersForProject = (projectId) => {
    if (chaptersByProjectId[projectId]) {
      delete chaptersByProjectId[projectId];
    }
  };

  // Fonction pour réordonner les chapitres
  const reorderChapters = async (projectId, orderedIds) => {
    if (!projectId || !orderedIds || !Array.isArray(orderedIds)) {
      if (showSnackbar) showSnackbar("Données de réordonnancement invalides.", "error");
      return false;
    }
    submittingChapter.value = true; // Utiliser un état de chargement générique ou spécifique
    chapterError.value = null;
    try {
      const response = await fetch(`/api/projects/${projectId}/chapters/reorder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        body: JSON.stringify({ ordered_ids: orderedIds }),
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      // Après un réordonnancement réussi, re-fetch les chapitres pour ce projet
      // pour s'assurer que l'état local est synchronisé avec le backend.
      await fetchChaptersForProject(projectId);
      if (showSnackbar) showSnackbar('Chapitres réordonnés avec succès.');
      return true;
    } catch (error) {
      const errorMessage = handleApiError(error, "Erreur lors du réordonnancement des chapitres");
      chapterError.value = errorMessage;
      if (showSnackbar) showSnackbar(errorMessage, 'error');
      return false;
    } finally {
      submittingChapter.value = false;
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