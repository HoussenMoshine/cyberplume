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
              :generatingSummaryChapterId="generatingSummaryChapterId"
              :loadingChapterAnalysis="loadingAnalysis"
              :analyzingChapterId="analyzingChapterId"
              @reordered="(ids) => onChapterDrop(project.id, ids)"
              @select-chapter="(chapterId) => emit('chapter-selected', { chapterId })"
              @toggle-selection="toggleChapterSelection"
              @handle-export="handleChapterExport"
              @open-delete="openDeleteConfirmDialog"
              @open-add-dialog="() => openAddChapterDialog(project.id)"
              @open-edit-dialog="openEditChapterDialog"
              @open-analysis-dialog="openChapterAnalysisDialog"
              @generate-summary="handleChapterGenerateSummaryRequested"
            >
            </ChapterList>
          </template>
        </ProjectItem>
      </div>

      <v-list-item v-if="!loadingProjects && projects.length === 0">
        <v-list-item-title class="text-center text-disabled font-italic mt-4">Aucun projet trouvé.</v-list-item-title>
      </v-list-item>
    </v-container>

    <!-- Dialogues de Projet -->
    <AddProjectDialog :show="showAddProjectDialog" :loading="submittingProject" :error="addProjectError" @close="showAddProjectDialog = false" @save="submitNewProject" />
    <EditProjectDialog :show="showEditProjectDialog" :loading="submittingProject" :error="editProjectError" :initialTitle="editingProject?.title || ''" :initialDescription="editingProject?.description || ''" @close="closeEditProjectDialog" @save="submitEditProject" />

    <!-- Dialogues de Chapitre -->
    <AddChapterDialog
      :show="showAddChapterDialog"
      :loading="submittingChapter"
      :error="addChapterError"
      :project-name="getProjectNameById(currentProjectIdForDialogs)"
      @close="closeAddChapterDialog"
      @save="submitNewChapter"
    />
    <EditChapterDialog
      :show="showEditChapterDialog"
      :loading="submittingChapter"
      :error="editChapterError"
      :initialTitle="editingChapter?.title || ''"
      :initialSummary="editingChapter?.summary || ''"
      @close="closeEditChapterDialog"
      @save="submitEditChapter"
    />

    <!-- Autres Dialogues -->
    <DeleteConfirmDialog
      :show="showDeleteConfirmDialog"
      :loading="isDeleting"
      :deleteTarget="deleteTarget"
      :deleteType="deleteType"
      :targetCounts="{ projects: selectedProjectIds.length, chapters: selectedChapterIds.length }"
      @close="closeDeleteConfirmDialog"
      @confirm="confirmDelete"
    />
    <AnalysisReportDialog
        :show="showAnalysisDialog"
        :loading="loadingAnalysis"
        :error="errorAnalysis"
        :analysisResult="analysisResult"
        @close="closeAnalysisDialog"
    />
     <ChapterAnalysisDialog
        :show="showChapterAnalysisDialog"
        :loading="loadingAnalysis"
        :error="errorAnalysis"
        :analysis-result="chapterAnalysisResult"
        :chapter-title="analyzingChapterTitle"
        @close="closeChapterAnalysisDialog"
        @apply-suggestion="handleApplySuggestion"
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
import { ref, onMounted, computed } from 'vue';

import AddProjectDialog from './dialogs/AddProjectDialog.vue';
import EditProjectDialog from './dialogs/EditProjectDialog.vue';
import DeleteConfirmDialog from './dialogs/DeleteConfirmDialog.vue';
import AnalysisReportDialog from './dialogs/AnalysisReportDialog.vue';
import AddChapterDialog from './dialogs/AddChapterDialog.vue';
import EditChapterDialog from './dialogs/EditChapterDialog.vue';
import ChapterAnalysisDialog from './dialogs/ChapterAnalysisDialog.vue';

import ProjectToolbar from './ProjectToolbar.vue';
import ProjectItem from './ProjectItem.vue';
import ChapterList from './ChapterList.vue';

import { useProjects } from '@/composables/useProjects.js';
import { useChapters } from '@/composables/useChapters.js';
import { useAnalysis } from '@/composables/useAnalysis.js';

const props = defineProps({
  selectedChapterId: { type: [Number, String, null], default: null },
  currentAiProvider: { type: String, default: 'gemini' },
  currentAiModel: { type: String, default: null },
  currentAiStyle: { type: String, default: 'normal' },
  currentCustomAiDescription: { type: String, default: null },
});

const emit = defineEmits(['chapter-selected', 'apply-suggestion-to-editor']);

const snackbarVisible = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');
const showSnackbar = (text, color = 'success') => {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbarVisible.value = true;
};

const {
  projects, loadingProjects, errorProjects, submittingProject, deletingItem: deletingProjectItemState,
  exportingProjectId, exportingFormat,
  fetchProjects: fetchProjectsComposable, addProject: addProjectComposable,
  updateProject: updateProjectComposable, deleteProject: deleteProjectInternalComposable,
  exportProject,
} = useProjects(showSnackbar);

const {
  chaptersByProjectId, loadingChapters, errorChapters,
  submittingChapter, deletingChapterItem,
  exportingChapterId: exportingChapterIdComposable,
  generatingSummaryChapterId,
  errorOnAddChapter, chapterError,
  fetchChaptersForProject: fetchChaptersComposable,
  addChapter: addChapterComposable,
  updateChapter: updateChapterComposable,
  deleteChapter: deleteChapterComposable,
  reorderChapters: reorderChaptersComposable,
  exportChapter: exportChapterComposable,
  generateChapterSummary: generateChapterSummaryComposable,
} = useChapters(showSnackbar);

const {
    analysisResult, loadingAnalysis, errorAnalysis,
    triggerConsistencyAnalysis, triggerChapterAnalysis,
    chapterAnalysisResult,
} = useAnalysis(showSnackbar);

// --- State ---
const selectedProjectIds = ref([]);
const selectedChapterIds = ref([]);

// --- Dialog State (Unified) ---
const showAddProjectDialog = ref(false);
const showEditProjectDialog = ref(false);
const editingProject = ref(null);
const addProjectError = ref('');
const editProjectError = ref('');

const showAddChapterDialog = ref(false);
const showEditChapterDialog = ref(false);
const editingChapter = ref(null);
const currentProjectIdForDialogs = ref(null);
const addChapterError = ref(null);
const editChapterError = ref(null);

const showDeleteConfirmDialog = ref(false);
const deleteTarget = ref(null);
const deleteType = ref('');

const showAnalysisDialog = ref(false);
const showChapterAnalysisDialog = ref(false);
const analyzingChapterId = ref(null);
const isDeleting = computed(() => !!deletingProjectItemState.value || deletingChapterItem.value);
const analyzingChapterTitle = ref('');

onMounted(fetchProjectsComposable);

// --- Methods ---

function toggleProjectSelection(projectId) {
  const index = selectedProjectIds.value.indexOf(projectId);
  if (index > -1) selectedProjectIds.value.splice(index, 1);
  else selectedProjectIds.value.push(projectId);
}

function toggleChapterSelection(chapterId) {
    const index = selectedChapterIds.value.indexOf(chapterId);
    if (index > -1) selectedChapterIds.value.splice(index, 1);
    else selectedChapterIds.value.push(chapterId);
}

function fetchChaptersForProject(projectId) {
    fetchChaptersComposable(projectId);
}

function onChapterDrop(projectId, orderedIds) {
    reorderChaptersComposable(projectId, orderedIds);
}

function handleChapterGenerateSummaryRequested({ projectId, chapterId }) {
    const aiSettings = {
      provider: props.currentAiProvider,
      model: props.currentAiModel,
    };
    generateChapterSummaryComposable(projectId, chapterId, aiSettings);
}

function handleProjectExport({ projectId, format }) {
    exportProject(projectId, format);
}

function handleChapterExport({ chapterId, format }) {
    exportChapterComposable(chapterId, format);
}

// --- Project Dialogs ---
async function submitNewProject(projectData) {
  const newProject = await addProjectComposable(projectData);
  if (newProject) showAddProjectDialog.value = false;
}

function openEditProjectDialog(project) {
  editingProject.value = project;
  showEditProjectDialog.value = true;
}

function closeEditProjectDialog() {
  editingProject.value = null;
  showEditProjectDialog.value = false;
}

async function submitEditProject(projectData) {
  if (!editingProject.value) return;
  const updatedProject = await updateProjectComposable(editingProject.value.id, projectData);
  if (updatedProject) closeEditProjectDialog();
}

// --- Chapter Dialogs ---
function openAddChapterDialog(projectId) {
    currentProjectIdForDialogs.value = projectId;
    addChapterError.value = null;
    showAddChapterDialog.value = true;
}

function closeAddChapterDialog() {
    showAddChapterDialog.value = false;
    currentProjectIdForDialogs.value = null;
}

async function submitNewChapter(title) {
    const newChapter = await addChapterComposable(currentProjectIdForDialogs.value, title);
    if (newChapter) {
        closeAddChapterDialog();
    }
}

function openEditChapterDialog(chapter) {
    editingChapter.value = { ...chapter };
    editChapterError.value = null;
    showEditChapterDialog.value = true;
}

function closeEditChapterDialog() {
    editingChapter.value = null;
    showEditChapterDialog.value = false;
}

async function submitEditChapter(updatedData) {
    if (!editingChapter.value) return;
    const success = await updateChapterComposable(editingChapter.value.id, updatedData);
    if (success) {
        closeEditChapterDialog();
    }
}

// --- Deletion Dialog ---
function openDeleteConfirmDialog(item, type) {
  // On clone l'item pour éviter les problèmes de réactivité si la liste source est modifiée
  deleteTarget.value = item ? { ...item } : null;
  deleteType.value = type;
  showDeleteConfirmDialog.value = true;
}

function closeDeleteConfirmDialog() {
  showDeleteConfirmDialog.value = false;
  deleteTarget.value = null;
  deleteType.value = '';
}

async function confirmDelete() {
  try {
    if (deleteType.value === 'project') {
      await deleteProjectInternalComposable([deleteTarget.value.id]);
    } else if (deleteType.value === 'chapter') {
      const chapter = deleteTarget.value;
      if (chapter && chapter.project_id && chapter.id) {
        await deleteChapterComposable(chapter.project_id, chapter.id);
      }
    } else if (deleteType.value === 'project-selection') {
      await deleteProjectInternalComposable([...selectedProjectIds.value]);
      selectedProjectIds.value = [];
    } else if (deleteType.value === 'chapter-selection') {
      // On doit trouver le project_id pour chaque chapitre, c'est plus complexe.
      // On va boucler sur les chapitres sélectionnés.
      for (const chapterId of selectedChapterIds.value) {
        const chapter = findChapterById(chapterId);
        if (chapter && chapter.project_id) {
          // On attend chaque suppression individuellement.
          await deleteChapterComposable(chapter.project_id, chapter.id);
        }
      }
      selectedChapterIds.value = [];
    }
  } catch (error) {
    console.error("Erreur lors de la suppression :", error);
    // Le snackbar est déjà géré dans les composables
  } finally {
    closeDeleteConfirmDialog();
  }
}

// --- Analysis Dialogs ---
function openAnalysisDialog(projectId) {
    triggerConsistencyAnalysis(projectId);
    showAnalysisDialog.value = true;
}

function closeAnalysisDialog() {
    showAnalysisDialog.value = false;
}

function openChapterAnalysisDialog(chapterId) {
    const chapter = findChapterById(chapterId);
    if(chapter) {
        analyzingChapterId.value = chapterId;
        analyzingChapterTitle.value = chapter.title;
        triggerChapterAnalysis(chapterId, props.currentAiProvider, props.currentAiModel);
        showChapterAnalysisDialog.value = true;
    }
}

function closeChapterAnalysisDialog() {
    showChapterAnalysisDialog.value = false;
}

function handleApplySuggestion(suggestion) {
    // Le dialogue n'a pas l'ID du chapitre, mais ce n'est pas grave car l'éditeur
    // travaille sur le chapitre actuellement chargé.
    // On remonte l'événement au parent (App.vue) qui a la référence de l'éditeur.
    emit('apply-suggestion-to-editor', suggestion);
    
    // On pourrait aussi fermer le dialogue ici si on le souhaite.
    // closeChapterAnalysisDialog();
}

// --- Helpers ---
function findChapterById(chapterId) {
    for (const projectId in chaptersByProjectId) {
        const chapters = chaptersByProjectId[projectId];
        if (chapters) {
            const found = chapters.find(c => c.id === chapterId);
            if (found) return found;
        }
    }
    return null;
}

function getProjectNameById(projectId) {
    if (!projectId) return '';
    const project = projects.value.find(p => p.id === projectId);
    return project ? project.title : '';
}

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
