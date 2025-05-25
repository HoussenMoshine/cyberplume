import { ref, watch, onUnmounted, computed } from 'vue';
import axios from 'axios';
import { debounce } from 'lodash-es'; // Utiliser debounce pour la sauvegarde auto
import { config } from '@/config.js'; // config.apiKey est toujours utilisé
import { handleApiError } from '@/utils/errorHandler.js';

// Délai pour la sauvegarde automatique (en millisecondes)
const AUTOSAVE_DELAY = 2000;

export function useSceneContent(selectedSceneIdRef, editorRef) {
  const isLoading = ref(false);
  const isSaving = ref(false);
  const loadingError = ref(null);
  const savingError = ref(null);
  const lastSavedContent = ref(''); // Stocker le contenu lors du dernier chargement/sauvegarde réussi
  const currentContent = ref(''); // Contenu actuel de l'éditeur
  // NOUVEAU: State pour stocker les personnages de la scène chargée
  const loadedSceneCharacters = ref([]);

  // --- Computed Property pour détecter les changements non sauvegardés ---
  const hasUnsavedChanges = computed(() => {
    // Comparer le contenu actuel avec le dernier contenu sauvegardé
    // S'assurer que l'éditeur est prêt et a du contenu
    if (!editorRef.value || !editorRef.value.isEditable) return false;
    const editorHtml = editorRef.value.getHTML();
    // Considérer le contenu initial vide comme non modifié
    // CORRECTION: Remplacer && par &&
    if (lastSavedContent.value === '' && (editorHtml === '<p></p>' || editorHtml === '')) { // Correction: &&
        return false;
    }
    return editorHtml !== lastSavedContent.value;
  });

  // --- Fonction pour charger le contenu et les personnages d'une scène ---
  const fetchSceneContent = async (sceneId) => {
    if (!sceneId) {
      if (editorRef.value) {
        editorRef.value.commands.setContent('<p>Sélectionnez une scène ou un chapitre...</p>', false); // false pour ne pas déclencher d'événement update
        editorRef.value.setEditable(false);
      }
      lastSavedContent.value = '';
      currentContent.value = '';
      loadedSceneCharacters.value = []; // Réinitialiser les personnages
      return;
    }

    
    isLoading.value = true;
    loadingError.value = null;
    loadedSceneCharacters.value = []; // Réinitialiser avant chargement
    try {

      // L'API GET /api/scenes/{sceneId} renvoie déjà les personnages grâce à SceneRead
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      const response = await axios.get(`/api/scenes/${sceneId}`, { headers: { 'x-api-key': config.apiKey } });
      const content = response.data.content || '<p></p>'; // Contenu par défaut si null
      const characters = response.data.characters || []; // Récupérer les personnages

      if (editorRef.value) {
        editorRef.value.commands.setContent(content, false); // Mettre à jour l'éditeur sans déclencher 'update'
        editorRef.value.setEditable(true); // Rendre éditable
        
      }
      lastSavedContent.value = content; // Mettre à jour le contenu sauvegardé
      currentContent.value = content; // Mettre à jour le contenu actuel
      loadedSceneCharacters.value = characters; // Stocker les personnages chargés
      

    } catch (error) {
      console.error(`useSceneContent: Error fetching scene ${sceneId}:`, error);
      loadingError.value = handleApiError(error, 'Erreur chargement scène');
      if (editorRef.value) {
        editorRef.value.commands.setContent('<p>Erreur de chargement...</p>', false);
        editorRef.value.setEditable(false);
      }
      lastSavedContent.value = '';
      currentContent.value = '';
      loadedSceneCharacters.value = []; // Réinitialiser en cas d'erreur
    } finally {
      isLoading.value = false;
    }
  };

  // --- Fonction pour sauvegarder le contenu de la scène actuelle ---
  const saveCurrentScene = async (sceneId, contentToSave) => {
    if (!sceneId) return false; // Ne rien faire si aucune scène n'est sélectionnée

    
    isSaving.value = true;
    savingError.value = null;
    try {
      // L'API PUT /api/scenes/{sceneId} ne met à jour que le contenu (et titre/ordre si inclus)
      // MODIFIÉ: Utilisation d'un chemin relatif pour l'API
      await axios.put(`/api/scenes/${sceneId}`, {
        content: contentToSave,
      }, { headers: { 'x-api-key': config.apiKey } });
      
      lastSavedContent.value = contentToSave; // Mettre à jour après sauvegarde réussie
      return true; // Indiquer le succès
    } catch (error) {
      console.error(`useSceneContent: Error saving scene ${sceneId}:`, error);
      savingError.value = handleApiError(error, 'Erreur sauvegarde scène');
      return false; // Indiquer l'échec
    } finally {
      isSaving.value = false;
    }
  };

  // --- Sauvegarde automatique (debounced) ---
  const debouncedSave = debounce(async () => {
    // CORRECTION: Remplacer && par &&
    if (selectedSceneIdRef.value && hasUnsavedChanges.value && editorRef.value) { // Correction: &&
      
      await saveCurrentScene(selectedSceneIdRef.value, editorRef.value.getHTML());
    }
  }, AUTOSAVE_DELAY);

  // --- Fonction pour déclencher la sauvegarde (manuelle ou via debounce) ---
  const saveCurrentSceneIfNeeded = async (isManualSave = false) => {
    if (!selectedSceneIdRef.value || !editorRef.value || !hasUnsavedChanges.value) {
      
      return; // Pas besoin de sauvegarder
    }

    const contentToSave = editorRef.value.getHTML();

    if (isManualSave) {
      
      debouncedSave.cancel(); // Annuler toute sauvegarde automatique en attente
      await saveCurrentScene(selectedSceneIdRef.value, contentToSave);
    } else {
      // Pour la sauvegarde auto (blur/debounce), on utilise la version debounced
      debouncedSave();
    }
  };

  // --- Watcher pour charger le contenu quand l'ID de la scène change ---
  watch(selectedSceneIdRef, (newId, oldId) => {
    
    // Si on passe d'une scène à une autre, sauvegarder l'ancienne avant de charger la nouvelle
    // CORRECTION: Remplacer && par &&
    if (oldId && editorRef.value && hasUnsavedChanges.value) { // Correction: &&
      
      debouncedSave.cancel(); // Annuler debounce
      saveCurrentScene(oldId, editorRef.value.getHTML()); // Sauvegarde immédiate
    }
    fetchSceneContent(newId);
  }, { immediate: true }); // immediate: true pour charger au montage si un ID est déjà présent

  // --- Écouter les changements dans l'éditeur pour la sauvegarde auto ---
  watch(editorRef, (newEditor) => {
    if (newEditor) {
      newEditor.off('update'); // Détacher l'ancien listener pour éviter les doublons
      newEditor.on('update', () => {
        // Mettre à jour currentContent à chaque modification
        currentContent.value = newEditor.getHTML();
        // Déclencher la sauvegarde debounced si une scène est sélectionnée
        if (selectedSceneIdRef.value) {
            debouncedSave();
        }
      });
    }
  }, { immediate: true }); // immediate: true pour attacher le listener si l'éditeur est déjà là


  // --- Nettoyage ---
  onUnmounted(() => {
    debouncedSave.cancel(); // Annuler la sauvegarde auto si le composant est détruit
    if (editorRef.value) {
        editorRef.value.off('update'); // Nettoyer le listener
    }
    // Optionnel: Sauvegarder une dernière fois si nécessaire ? À évaluer.
    // if (selectedSceneIdRef.value && hasUnsavedChanges.value && editorRef.value) {
    //   saveCurrentScene(selectedSceneIdRef.value, editorRef.value.getHTML());
    // }
  });

  return {
    isLoading,
    isSaving,
    loadingError,
    savingError,
    hasUnsavedChanges,
    loadSceneContent: fetchSceneContent, // Exposer sous le nom attendu par EditorComponent
    saveCurrentSceneIfNeeded, // Exposer la fonction pour sauvegarde manuelle/blur
    // NOUVEAU: Exposer les personnages chargés
    loadedSceneCharacters: computed(() => loadedSceneCharacters.value), // Exposer en lecture seule
  };
}