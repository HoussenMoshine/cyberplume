<template>
  <v-navigation-drawer app permanent width="380">
    <ProjectToolbar
      :selectedProjectIds="selectedProjectIds"
      :selectedChapterIds="selectedChapterIds"
      @open-add-project-dialog="showAddProjectDialog = true"
      @open-delete-confirm-dialog="openDeleteConfirmDialog"
    />

    <v-divider></v-divider>

    <v-container fluid class="pa-2">
      <v-progress-linear v-if="loadingProjects" indeterminate color="primary" class="mb-2"></v-progress-linear>
      <v-alert v-if="errorProjects" type="error" density="compact" variant="tonal" class="mb-2">
        {{ errorProjects }}
      </v-alert>

      <div v-if="!loadingProjects && projects.length > 0">
        <ProjectItem
          v-for="project in projects"
          :key="project.id"
          :project="project"
          :selectedProjectIds="selectedProjectIds"
          :exportingProjectId="exportingProjectId"
          :exportingFormat="exportingFormat"
          @toggle-selection="toggleProjectSelection"
          @open-edit="openEditProjectDialog"
          @open-analysis="openAnalysisDialog"
          @handle-export="handleProjectExport"
          @open-delete="openDeleteConfirmDialog"
          @chapters-requested="fetchChaptersForProject"
        >
          <template v-slot:chapter-list>
            <ChapterList
              :project-id="project.id"
              :chapters="chaptersByProjectId[project.id]"
              :loading="loadingChapters[project.id]" 
              :error="errorChapters[project.id]" 
              :selectedChapterId="selectedChapterId"
              :selectedChapterIds="selectedChapterIds"
              :exportingChapterId="exportingChapterIdComposable" 
              :exportingFormat="exportingFormat"
              :submittingChapter="submittingChapter" 
              :generatingSummaryChapterId="generatingSummaryChapterId" 
              @reordered="(event) => onChapterDrop(project.id, event)"
              @select-chapter="(chapterId) => selectChapter(project.id, chapterId)"
              @toggle-selection="toggleChapterSelection"
              @handle-export="handleChapterExport"
              @open-delete="openDeleteConfirmDialog"
              @apply-suggestion="handleApplySuggestion"
              @request-add-chapter="handleChapterAddRequested"
              @request-update-chapter="handleChapterUpdateRequested"
              @request-generate-summary="handleChapterGenerateSummaryRequested"
              :showSnackbar="showSnackbar" 
            >
            </ChapterList>
          </template>
        </ProjectItem>
      </div>

      <v-list-item v-if="!loadingProjects && projects.length === 0">
        <v-list-item-title class="text-center text-disabled font-italic mt-4">Aucun projet trouvé.</v-list-item-title>
      </v-list-item>
    </v-container>


    <AddProjectDialog :show="showAddProjectDialog" :loading="submittingProject" :error="addProjectError" @close="handleAddProjectDialogClose" @save="submitNewProject" />
    <DeleteConfirmDialog
      :show="showDeleteConfirmDialog"
      :loading="!!deletingProjectItemState?.id || deletingChapterItem.value"
      :deleteTarget="deleteTarget"
      :targetCounts="{ projects: selectedProjectIds.length, chapters: selectedChapterIds.length }"
      @close="closeDeleteConfirmDialog"
      @confirm="confirmDelete" 
    />
    <EditProjectDialog :show="showEditProjectDialog" :loading="submittingProject" :error="editProjectError" :initialTitle="editingProject?.title || ''" :initialDescription="editingProject?.description || ''" @close="closeEditProjectDialog" @save="submitEditProject" />

    <AnalysisReportDialog
        :show="showAnalysisDialog"
        :loading="loadingAnalysis"
        :error="errorAnalysis"
        :analysisResult="analysisResult"
        @close="closeAnalysisDialog"
    />

    <v-snackbar
      v-model="snackbarVisible"
      :color="snackbarColor"
      :timeout="3000"
      location="bottom right"
      variant="elevated"
    >
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbarVisible = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch, toRefs } from 'vue';
import axios from 'axios';
import AddProjectDialog from './dialogs/AddProjectDialog.vue';
import DeleteConfirmDialog from './dialogs/DeleteConfirmDialog.vue';
import EditProjectDialog from './dialogs/EditProjectDialog.vue';
import AnalysisReportDialog from './dialogs/AnalysisReportDialog.vue';

import ProjectToolbar from './ProjectToolbar.vue';
import ProjectItem from './ProjectItem.vue';
import ChapterList from './ChapterList.vue';


import { useProjects } from '@/composables/useProjects.js';
import { useChapters } from '@/composables/useChapters.js';
import { useAIModels, writingStyles } from '@/composables/useAIModels.js';
import { useAnalysis } from '@/composables/useAnalysis.js';
// import { useCharacters } from '@/composables/useCharacters.js'; // SUPPRIMÉ

import {
  VNavigationDrawer, VToolbar, VToolbarTitle, VDivider, VList, VListItem, VListItemTitle, VListItemAction, VListSubheader,
  VBtn, VIcon, VProgressLinear, VAlert, VDialog, VCard, VCardTitle, VCardText, VTextField, VCardActions,
  VSpacer, VContainer, VRow, VCol, VCheckboxBtn, VSnackbar, VMenu, VSelect, VTextarea,
  VTooltip, VChip, VListGroup, VProgressCircular
} from 'vuetify/components';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

const props = defineProps({
  currentAiProvider: String,
  currentAiModel: String,
  currentAiStyle: String,
  currentCustomAiDescription: String,
});

const emit = defineEmits(['active-chapter-content-changed', 'ai-action-insert-content', 'chapter-selected']);


const snackbarVisible = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');
const showSnackbar = (text, color = 'success', timeout = 3000) => {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbarVisible.value = true;
};

const {
  projects, loadingProjects, errorProjects, submittingProject, deletingItem: deletingProjectItemState,
  exportingProjectId, exportingFormat, exportError,
  fetchProjects: fetchProjectsComposable, addProject: addProjectComposable, 
  updateProject: updateProjectComposable, deleteProject: deleteProjectInternalComposable,
  exportProject, getProjectById
} = useProjects(showSnackbar);

const {
  chaptersByProjectId, loadingChapters, errorChapters, 
  submittingChapter, 
  deletingChapterItem, 
  exportingChapterId: exportingChapterIdComposable, 
  generatingSummaryChapterId, 
  fetchChaptersForProject: fetchChaptersComposable, 
  addChapter: addChapterComposable, 
  updateChapter: updateChapterComposable, 
  deleteChapter: deleteChapterComposable, 
  reorderChapters: reorderChaptersComposable,
  exportChapter: exportChapterComposable,
  generateChapterSummary: generateChapterSummaryComposable,
  applySuggestionToChapterContent,
} = useChapters(showSnackbar);


const { 
  providers, 
  availableModels, 
  providerInfo, 
  loadingModels, 
  errorLoadingModels, 
  fetchModels, 
  selectDefaultModel 
} = useAIModels(showSnackbar, props);

const {
    analysisResult,
    loadingAnalysis,
    errorAnalysis,
    getProjectAnalysis,
    getChapterAnalysis,
    getStyleAnalysis,
    applySuggestionToChapter: applySuggestionToChapterAnalysis, // Renommer pour éviter conflit
} = useAnalysis(showSnackbar);


// --- State (local) ---
const activeProjectId = ref(null); // Pour suivre le projet actuellement actif/développé
const selectedChapterId = ref(null); // ID du chapitre sélectionné pour l'édition
const selectedProjectIds = ref([]); // Pour la sélection multiple de projets
const selectedChapterIds = ref([]); // Pour la sélection multiple de chapitres


// Dialogs visibility
const showAddProjectDialog = ref(false);
const showDeleteConfirmDialog = ref(false);
const deleteTarget = ref({ type: null, item: null }); // type: 'project' ou 'chapter'
const showEditProjectDialog = ref(false);
const editingProject = ref(null); // Projet en cours d'édition
const addProjectError = ref(null);
const editProjectError = ref(null);

const showAnalysisDialog = ref(false);


// --- Cycle de vie ---
onMounted(async () => {
  await fetchProjectsComposable();
  // Optionnel: charger les chapitres du premier projet si la liste n'est pas vide
  if (projects.value.length > 0) {
    // activeProjectId.value = projects.value[0].id; // Décommentez si vous voulez un projet actif par défaut
    // await fetchChaptersForProject(projects.value[0].id); // Décommentez pour charger les chapitres
  }
});

// --- Gestion des Projets ---
const fetchChaptersForProject = async (projectId) => {
  activeProjectId.value = projectId;
  await fetchChaptersComposable(projectId);
};

const submitNewProject = async (projectData) => {
  addProjectError.value = null;
  const newProject = await addProjectComposable(projectData);
  if (newProject) {
    handleAddProjectDialogClose();
  } else {
    addProjectError.value = "Erreur lors de l'ajout du projet."; // Ou utiliser l'erreur de useProjects
  }
};

const handleAddProjectDialogClose = () => {
  showAddProjectDialog.value = false;
  addProjectError.value = null;
};

const openEditProjectDialog = (project) => {
  editingProject.value = { ...project }; // Copie pour éviter la modification directe
  editProjectError.value = null;
  showEditProjectDialog.value = true;
};

const closeEditProjectDialog = () => {
  showEditProjectDialog.value = false;
  editingProject.value = null;
  editProjectError.value = null;
};

const submitEditProject = async (projectData) => {
  editProjectError.value = null;
  if (!editingProject.value) return;
  const success = await updateProjectComposable(editingProject.value.id, projectData);
  if (success) {
    closeEditProjectDialog();
  } else {
    editProjectError.value = "Erreur lors de la modification du projet."; // Ou utiliser l'erreur de useProjects
  }
};

const toggleProjectSelection = (projectId) => {
  const index = selectedProjectIds.value.indexOf(projectId);
  if (index > -1) {
    selectedProjectIds.value.splice(index, 1);
  } else {
    selectedProjectIds.value.push(projectId);
  }
};

const handleProjectExport = async (projectId, format) => {
    await exportProject(projectId, format);
};


// --- Gestion des Chapitres ---
const selectChapter = (projectId, chapterId) => {
  selectedChapterId.value = chapterId;
  activeProjectId.value = projectId; // S'assurer que le projet parent est actif
  emit('chapter-selected', { projectId, chapterId });
  // fetchCharactersForProject(projectId); // SUPPRIMÉ pour l'instant
};

const toggleChapterSelection = (chapterId) => {
  const index = selectedChapterIds.value.indexOf(chapterId);
  if (index > -1) {
    selectedChapterIds.value.splice(index, 1);
  } else {
    selectedChapterIds.value.push(chapterId);
  }
};

const onChapterDrop = async (projectId, newOrderedChapters) => {
  const orderedIds = newOrderedChapters.map(c => c.id);
  await reorderChaptersComposable(projectId, orderedIds);
};

const handleChapterExport = async (chapterId, format) => {
    await exportChapterComposable(chapterId, format);
};

const handleChapterAddRequested = async (projectId, chapterData) => {
    await addChapterComposable(projectId, chapterData);
};

const handleChapterUpdateRequested = async (chapterId, chapterUpdateData) => {
    await updateChapterComposable(chapterId, chapterUpdateData);
};

const handleChapterGenerateSummaryRequested = async (chapterId) => {
    await generateChapterSummaryComposable(chapterId);
};


// --- Suppression (Projets & Chapitres) ---
const openDeleteConfirmDialog = (type, item) => {
  deleteTarget.value = { type, item };
  showDeleteConfirmDialog.value = true;
};

const closeDeleteConfirmDialog = () => {
  showDeleteConfirmDialog.value = false;
  deleteTarget.value = { type: null, item: null };
};

const confirmDelete = async () => {
  const { type, item } = deleteTarget.value;
  let success = false;

  if (type === 'project-selection' && selectedProjectIds.value.length > 0) {
    // Logique pour supprimer plusieurs projets sélectionnés
    // Pour l'instant, on va boucler, mais une API de suppression en masse serait mieux
    let allSucceeded = true;
    for (const projectId of selectedProjectIds.value) {
      const result = await deleteProjectInternalComposable(projectId);
      if (!result) allSucceeded = false;
    }
    success = allSucceeded;
    if (success) selectedProjectIds.value = [];

  } else if (type === 'chapter-selection' && selectedChapterIds.value.length > 0) {
     // Logique pour supprimer plusieurs chapitres sélectionnés
    let allSucceeded = true;
    for (const chapterId of selectedChapterIds.value) {
      const result = await deleteChapterComposable(chapterId);
      if (!result) allSucceeded = false;
    }
    success = allSucceeded;
    if (success) selectedChapterIds.value = [];

  } else if (type === 'project' && item) {
    success = await deleteProjectInternalComposable(item.id);
    if (success) selectedProjectIds.value = selectedProjectIds.value.filter(pid => pid !== item.id);
  } else if (type === 'chapter' && item) {
    success = await deleteChapterComposable(item.id);
    if (success) selectedChapterIds.value = selectedChapterIds.value.filter(cid => cid !== item.id);
  }

  if (success) {
    showSnackbar(`${type === 'project' || type === 'project-selection' ? 'Projet(s)' : 'Chapitre(s)'} supprimé(s) avec succès.`, 'success');
  } else {
    showSnackbar(`Erreur lors de la suppression.`, 'error');
  }
  closeDeleteConfirmDialog();
};


// --- Analyse ---
const openAnalysisDialog = async (itemType, itemId) => {
    errorAnalysis.value = null;
    analysisResult.value = null; // Réinitialiser avant de charger
    showAnalysisDialog.value = true;

    if (itemType === 'project') {
        await getProjectAnalysis(itemId);
    } else if (itemType === 'chapter') {
        await getChapterAnalysis(itemId);
    } else if (itemType === 'style') {
        // Pour l'analyse de style, itemId pourrait être l'ID du chapitre ou du projet
        // ou vous pourriez avoir une logique différente pour obtenir le texte.
        // Pour l'instant, supposons que c'est l'ID du chapitre.
        const chapter = getChapterById(itemId); // Vous devrez peut-être implémenter getChapterById dans useChapters
        if (chapter && chapter.content) {
             await getStyleAnalysis(chapter.content);
        } else {
            errorAnalysis.value = "Contenu du chapitre non trouvé pour l'analyse de style.";
        }
    }
};

const closeAnalysisDialog = () => {
    showAnalysisDialog.value = false;
    analysisResult.value = null;
    errorAnalysis.value = null;
};

const handleApplySuggestion = async (suggestionData) => {
  if (selectedChapterId.value) {
    // Utiliser la fonction applySuggestionToChapterContent de useChapters
    const success = await applySuggestionToChapterContent(selectedChapterId.value, suggestionData.texte_modifie);
    if (success) {
      showSnackbar('Suggestion appliquée avec succès au chapitre.', 'success');
      // L'état du contenu du chapitre devrait être mis à jour par useChapters,
      // et EditorComponent devrait réagir à ce changement.
      // On peut aussi émettre un événement pour forcer un re-fetch si nécessaire.
      emit('active-chapter-content-changed', { chapterId: selectedChapterId.value, content: suggestionData.texte_modifie });

    } else {
      showSnackbar('Erreur lors de l\'application de la suggestion.', 'error');
    }
  } else {
    showSnackbar('Aucun chapitre sélectionné pour appliquer la suggestion.', 'warning');
  }
};


// --- Watchers ---
watch(projects, (newProjects) => {
  // Si un projet actif n'existe plus (ex: supprimé), réinitialiser
  if (activeProjectId.value && !newProjects.some(p => p.id === activeProjectId.value)) {
    activeProjectId.value = null;
    selectedChapterId.value = null; // Désélectionner aussi le chapitre
    emit('chapter-selected', { projectId: null, chapterId: null });
  }
}, { deep: true });

watch(() => chaptersByProjectId, (newChaptersMap) => {
  // Si un chapitre sélectionné n'existe plus dans le projet actif, réinitialiser
  if (activeProjectId.value && selectedChapterId.value) {
    const chaptersOfActiveProject = newChaptersMap[activeProjectId.value];
    if (chaptersOfActiveProject && !chaptersOfActiveProject.some(c => c.id === selectedChapterId.value)) {
      selectedChapterId.value = null;
      emit('chapter-selected', { projectId: activeProjectId.value, chapterId: null });
    }
  }
}, { deep: true });


// Exposer les fonctions/états nécessaires au template
defineExpose({
  fetchProjects: fetchProjectsComposable,
  fetchChaptersForProject,
  // ... autres si nécessaire pour des tests ou accès parent
});

</script>

<style scoped>
.v-navigation-drawer {
  border-right: 1px solid rgba(0,0,0,0.12);
}
.project-item-container {
  margin-bottom: 8px;
}
.text-disabled {
  color: #9e9e9e !important; /* Gris pour le texte désactivé */
}
</style>
