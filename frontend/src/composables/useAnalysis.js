import { ref } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

export function useAnalysis(showSnackbar) {
  // --- State for Consistency Analysis (Project Level) ---
  const analysisResult = ref(null); // { project_id, total_chapters, total_words, entities: [...], warnings: [...] }
  const loadingAnalysis = ref(false);
  const errorAnalysis = ref(null);

  // --- State for Content Analysis (Chapter Level) ---
  const chapterAnalysisResult = ref(null); // { chapter_id, stats: {...}, suggestions: [...] }
  const loadingChapterAnalysis = ref(false);
  const errorChapterAnalysis = ref(null);

  // --- Function for Consistency Analysis ---
  const triggerConsistencyAnalysis = async (projectId) => {
    if (!projectId) return;
    loadingAnalysis.value = true;
    errorAnalysis.value = null;
    analysisResult.value = null; // Reset previous results
    console.log(`useAnalysis: Triggering consistency analysis for project ${projectId}...`);
    try {
      const response = await fetch(`${config.apiUrl}/api/analyze/consistency`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        body: JSON.stringify({ project_id: projectId }),
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error;
      }
      analysisResult.value = await response.json(); // Store the result
      console.log(`useAnalysis: Consistency analysis complete for project ${projectId}.`);
    } catch (error) {
      // Log détaillé de l'erreur
      console.error("Error during consistency analysis:", error);
      if (error.data) {
        console.error("Error details (consistency):", JSON.stringify(error.data, null, 2));
      }
      errorAnalysis.value = handleApiError(error, `analyse de cohérence du projet ${projectId}`);
      analysisResult.value = null; // Ensure result is null on error
      if (showSnackbar) showSnackbar(errorAnalysis.value, 'error'); // Show error in snackbar as well
    } finally {
      loadingAnalysis.value = false;
    }
  };

  // --- Function for Content Analysis ---
  const triggerChapterAnalysis = async (chapterId, provider, model = null) => {
    if (!chapterId || !provider) {
        // Log si le provider est manquant
        console.error(`useAnalysis: Cannot trigger chapter analysis for chapter ${chapterId}. Provider is missing or invalid:`, provider);
        const errorMsg = `Fournisseur IA manquant ou invalide pour l'analyse du chapitre ${chapterId}.`;
        errorChapterAnalysis.value = errorMsg;
        if (showSnackbar) showSnackbar(errorMsg, 'error');
        return; // Ne pas continuer si le provider est invalide
    }
    loadingChapterAnalysis.value = true;
    errorChapterAnalysis.value = null;
    chapterAnalysisResult.value = null; // Reset previous results
    console.log(`useAnalysis: Triggering content analysis for chapter ${chapterId} using provider: ${provider}, model: ${model}`);
    try {
      const payload = { provider: provider };
      if (model) {
        payload.model = model;
      }
      const response = await fetch(`${config.apiUrl}/api/chapters/${chapterId}/analyze-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
        body: JSON.stringify(payload), // Send provider and optional model
      });
      if (!response.ok) {
        const error = new Error(`HTTP error! status: ${response.status}`);
        try { error.data = await response.json(); } catch (e) { /* ignore */ }
        throw error; // Lancer l'erreur pour la capture ci-dessous
      }
      chapterAnalysisResult.value = await response.json(); // Store the result
      console.log(`useAnalysis: Content analysis complete for chapter ${chapterId}. Found ${chapterAnalysisResult.value?.suggestions?.length || 0} suggestions.`);
    } catch (error) {
      // Log détaillé de l'erreur 422 ou autre
      console.error(`Error during chapter content analysis (chapter ${chapterId}):`, error);
      if (error.data) {
        console.error(`Error details (chapter ${chapterId}):`, JSON.stringify(error.data, null, 2)); // Log des détails de l'erreur FastAPI
      }
      errorChapterAnalysis.value = handleApiError(error, `analyse de contenu du chapitre ${chapterId}`);
      chapterAnalysisResult.value = null; // Ensure result is null on error
      if (showSnackbar) showSnackbar(errorChapterAnalysis.value, 'error'); // Show error in snackbar as well
    } finally {
      loadingChapterAnalysis.value = false;
    }
  };

  // --- Functions to clear state ---
  const clearConsistencyAnalysisState = () => {
      analysisResult.value = null;
      errorAnalysis.value = null;
      // loadingAnalysis is reset in the finally block
  };

  const clearChapterAnalysisState = () => {
      chapterAnalysisResult.value = null;
      errorChapterAnalysis.value = null;
      // loadingChapterAnalysis is reset in the finally block
  };

  return {
    // Consistency Analysis
    analysisResult,
    loadingAnalysis,
    errorAnalysis,
    triggerConsistencyAnalysis,
    clearConsistencyAnalysisState, // Renamed for clarity

    // Chapter Content Analysis
    chapterAnalysisResult,
    loadingChapterAnalysis,
    errorChapterAnalysis,
    triggerChapterAnalysis,
    clearChapterAnalysisState,
  };
}