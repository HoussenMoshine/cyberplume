<template>
  <div class="chapters-container pl-2 pr-1 py-1">
    <v-progress-linear v-if="loadingChapters" indeterminate color="secondary" height="2"></v-progress-linear>
    <v-alert v-if="errorChapters" type="error" density="compact" variant="tonal" class="my-1 mx-2">
      {{ errorChapters }}
    </v-alert>

    <div v-if="!loadingChapters && localChapters && localChapters.length > 0">
      <draggable
        v-model="localChapters"
        item-key="id"
        tag="div"
        handle=".drag-handle"
        @end="$emit('reordered', localChapters)"
        ghost-class="ghost-item"
        drag-class="drag-item"
      >
        <template #item="{ element: chapter }">
          <v-list-group
            :key="chapter.id"
            :value="chapter.id"
            @update:modelValue="(newValue) => $emit('load-scenes-if-needed', chapter.id, newValue)"
            class="chapter-group"
          >
            <template v-slot:activator="{ props: activatorProps }">
              <v-list-item
                v-bind="activatorProps"
                link
                density="default"
                min-height="48px"
                :class="{ 'v-list-item--active active-chapter': selectedChapterId === chapter.id }"
                class="list-item-hover-actions chapter-item pl-2 pr-1 py-1"
                @click.stop="$emit('select-chapter', chapter.id)"
              >
                <template v-slot:prepend>
                   <IconGripVertical size="20" class="drag-handle mr-2" title="Réordonner" />
                  <v-checkbox-btn
                    :model-value="selectedChapterIds.includes(chapter.id)"
                    @update:model-value="$emit('toggle-selection', chapter.id)"
                    density="default"
                    @click.stop
                    class="mr-2 flex-grow-0"
                  ></v-checkbox-btn>
                  <IconBook size="20" class="mr-2" />
                </template>

                <v-list-item-title class="text-body-1 font-weight-medium">{{ chapter.title }}</v-list-item-title>

                <template v-slot:append>
                  <v-menu location="bottom end">
                    <template v-slot:activator="{ props: menuProps }">
                      <v-btn
                        icon
                        density="default"
                        variant="text"
                        v-bind="menuProps"
                        @click.stop="() => { console.log('ChapterList Menu clicked, exportingChapterId:', exportingChapterId); }"
                        title="Actions Chapitre"
                        class="action-menu-btn"
                        size="default"
                      >
                        <IconDotsVertical size="22" />
                      </v-btn>
                    </template>
                    <v-list density="compact">
                      <v-list-subheader>Exporter Chapitre</v-list-subheader>
                      <v-list-item @click="$emit('handle-export', { chapterId: chapter.id, format: 'docx' })" :disabled="!!exportingChapterId" title="Exporter Chapitre en DOCX">
                        <template v-slot:prepend>
                          <IconFileText size="20" class="mr-3"/>
                        </template>
                        <v-list-item-title>DOCX</v-list-item-title>
                         <template v-slot:append v-if="exportingChapterId === chapter.id && exportingFormat === 'docx'">
                            <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
                          </template>
                      </v-list-item>
                      <v-list-item @click="$emit('handle-export', { chapterId: chapter.id, format: 'pdf' })" :disabled="!!exportingChapterId" title="Exporter Chapitre en PDF">
                        <template v-slot:prepend>
                          <IconFileTypePdf size="20" class="mr-3"/>
                        </template>
                        <v-list-item-title>PDF</v-list-item-title>
                         <template v-slot:append v-if="exportingChapterId === chapter.id && exportingFormat === 'pdf'">
                            <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
                          </template>
                       </v-list-item>
                       <v-list-item @click="$emit('handle-export', { chapterId: chapter.id, format: 'txt' })" :disabled="!!exportingChapterId" title="Exporter Chapitre en TXT">
                         <template v-slot:prepend>
                           <IconFileText size="20" class="mr-3"/>
                         </template>
                         <v-list-item-title>TXT</v-list-item-title>
                          <template v-slot:append v-if="exportingChapterId === chapter.id && exportingFormat === 'txt'">
                             <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
                           </template>
                        </v-list-item>
                       <v-list-item @click="$emit('handle-export', { chapterId: chapter.id, format: 'epub' })" :disabled="!!exportingChapterId" title="Exporter Chapitre en EPUB">
                         <template v-slot:prepend>
                           <IconBookDownload size="20" class="mr-3"/>
                         </template>
                         <v-list-item-title>EPUB</v-list-item-title>
                          <template v-slot:append v-if="exportingChapterId === chapter.id && exportingFormat === 'epub'">
                             <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
                           </template>
                        </v-list-item>
                      <v-divider class="my-1"></v-divider>
                      <v-list-subheader>Actions Chapitre</v-list-subheader>
                      <v-list-item @click="openEditChapterDialog(chapter)" title="Renommer le chapitre">
                        <template v-slot:prepend>
                          <IconPencil size="20" class="mr-3"/>
                        </template>
                        <v-list-item-title>Renommer</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click.stop="$emit('open-add-scene', chapter.id)" title="Ajouter une scène">
                         <template v-slot:prepend>
                           <IconSquarePlus size="20" class="mr-3"/>
                         </template>
                         <v-list-item-title>Ajouter Scène</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click.stop="openChapterAnalysisDialog(chapter.id)" title="Analyser le contenu du chapitre">
                         <template v-slot:prepend>
                           <IconFileSearch size="20" class="mr-3"/>
                         </template>
                         <v-list-item-title>Analyser Contenu</v-list-item-title>
                         <template v-slot:append v-if="loadingChapterAnalysis && analyzingChapterId === chapter.id">
                            <v-progress-circular indeterminate size="16" width="2" color="info"></v-progress-circular>
                          </template>
                      </v-list-item>
                      <v-list-item @click="$emit('open-delete', chapter, 'chapter')" title="Supprimer le chapitre" class="text-error">
                        <template v-slot:prepend>
                          <IconTrash size="20" class="mr-3"/>
                        </template>
                        <v-list-item-title>Supprimer</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-list-item>
            </template>

            <slot :name="`scene-list-${chapter.id}`"></slot>

          </v-list-group>
        </template>
      </draggable>

      <v-list-item v-if="localChapters.length === 0 && !loadingChapters && !errorChapters" dense class="pl-2 py-1">
        <v-list-item-title class="text-caption font-italic text-disabled">Aucun chapitre</v-list-item-title>
      </v-list-item>
    </div>
     <v-list-item v-else-if="!loadingChapters && !errorChapters && (!localChapters || localChapters.length === 0)" dense class="pl-2 py-1">
        <v-list-item-title class="text-caption font-italic text-disabled">Aucun chapitre</v-list-item-title>
      </v-list-item>

    <v-list-item link @click="openAddChapterDialogInternal" class="mt-2">
      <template v-slot:prepend>
        <IconPlus size="20" class="mr-2"/>
      </template>
      <v-list-item-title class="text-body-2">Ajouter un chapitre</v-list-item-title>
    </v-list-item>

      <AddChapterDialog
        :show="showAddChapterDialog"
        :loading="submittingChapter"
        :error="addChapterError"
        :project-name="getProjectNameById(projectId)"
        @close="handleAddChapterDialogClose"
        @save="handleAddChapterDialogSave"
      />
      <EditChapterDialog :show="showEditChapterDialog" :loading="submittingChapter" :error="editChapterError" :initialTitle="editingChapter?.title || ''" @close="closeEditChapterDialog" @save="submitEditChapter" />
      <ChapterAnalysisDialog
        :show="showChapterAnalysisDialog"
        :loading="loadingChapterAnalysis"
        :error="errorChapterAnalysis"
        :analysisResult="chapterAnalysisResult"
        :chapterTitle="getChapterTitleById(analyzingChapterId)"
        @close="closeChapterAnalysisDialog"
        @apply-suggestion="handleApplySuggestion"
      />
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch, computed, nextTick, onMounted } from 'vue'; // Ajout de onMounted
import draggable from 'vuedraggable';
import {
  VListGroup, VListItem, VListItemTitle, VListSubheader, VDivider,
  VBtn, VProgressLinear, VAlert, VCheckboxBtn, VMenu, VProgressCircular, VList
} from 'vuetify/components';
import AddChapterDialog from './dialogs/AddChapterDialog.vue';
import EditChapterDialog from './dialogs/EditChapterDialog.vue';
import ChapterAnalysisDialog from './dialogs/ChapterAnalysisDialog.vue';
import { useChapters } from '@/composables/useChapters.js';
import { useAnalysis } from '@/composables/useAnalysis.js';
import { useAIModels } from '@/composables/useAIModels.js';
import { useProjects } from '@/composables/useProjects.js';

import {
  IconGripVertical, IconBook, IconDotsVertical, IconFileText, IconFileTypePdf,
  IconBookDownload, IconPencil, IconSquarePlus, IconFileSearch, IconTrash, IconPlus
} from '@tabler/icons-vue';

const props = defineProps({
  projectId: {
    type: Number,
    required: true,
  },
  chapters: {
    type: Array,
    default: () => [],
  },
  loadingChapters: {
    type: Boolean,
    default: false,
  },
  errorChapters: {
    type: String,
    default: null,
  },
  selectedChapterId: {
    type: [Number, null],
    default: null,
  },
  selectedChapterIds: {
    type: Array,
    default: () => []
  },
  exportingChapterId: {
    type: [Number, null],
    default: null
  },
  exportingFormat: {
    type: [String, null],
    default: null
  },
  // Props pour l'IA contextuelle
  selectedAiProvider: String,
  selectedAiModel: String,
  selectedAiStyle: String,
  customAiDescription: String,
});

// Log pour vérifier la valeur de la prop exportingChapterId à la création/mise à jour
onMounted(() => {
  console.log(`ChapterList for project ${props.projectId} MOUNTED. exportingChapterId:`, props.exportingChapterId);
});
watch(() => props.exportingChapterId, (newValue) => {
  console.log(`ChapterList for project ${props.projectId} exportingChapterId prop CHANGED to:`, newValue);
});


const emit = defineEmits([
  'reordered',
  'select-chapter',
  'toggle-selection',
  'handle-export',
  'open-add-scene',
  'open-delete',
  'load-scenes-if-needed',
  'apply-suggestion',
  'add-chapter-requested',
  'chapter-updated'
]);

const { getProjectById } = useProjects();
const getProjectNameById = (id) => {
  const project = getProjectById(id);
  return project ? project.title : 'Projet inconnu';
};


const localChapters = ref([]);
const showAddChapterDialog = ref(false);
const showEditChapterDialog = ref(false);
const editingChapter = ref(null);
const addChapterError = ref(null); // Pour le dialogue d'ajout
const editChapterError = ref(null); // Pour le dialogue d'édition

const { submittingChapter, addChapter, updateChapter } = useChapters();
const {
    chapterAnalysisResult, loadingChapterAnalysis, errorChapterAnalysis,
    triggerChapterAnalysis, clearChapterAnalysisState
} = useAnalysis();

const showChapterAnalysisDialog = ref(false);
const analyzingChapterId = ref(null);


const getChapterTitleById = (chapterId) => {
  if (!chapterId || !localChapters.value) return 'Chapitre inconnu';
  const chapter = localChapters.value.find(c => c.id === chapterId);
  return chapter ? chapter.title : 'Chapitre inconnu';
};


const openChapterAnalysisDialog = (chapterId) => {
  analyzingChapterId.value = chapterId;
  clearChapterAnalysisState(); // Clear previous results
  triggerChapterAnalysis(chapterId, props.selectedAiProvider, props.selectedAiModel);
  showChapterAnalysisDialog.value = true;
};

const closeChapterAnalysisDialog = () => {
  showChapterAnalysisDialog.value = false;
  analyzingChapterId.value = null;
};

const handleApplySuggestion = (suggestion) => {
  emit('apply-suggestion', suggestion);
  closeChapterAnalysisDialog();
};


watch(() => props.chapters, (newChapters) => {
  // console.log(`DEBUG ChapterList WATCH props.chapters for project ${props.projectId}:`, newChapters ? newChapters.length : 0);
  if (newChapters) {
    localChapters.value = [...newChapters].sort((a, b) => a.order - b.order);
  } else {
    localChapters.value = [];
  }
}, { immediate: true, deep: true });


const openAddChapterDialogInternal = () => {
  addChapterError.value = null; // Réinitialiser l'erreur
  showAddChapterDialog.value = true;
};

const handleAddChapterDialogClose = () => {
  showAddChapterDialog.value = false;
  addChapterError.value = null;
};

const handleAddChapterDialogSave = async (title) => {
  addChapterError.value = null;
  // L'objet newChapterData n'est plus nécessaire ici car le composable attend projectId et title séparément.
  // L'ordre sera géré par le backend ou par un rafraîchissement de la liste.
  const result = await addChapter(props.projectId, title); // Appel corrigé
  if (result) {
    // Le composable useChapters devrait mettre à jour la liste globale des chapitres
    // de manière réactive, ce qui devrait se refléter dans props.chapters.
    // L'émission de 'add-chapter-requested' peut toujours être utile si ProjectManager
    // a besoin de faire des actions supplémentaires (ex: sélectionner le nouveau chapitre).
    emit('add-chapter-requested', title); 
    showAddChapterDialog.value = false;
  } else {
    // L'erreur est gérée par le composable useChapters (via chapterError)
    // et peut être affichée par une snackbar globale ou un message d'erreur dans ProjectManager.
    // On peut aussi conserver une erreur locale pour le dialogue si nécessaire.
    addChapterError.value = "Erreur lors de l'ajout du chapitre. Vérifiez la console ou les notifications.";
  }
};

const openEditChapterDialog = (chapter) => {
  editingChapter.value = { ...chapter };
  editChapterError.value = null;
  showEditChapterDialog.value = true;
};

const closeEditChapterDialog = () => {
  showEditChapterDialog.value = false;
  editingChapter.value = null;
  editChapterError.value = null;
};

const submitEditChapter = async (newTitle) => {
  if (!editingChapter.value) return;
  editChapterError.value = null;
  const updatedData = { title: newTitle };
  const result = await updateChapter(editingChapter.value.id, updatedData);
  if (result) {
    // Le composable devrait mettre à jour la liste globale.
    // Émettre avec projectId et chapterId pour que ProjectManager puisse rafraîchir correctement.
    emit('chapter-updated', { projectId: props.projectId, chapterId: editingChapter.value.id }); 
    closeEditChapterDialog();
  } else {
    editChapterError.value = "Erreur lors de la mise à jour du chapitre.";
  }
};

</script>

<style scoped>
.chapters-container {
  /* background-color: #f9f9f9; */
  /* border-top: 1px solid #eee; */
  /* border-bottom: 1px solid #eee; */
}
.ghost-item {
  opacity: 0.5;
  background: #c8ebfb;
}
.drag-item {
  background: #e0f7fa;
  /* box-shadow: 0 2px 5px rgba(0,0,0,0.1); */
}
.drag-handle {
  cursor: grab;
  color: #757575;
}
.drag-handle:hover {
  color: #333;
}

.chapter-group {
  margin-bottom: 0px; /* Reduced margin */
  border-radius: 4px;
  /* overflow: hidden; */
}

.chapter-item {
  /* background-color: white; */
  /* border-bottom: 1px solid #f0f0f0; */
  transition: background-color 0.1s ease-in-out;
}
.chapter-item:hover {
  /* background-color: #f5f5f5; */
}

.active-chapter {
  /* background-color: rgba(var(--v-theme-primary), 0.08) !important; */
  /* border-left: 3px solid rgb(var(--v-theme-primary)) !important; */
  /* color: rgb(var(--v-theme-primary)) !important; */
}
.active-chapter .v-list-item-title {
  /* color: rgb(var(--v-theme-primary)) !important; */
  /* font-weight: 500 !important; */
}

.list-item-hover-actions .action-menu-btn {
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}

.list-item-hover-actions:hover .action-menu-btn {
    visibility: visible;
    opacity: 1;
}
</style>