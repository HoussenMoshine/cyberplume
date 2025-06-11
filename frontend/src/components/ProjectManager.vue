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
              :loading="loadingChapters[project.id] || false"
              :error="errorChapters[project.id] || null"
              :selectedChapterId="props.selectedChapterId"
              :selectedChapterIds="selectedChapterIds"
              :exportingChapterId="exportingChapterIdComposable"
              :exportingFormat="exportingFormat"
              :submittingChapter="submittingChapter"
              :generatingSummaryChapterId="generatingSummaryChapterId"
              :addingChapterError="currentErrorAddingChapter"
              :on-generate-summary="handleChapterGenerateSummaryRequested"
              @reordered="(event) => onChapterDrop(project.id, event)"
              @select-chapter="(chapterId) => emit('chapter-selected', { chapterId })"
              @toggle-selection="toggleChapterSelection"
              @handle-export="handleChapterExport"
              @open-delete="openDeleteConfirmDialog"
              @apply-suggestion="handleApplySuggestion"
              @request-add-chapter="handleChapterAddRequested"
              @request-update-chapter="handleChapterUpdateRequested"
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
  selectedChapterId: [String, Number, null],
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
  errorOnAddChapter: currentErrorAddingChapter, // Récupérer l'erreur spécifique à l'ajout
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


// --- Projects ---
const selectedProjectIds = ref([]);
const showAddProjectDialog = ref(false);
const addProjectError = ref('');
const editingProject = ref(null);
const showEditProjectDialog = ref(false);
const editProjectError = ref('');

// --- Chapters ---
const selectedChapterIds = ref([]);
const currentProjectIdForChapters = ref(null);

// --- Deletion ---
const showDeleteConfirmDialog = ref(false);
const deleteTarget = ref(null);
const deleteType = ref(''); // 'project' or 'chapter'

// --- Analysis ---
const showAnalysisDialog = ref(false);


onMounted(() => {
  fetchProjects();
});

function fetchProjects() {
  fetchProjectsComposable();
}

// ... (rest of the component logic for project/chapter management)

function toggleProjectSelection(projectId) {
  const index = selectedProjectIds.value.indexOf(projectId);
  if (index > -1) {
    selectedProjectIds.value.splice(index, 1);
  } else {
    selectedProjectIds.value.push(projectId);
  }
}

function toggleChapterSelection(chapterId) {
    const index = selectedChapterIds.value.indexOf(chapterId);
    if (index > -1) {
        selectedChapterIds.value.splice(index, 1);
    } else {
        selectedChapterIds.value.push(chapterId);
    }
}

function fetchChaptersForProject(projectId) {
    currentProjectIdForChapters.value = projectId;
    fetchChaptersComposable(projectId);
}

function onChapterDrop(projectId, event) {
    reorderChaptersComposable(projectId, event);
}

function handleChapterAddRequested({ projectId, title, summary }) {
    addChapterComposable(projectId, { title, summary });
}

function handleChapterUpdateRequested({ chapterId, title, summary }) {
    const chapter = findChapterById(chapterId);
    if (chapter) {
        updateChapterComposable(chapter.project_id, chapterId, { title, summary });
    }
}

function handleChapterGenerateSummaryRequested(projectId, chapterId) {
    
    generateChapterSummaryComposable(projectId, chapterId);
}

function handleProjectExport({ projectId, format }) {
    exportProject(projectId, format);
}

function handleChapterExport({ chapterId, format }) {
    const chapter = findChapterById(chapterId);
    if (chapter) {
        exportChapterComposable(chapter.project_id, chapterId, format);
    }
}

function handleApplySuggestion(suggestionData) {
    const chapter = findChapterById(suggestionData.chapterId);
    if (chapter) {
        applySuggestionToChapterContent(chapter.project_id, suggestionData.chapterId, suggestionData.suggestion);
    }
}

// --- Dialogs management ---

function openAddProjectDialog() {
  addProjectError.value = '';
  showAddProjectDialog.value = true;
}

function handleAddProjectDialogClose() {
  showAddProjectDialog.value = false;
}

async function submitNewProject(projectData) {
  const success = await addProjectComposable(projectData);
  if (success) {
    showAddProjectDialog.value = false;
  }
}

function openEditProjectDialog(project) {
  editingProject.value = project;
  editProjectError.value = '';
  showEditProjectDialog.value = true;
}

function closeEditProjectDialog() {
  showEditProjectDialog.value = false;
  editingProject.value = null;
}

async function submitEditProject(projectData) {
  if (!editingProject.value) return;
  const success = await updateProjectComposable(editingProject.value.id, projectData);
  if (success) {
    closeEditProjectDialog();
  }
}

function openDeleteConfirmDialog(item, type) {
  deleteTarget.value = item;
  deleteType.value = type;
  showDeleteConfirmDialog.value = true;
}

function closeDeleteConfirmDialog() {
  showDeleteConfirmDialog.value = false;
  deleteTarget.value = null;
  deleteType.value = '';
}

async function confirmDelete() {
  if (deleteType.value === 'project') {
    const idsToDelete = selectedProjectIds.value.length > 0 ? [...selectedProjectIds.value] : [deleteTarget.value.id];
    await deleteProjectInternalComposable(idsToDelete);
    selectedProjectIds.value = [];
  } else if (deleteType.value === 'chapter') {
    const chapter = deleteTarget.value;
    await deleteChapterComposable(chapter.project_id, chapter.id);
  }
  closeDeleteConfirmDialog();
}

function openAnalysisDialog(projectId) {
    getProjectAnalysis(projectId);
    showAnalysisDialog.value = true;
}

function closeAnalysisDialog() {
    showAnalysisDialog.value = false;
}

// --- Helper ---
function findChapterById(chapterId) {
    for (const projectId in chaptersByProjectId.value) {
        const chapters = chaptersByProjectId.value[projectId];
        const found = chapters.find(c => c.id === chapterId);
        if (found) return found;
    }
    return null;
}

watch(currentProjectIdForChapters, (newVal) => {
    if (newVal) {
        selectedChapterIds.value = [];
    }
});

</script>

<style scoped>
.v-navigation-drawer {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.v-container {
  flex-grow: 1;
  overflow-y: auto;
}
</style>
