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
            <!-- Log retiré -->
            <ChapterList
              :project-id="project.id"
              :chapters="chaptersByProjectId[project.id]"
              :loadingChapters="loadingChapters[project.id]"
              :errorChapters="errorChapters[project.id]"
              :selectedChapterId="selectedChapterId"
              :selectedChapterIds="selectedChapterIds"
              :exportingChapterId="exportingChapterId"
              :exportingFormat="exportingFormat"
              @reordered="(event) => onChapterDrop(project.id, event)"
              @load-scenes-if-needed="loadScenesIfNeeded"
              @select-chapter="(chapterId) => selectChapter(project.id, chapterId)"
              @toggle-selection="toggleChapterSelection"
              @handle-export="handleChapterExport"
              @open-add-scene="openAddSceneDialog"
              @open-delete="openDeleteConfirmDialog"
              @apply-suggestion="handleApplySuggestion"
              @add-chapter-requested="(title) => handleAddChapterRequest(project.id, title)"
              @chapter-updated="handleChapterUpdated"
              :selected-ai-provider="props.currentAiProvider"
              :selected-ai-model="props.currentAiModel"
              :selected-ai-style="props.currentAiStyle"
              :custom-ai-description="props.currentCustomAiDescription"
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
      :loading="!!deletingProjectItem?.id || deletingChapterItem.value || !!deletingSceneId"
      :deleteTarget="deleteTarget"
      :targetCounts="{ projects: selectedProjectIds.length, chapters: selectedChapterIds.length }"
      @close="closeDeleteConfirmDialog"
      @confirm="() => { console.log('[ProjectManager] @confirm event received via inline arrow function'); confirmDelete(); }"
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
      :project-characters="allCharacters"
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
import { ref, reactive, onMounted, computed, watch } from 'vue';
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

import {
  VNavigationDrawer, VToolbar, VToolbarTitle, VDivider, VList, VListItem, VListItemTitle, VListItemAction, VListSubheader,
  VBtn, VIcon, VProgressLinear, VAlert, VDialog, VCard, VCardTitle, VCardText, VTextField, VCardActions,
  VSpacer, VContainer, VRow, VCol, VCheckboxBtn, VSnackbar, VMenu, VSelect, VTextarea,
  VTooltip, VChip, VListGroup, VProgressCircular
} from 'vuetify/components';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';

const snackbarVisible = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');
const showSnackbar = (text, color = 'success', timeout = 3000) => {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbarVisible.value = true;
};

const {
  projects, loadingProjects, errorProjects, submittingProject, deletingItem: deletingProjectItem,
  exportingProjectId, exportingFormat, exportError,
  fetchProjects: fetchProjectsComposable, addProject, updateProject, deleteProject: deleteProjectComposable,
  exportProject, getProjectById
} = useProjects(showSnackbar);

const {
  chaptersByProjectId, loadingChapters, errorChapters, submittingChapter, deletingChapterItem, exportingChapterId,
  fetchChaptersForProject, addChapter, updateChapter, deleteChapter: deleteChapterComposable, exportChapter, clearChaptersForProject,
  reorderChapters
} = useChapters(showSnackbar);

const {
    providerInfo, providers, availableModels, loadingModels, errorLoadingModels,
    fetchModels, selectDefaultModel
} = useAIModels(showSnackbar);

const {
    analysisResult, loadingAnalysis, errorAnalysis,
    triggerConsistencyAnalysis, clearConsistencyAnalysisState,
    chapterAnalysisResult, loadingChapterAnalysis, errorChapterAnalysis,
    triggerChapterAnalysis, clearChapterAnalysisState
} = useAnalysis(showSnackbar);

const {
  scenesByChapterId, loadingScenes, errorScenes, submittingScene, deletingSceneId,
  fetchScenesForChapter, addScene, updateScene, deleteScene,
  reorderScenes
} = useScenes(showSnackbar);

const allCharacters = ref([]);

const selectedProjectIds = ref([]);
const selectedChapterIds = ref([]);
const selectedChapterId = ref(null);
const selectedSceneId = ref(null);

const showAddProjectDialog = ref(false);
const addProjectError = ref(null);

const showDeleteConfirmDialog = ref(false);
const deleteTarget = ref({ type: '', name: '' });
const itemToDelete = ref(null);

const showEditProjectDialog = ref(false);
const editingProject = ref(null);
const editProjectError = ref(null);

const showGenerateSceneDialog = ref(false);
const chapterForSceneGeneration = ref(null);

const showAnalysisDialog = ref(false);


const props = defineProps({
  currentAiProvider: { type: String, default: null },
  currentAiModel: { type: String, default: null },
  currentAiStyle: { type: String, default: null },
  currentCustomAiDescription: { type: String, default: null },
});
const emit = defineEmits(['chapter-selected', 'scene-selected', 'insert-generated-content', 'apply-suggestion-to-editor']);


const fetchAllCharactersForProject = async (projectId) => {
  if (!projectId) {
    allCharacters.value = [];
    return;
  }
  try {
    const response = await axios.get(`${config.apiUrl}/api/characters`, {
      headers: { 'x-api-key': config.apiKey }
    });
    allCharacters.value = response.data.map(char => ({ id: char.id, name: char.name, description: char.description, backstory: char.backstory }));
  } catch (error) {
    console.error("Erreur lors de la récupération des personnages:", error);
    showSnackbar(handleApiError(error, "récupération des personnages"), 'error');
    allCharacters.value = [];
  }
};


onMounted(async () => {
  // console.log('ProjectManager: onMounted - Fetching projects...'); // Log retiré
  await fetchProjectsComposable();
  // console.log('ProjectManager: onMounted - Projects fetched:', JSON.parse(JSON.stringify(projects.value))); // Log retiré
  if (projects.value.length > 0) {
    // console.log('ProjectManager: onMounted - Fetching chapters for all loaded projects...'); // Log retiré
    for (const project of projects.value) {
      // console.log(`ProjectManager: onMounted - Requesting chapters for project ID: ${project.id}`); // Log retiré
      await fetchChaptersForProject(project.id);
    }
    // console.log('ProjectManager: onMounted - Finished fetching initial chapters.'); // Log retiré
    await fetchAllCharactersForProject(projects.value[0].id);
  }
});

// Fonction de log retirée
// const logChapterData = (projectId) => { ... };

const handleAddProjectDialogClose = () => {
  showAddProjectDialog.value = false;
  addProjectError.value = null;
};

const submitNewProject = async (projectData) => {
  const success = await addProject(projectData);
  if (success) {
    handleAddProjectDialogClose();
    if (projects.value.find(p => p.title === projectData.title)) {
        const newProject = projects.value.find(p => p.title === projectData.title); 
        if (newProject) {
            await fetchChaptersForProject(newProject.id);
            if (projects.value.length === 1) {
                 await fetchAllCharactersForProject(newProject.id);
            }
        }
    }
  } else {
    addProjectError.value = "Erreur lors de l'ajout du projet.";
  }
};

const openEditProjectDialog = (project) => {
  editingProject.value = project;
  editProjectError.value = null;
  showEditProjectDialog.value = true;
};

const closeEditProjectDialog = () => {
  showEditProjectDialog.value = false;
  editingProject.value = null;
  editProjectError.value = null;
};

const submitEditProject = async (projectData) => {
  if (!editingProject.value) return;
  const success = await updateProject(editingProject.value.id, projectData);
  if (success) {
    closeEditProjectDialog();
  } else {
    editProjectError.value = "Erreur lors de la mise à jour du projet.";
  }
};

const toggleProjectSelection = (projectId) => {
  const index = selectedProjectIds.value.indexOf(projectId);
  if (index > -1) {
    selectedProjectIds.value.splice(index, 1);
  } else {
    selectedProjectIds.value.push(projectId);
  }
  if (selectedProjectIds.value.length === 1) {
    fetchAllCharactersForProject(selectedProjectIds.value[0]);
  } else {
    allCharacters.value = [];
  }
};

const selectChapter = (projectId, chapterId) => {
  // console.log(`ProjectManager: selectChapter - projectId: ${projectId}, chapterId: ${chapterId}`); // Log retiré
  selectedChapterId.value = chapterId;
  selectedSceneId.value = null; 
  emit('chapter-selected', chapterId);
  fetchAllCharactersForProject(projectId);
};

const toggleChapterSelection = (chapterId) => {
  const index = selectedChapterIds.value.indexOf(chapterId);
  if (index > -1) {
    selectedChapterIds.value.splice(index, 1);
  } else {
    selectedChapterIds.value.push(chapterId);
  }
};

const handleAddChapterRequest = async (projectId, title) => {
  await addChapter(projectId, title);
};

const handleChapterUpdated = async ({ projectId, chapterId }) => {
  // console.log(`ProjectManager: Chapter ${chapterId} in project ${projectId} was updated. Refetching chapters.`); // Optionnel: log
  await fetchChaptersForProject(projectId);
};

const selectScene = (sceneId, chapterId) => {
  // console.log(`ProjectManager: selectScene - sceneId: ${sceneId}, chapterId: ${chapterId}`); // Log retiré
  selectedSceneId.value = sceneId;
  selectedChapterId.value = null; 
  emit('scene-selected', sceneId);
  const project = projects.value.find(p => chaptersByProjectId[p.id]?.some(c => c.id === chapterId));
  if (project) {
    fetchAllCharactersForProject(project.id);
  }
};

const openAddSceneDialog = (chapterId) => {
  console.log("Ouvrir dialogue ajout scène pour chapitre:", chapterId);
  showSnackbar("Fonctionnalité d'ajout de scène pas encore implémentée.", "info");
};

const openEditSceneDialog = (scene) => {
  console.log("Ouvrir dialogue édition scène:", scene);
  showSnackbar("Fonctionnalité d'édition de scène pas encore implémentée.", "info");
};

const loadScenesIfNeeded = async (chapterId) => {
    if (chapterId && (!scenesByChapterId[chapterId] || scenesByChapterId[chapterId].length === 0)) {
        // console.log(`ProjectManager: loadScenesIfNeeded for chapter ${chapterId}`); // Log retiré
        await fetchScenesForChapter(chapterId);
    }
};

const onChapterDrop = async (projectId, event) => {
  if (event.moved) {
    const { newIndex, oldIndex } = event.moved;
    const chaptersOfProject = chaptersByProjectId[projectId];
    if (chaptersOfProject && chaptersOfProject[oldIndex]) {
        const chapterId = chaptersOfProject[oldIndex].id;
        await reorderChapters(projectId, chapterId, newIndex);
    } else {
        console.error(`ProjectManager: onChapterDrop - Impossible de trouver le chapitre à l'index ${oldIndex} pour le projet ${projectId}`);
    }
  }
};

const onSceneDrop = async (chapterId, event) => {
  if (event.moved) {
    const { newIndex, oldIndex } = event.moved;
    const scenesOfChapter = scenesByChapterId[chapterId];
    if (scenesOfChapter && scenesOfChapter[oldIndex]) {
        const sceneId = scenesOfChapter[oldIndex].id;
        await reorderScenes(chapterId, sceneId, newIndex);
    } else {
        console.error(`ProjectManager: onSceneDrop - Impossible de trouver la scène à l'index ${oldIndex} pour le chapitre ${chapterId}`);
    }
  }
};

const openDeleteConfirmDialog = (item, type) => {
console.log('[ProjectManager] openDeleteConfirmDialog called with item:', JSON.parse(JSON.stringify(item)), 'type:', type);
  itemToDelete.value = { item, type };
  if (type === 'project') {
    deleteTarget.value = { type: 'projet', name: item.title };
  } else if (type === 'chapter') {
    deleteTarget.value = { type: 'chapitre', name: item.title };
  } else if (type === 'scene') {
     deleteTarget.value = { type: 'scène', name: item.title || `Scène ID ${item.id}` };
  } else if (type === 'bulkProjects') {
    deleteTarget.value = { type: 'projets sélectionnés', name: `${selectedProjectIds.value.length} projet(s)`};
  } else if (type === 'bulkChapters') {
    deleteTarget.value = { type: 'chapitres sélectionnés', name: `${selectedChapterIds.value.length} chapitre(s)`};
  }
  showDeleteConfirmDialog.value = true;
};

const closeDeleteConfirmDialog = () => {
  showDeleteConfirmDialog.value = false;
  itemToDelete.value = null;
};


const confirmDelete = async () => {
  console.log('[ProjectManager] confirmDelete function has been entered');
  console.log('[ProjectManager] confirmDelete - current itemToDelete.value:', itemToDelete.value ? JSON.parse(JSON.stringify(itemToDelete.value)) : null);
  if (!itemToDelete.value) {
    console.log('[ProjectManager] confirmDelete: itemToDelete.value was falsy (e.g., null/undefined), returning early.');
    return;
  }
  const { item, type } = itemToDelete.value;
  let success = false;

  if (type === 'project') {
console.log('[ProjectManager] Attempting to delete project with ID (from confirmDelete):', item.id);
    success = await deleteProjectComposable(item.id);
  } else if (type === 'chapter') {
    const deleteResult = await deleteChapterComposable(item.id); success = deleteResult.success;
  } else if (type === 'scene') {
    success = await deleteScene(item.chapter_id, item.id);
  } else if (type === 'bulkProjects') {
    for (const projectId of selectedProjectIds.value) {
      await deleteProjectComposable(projectId); 
    }
    selectedProjectIds.value = []; 
    success = true; 
  } else if (type === 'bulkChapters') {
    console.warn("La suppression en masse de chapitres de projets différents n'est pas entièrement gérée pour trouver le projectId.");
    for (const chapterId of selectedChapterIds.value) {
        const chapterToDelete = findChapterById(chapterId); 
        if (chapterToDelete) {
            await deleteChapterComposable(chapterToDelete.project_id, chapterId);
        }
    }
    selectedChapterIds.value = [];
    success = true;
  }

  if (success) {
    showSnackbar(`${deleteTarget.value.type} "${deleteTarget.value.name}" supprimé(e).`, 'success');
  }
  closeDeleteConfirmDialog();
};

const findChapterById = (chapterId) => {
  for (const projectId in chaptersByProjectId) {
    const chapters = chaptersByProjectId[projectId];
    if (Array.isArray(chapters)) {
        const chapter = chapters.find(c => c.id === chapterId);
        if (chapter) return chapter;
    }
  }
  return null;
};

const handleProjectExport = async ({ projectId, format }) => {
  await exportProject(projectId, format);
};

const handleChapterExport = async ({ chapterId, format }) => {
  // La fonction exportChapter dans useChapters attend chapterId et format.
  // project_id n'est pas nécessaire pour l'appel API d'export de chapitre.
  if (chapterId && format) {
    await exportChapter(chapterId, format);
  } else {
    showSnackbar(`Informations manquantes pour l'export du chapitre (ID: ${chapterId}, Format: ${format}).`, 'error');
  }
};

const openGenerateSceneDialog = (chapterId) => {
  chapterForSceneGeneration.value = chapterId; 
  const chapter = findChapterById(chapterId);
  if (chapter) {
      fetchAllCharactersForProject(chapter.project_id);
  }
  showGenerateSceneDialog.value = true;
};

const handleInsertContent = (content) => {
  emit('insert-generated-content', content);
  showGenerateSceneDialog.value = false; 
};

const openAnalysisDialog = async (projectId) => {
    const project = getProjectById(projectId);
    if (project) {
        deleteTarget.value = { type: 'Analyse de Cohérence', name: project.title };
        await triggerConsistencyAnalysis(projectId);
        showAnalysisDialog.value = true;
    } else {
        showSnackbar(`Projet avec ID ${projectId} non trouvé pour l'analyse.`, 'error');
    }
};
const closeAnalysisDialog = () => {
    showAnalysisDialog.value = false;
    clearConsistencyAnalysisState();
};

const handleApplySuggestion = (suggestionData) => {
  emit('apply-suggestion-to-editor', suggestionData);
};

// Watchers retirés
// watch(selectedProjectIds, (newVal) => { ... });
// watch(selectedChapterIds, (newVal) => { ... });

</script>

<style scoped>
.v-navigation-drawer {
  border-right: 1px solid #e0e0e0; 
}
.v-list-item-title.text-disabled {
  white-space: normal; 
}
</style>
