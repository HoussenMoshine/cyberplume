<template>
  <v-navigation-drawer app permanent width="380">
    <ProjectToolbar
      :selectedProjectIds="selectedProjectIds"
      :selectedChapterIds="selectedChapterIds"
      @open-generate-scene-dialog="openGenerateSceneDialog"
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
              @load-scenes-if-needed="loadScenesIfNeeded"
              @select-chapter="(chapterId) => selectChapter(project.id, chapterId)"
              @toggle-selection="toggleChapterSelection"
              @handle-export="handleChapterExport"
              @open-add-scene="openAddSceneDialog"
              @open-delete="openDeleteConfirmDialog"
              @apply-suggestion="handleApplySuggestion"
              @request-add-chapter="handleChapterAddRequested"
              @request-update-chapter="handleChapterUpdateRequested"
              @request-generate-summary="handleChapterGenerateSummaryRequested"
              :showSnackbar="showSnackbar" 
            >
              <template v-for="chapter in chaptersByProjectId[project.id]" :key="`scenes-${chapter.id}`" #[`scene-list-${chapter.id}`]>
                 <SceneList
                   :chapter-id="chapter.id"
                   :scenes="scenesByChapterId[chapter.id]"
                   :loadingScenes="loadingScenes[chapter.id]"
                   :errorScenes="errorScenes[chapter.id]"
                   @reordered="(event) => onSceneDrop(chapter.id, event)"
                   @select-scene="selectScene"
                   @open-edit="openEditSceneDialog"
                   @open-delete="openDeleteConfirmDialog"
                 />
              </template>
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
      :loading="!!deletingProjectItemState?.id || deletingChapterItem.value || !!deletingSceneId"
      :deleteTarget="deleteTarget"
      :targetCounts="{ projects: selectedProjectIds.length, chapters: selectedChapterIds.length }"
      @close="closeDeleteConfirmDialog"
      @confirm="confirmDelete" 
    />
    <EditProjectDialog :show="showEditProjectDialog" :loading="submittingProject" :error="editProjectError" :initialTitle="editingProject?.title || ''" :initialDescription="editingProject?.description || ''" @close="closeEditProjectDialog" @save="submitEditProject" />

    <GenerateSceneDialog
      :show="showGenerateSceneDialog"
      :providers="providers"
      :availableModels="availableModels"
      :writingStyles="writingStyles"
      :providerInfo="providerInfo"
      :loadingModels="loadingModels"
      :errorLoadingModels="errorLoadingModels"
      :fetchModels="fetchModels"
      :selectDefaultModel="selectDefaultModel"
      :showSnackbar="showSnackbar"
      :project-characters="[]" 
      @close="showGenerateSceneDialog = false"
      @insert-content="handleInsertContent"
    />
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
import GenerateSceneDialog from './dialogs/GenerateSceneDialog.vue';
import AnalysisReportDialog from './dialogs/AnalysisReportDialog.vue';

import ProjectToolbar from './ProjectToolbar.vue';
import ProjectItem from './ProjectItem.vue';
import ChapterList from './ChapterList.vue';
import SceneList from './SceneList.vue';


import { useProjects } from '@/composables/useProjects.js';
import { useChapters } from '@/composables/useChapters.js';
import { useAIModels, writingStyles } from '@/composables/useAIModels.js';
import { useAnalysis } from '@/composables/useAnalysis.js';
import { useScenes } from '@/composables/useScenes.js';
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

const emit = defineEmits(['active-chapter-content-changed', 'active-scene-content-changed', 'ai-action-insert-content', 'chapter-selected']);


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
  fetchChaptersForProject, addChapter: addChapterComposable, 
  updateChapter: updateChapterComposable, deleteChapter: deleteChapterInternalComposable, 
  exportChapter, clearChaptersForProject,
  reorderChapters, generateChapterSummary 
} = useChapters(showSnackbar);

const {
    providerInfo, providers, availableModels, loadingModels, errorLoadingModels,
    fetchModels, selectDefaultModel
} = useAIModels(showSnackbar);

const {
    analysisResult, loadingAnalysis, errorAnalysis,
    triggerConsistencyAnalysis, clearConsistencyAnalysisState,
} = useAnalysis(showSnackbar);

const {
  scenesByChapterId, loadingScenes, errorScenes, submittingScene, deletingSceneId,
  fetchScenesForChapter, addScene, updateScene, deleteScene: deleteSceneComposable, reorderScenes
} = useScenes(showSnackbar);

// Utilisation de useCharacters SUPPRIMÉE
// const {
//     charactersByProjectId, fetchCharactersForProject, addCharacter, updateCharacter, deleteCharacter,
//     loadingCharacters: loadingAllCharacters, errorCharacters: errorAllCharacters
// } = useCharacters(showSnackbar);


// --- Gestion de la sélection et de l'état actif ---
const selectedProjectIds = ref([]);
const selectedChapterId = ref(null);
const selectedChapterIds = ref([]);
const activeProjectId = ref(null); 

const selectedSceneId = ref(null);


// --- Dialogs ---
const showAddProjectDialog = ref(false);
const addProjectError = ref(null);
const editingProject = ref(null);
const showEditProjectDialog = ref(false);
const editProjectError = ref(null);

const showDeleteConfirmDialog = ref(false);
const deleteTarget = ref(null); 

const showGenerateSceneDialog = ref(false);
const currentChapterIdForSceneGeneration = ref(null);

const showAnalysisDialog = ref(false);


// --- Characters ---
// const allCharacters = computed(() => { // SUPPRIMÉ pour l'instant
//     if (activeProjectId.value && charactersByProjectId[activeProjectId.value]) {
//         return charactersByProjectId[activeProjectId.value];
//     }
//     return [];
// });

// --- Logique de Projet ---
const fetchAllProjects = async () => {
  await fetchProjectsComposable();
};

const handleAddProjectDialogClose = () => {
  showAddProjectDialog.value = false;
  addProjectError.value = null;
};

const submitNewProject = async (projectData) => {
  addProjectError.value = null;
  const newProject = await addProjectComposable(projectData);
  if (newProject) {
    showAddProjectDialog.value = false;
  } else {
    addProjectError.value = "Erreur lors de l'ajout du projet."; 
  }
};

const openEditProjectDialog = (project) => {
  editingProject.value = { ...project };
  editProjectError.value = null;
  showEditProjectDialog.value = true;
};

const closeEditProjectDialog = () => {
  showEditProjectDialog.value = false;
  editingProject.value = null;
};

const submitEditProject = async (projectData) => {
  if (!editingProject.value || !editingProject.value.id) return;
  editProjectError.value = null;
  const success = await updateProjectComposable(editingProject.value.id, projectData);
  if (success) {
    showEditProjectDialog.value = false;
    editingProject.value = null;
  } else {
    editProjectError.value = "Erreur lors de la mise à jour du projet.";
  }
};

const handleProjectExport = async ({ projectId, format }) => {
  await exportProject(projectId, format);
};


// --- Logique de Chapitre ---
const handleChapterAddRequested = async ({ projectId, title }) => {
  const newChapter = await addChapterComposable(projectId, title);
  if (newChapter) {
    // La liste des chapitres est mise à jour par le re-fetch dans addChapterComposable.
    // Fermer le dialogue AddChapterDialog dans ChapterList si ce n'est pas déjà fait par ChapterList.
    // Pour l'instant, on assume que ChapterList gère la fermeture de son propre dialogue après l'emit.
  } else {
    showSnackbar("Erreur lors de l'ajout du chapitre.", "error");
  }
};

const handleChapterUpdateRequested = async (updatePayload) => {
  const success = await updateChapterComposable(updatePayload.id, { title: updatePayload.title, summary: updatePayload.summary });
  if (success) {
    // Le dialogue EditChapterDialog dans ChapterList devrait se fermer.
  } else {
    showSnackbar("Erreur lors de la mise à jour du chapitre.", "error");
  }
};

const handleChapterGenerateSummaryRequested = async (chapterId) => {
  await generateChapterSummary(chapterId); 
};


const selectChapter = (projectId, chapterId) => {
  selectedChapterId.value = chapterId;
  activeProjectId.value = projectId; 
  emit('chapter-selected', { projectId, chapterId });
  fetchScenesForChapter(chapterId); 
  // fetchCharactersForProject(projectId); // SUPPRIMÉ pour l'instant
};

const toggleProjectSelection = (projectId) => {
  const index = selectedProjectIds.value.indexOf(projectId);
  if (index > -1) {
    selectedProjectIds.value.splice(index, 1);
  } else {
    selectedProjectIds.value.push(projectId);
  }
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
  const orderedIds = newOrderedChapters.map(ch => ch.id);
  await reorderChapters(projectId, orderedIds);
};

const handleChapterExport = async ({ chapterId, format }) => {
  await exportChapter(chapterId, format);
};

// --- Logique de Scène ---
const openAddSceneDialog = (chapterId) => {
  console.log("Ouvrir dialogue ajout scène pour chapitre:", chapterId);
};

const selectScene = (sceneId, chapterId) => {
  selectedSceneId.value = sceneId;
  emit('active-scene-content-changed', { sceneId, chapterId });
};

const openEditSceneDialog = (scene) => {
  console.log("Ouvrir dialogue édition scène:", scene);
};

const onSceneDrop = async (chapterId, newOrderedScenes) => {
  const orderedIds = newOrderedScenes.map(s => s.id);
  await reorderScenes(chapterId, orderedIds);
};

const loadScenesIfNeeded = async (chapterId, isOpen) => {
    if (isOpen && chapterId && (!scenesByChapterId[chapterId] || scenesByChapterId[chapterId].length === 0)) {
        await fetchScenesForChapter(chapterId);
    }
};

// --- Logique de Suppression ---
const openDeleteConfirmDialog = (item, type) => {
  deleteTarget.value = { item, type, id: item.id };
  showDeleteConfirmDialog.value = true;
};

const closeDeleteConfirmDialog = () => {
  showDeleteConfirmDialog.value = false;
  deleteTarget.value = null;
};

const confirmDelete = async () => {
  if (!deleteTarget.value) return;
  const { type, id, item } = deleteTarget.value;
  let success = false;

  if (type === 'project') {
    success = await deleteProjectInternalComposable(id);
    if (success) selectedProjectIds.value = selectedProjectIds.value.filter(pid => pid !== id);
  } else if (type === 'chapter') {
    success = await deleteChapterInternalComposable(id);
    if (success) selectedChapterIds.value = selectedChapterIds.value.filter(cid => cid !== id);
  } else if (type === 'scene') {
    success = await deleteSceneComposable(id);
  }

  if (success) {
    showSnackbar(`${type.charAt(0).toUpperCase() + type.slice(1)} supprimé(e) avec succès.`);
  } else {
    showSnackbar(`Erreur lors de la suppression.`, 'error');
  }
  closeDeleteConfirmDialog();
};


// --- Génération de Scène ---
const openGenerateSceneDialog = (chapterId) => {
    currentChapterIdForSceneGeneration.value = chapterId;
    // if (activeProjectId.value) { // SUPPRIMÉ pour l'instant
    //     fetchCharactersForProject(activeProjectId.value);
    // }
    showGenerateSceneDialog.value = true;
};

const handleInsertContent = (content) => {
    emit('ai-action-insert-content', content);
    showGenerateSceneDialog.value = false; 
};

// --- Analyse ---
const openAnalysisDialog = async (project) => {
    analysisResult.value = null; 
    showAnalysisDialog.value = true;
    await triggerConsistencyAnalysis(project.id);
};
const closeAnalysisDialog = () => {
    showAnalysisDialog.value = false;
    clearConsistencyAnalysisState();
};

const handleApplySuggestion = (payload) => { 
  emit('active-chapter-content-changed', { 
    projectId: activeProjectId.value, 
    chapterId: payload.chapterId, 
    applySuggestion: payload.suggestion 
  });
};


// --- Cycle de vie ---
onMounted(() => {
  fetchAllProjects();
  fetchModels(); 
});

defineExpose({
  fetchChaptersForProject, 
});

</script>

<style scoped>
.v-navigation-drawer {
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
/* Autres styles si nécessaire */
</style>
