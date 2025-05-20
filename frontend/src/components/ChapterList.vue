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
                        @click.stop
                        title="Actions Chapitre"
                        class="action-menu-btn"
                        size="default"
                      >
                        <IconDotsVertical size="22" />
                      </v-btn>
                    </template>
                    <v-list density="compact">
                      <v-list-subheader>Exporter Chapitre</v-list-subheader>
                      <v-list-item @click="$emit('handle-export', chapter.id, 'docx')" :disabled="!!exportingChapterId" title="Exporter Chapitre en DOCX">
                        <template v-slot:prepend>
                          <IconFileText size="20" class="mr-3"/>
                        </template>
                        <v-list-item-title>DOCX</v-list-item-title>
                         <template v-slot:append v-if="exportingChapterId === chapter.id && exportingFormat === 'docx'">
                            <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
                          </template>
                      </v-list-item>
                      <v-list-item @click="$emit('handle-export', chapter.id, 'pdf')" :disabled="!!exportingChapterId" title="Exporter Chapitre en PDF">
                        <template v-slot:prepend>
                          <IconFileTypePdf size="20" class="mr-3"/>
                        </template>
                        <v-list-item-title>PDF</v-list-item-title>
                         <template v-slot:append v-if="exportingChapterId === chapter.id && exportingFormat === 'pdf'">
                            <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
                          </template>
                       </v-list-item>
                       <v-list-item @click="$emit('handle-export', chapter.id, 'txt')" :disabled="!!exportingChapterId" title="Exporter Chapitre en TXT">
                         <template v-slot:prepend>
                           <IconFileText size="20" class="mr-3"/>
                         </template>
                         <v-list-item-title>TXT</v-list-item-title>
                          <template v-slot:append v-if="exportingChapterId === chapter.id && exportingFormat === 'txt'">
                             <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
                           </template>
                        </v-list-item>
                       <v-list-item @click="$emit('handle-export', chapter.id, 'epub')" :disabled="!!exportingChapterId" title="Exporter Chapitre en EPUB">
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
import { defineProps, defineEmits, ref, watch, computed, nextTick } from 'vue';
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
  chapters: {
    type: Array,
    default: () => []
  },
  loadingChapters: {
    type: Boolean,
    default: false
  },
  errorChapters: {
    type: [String, null],
    default: null
  },
  selectedChapterId: {
    type: [Number, null],
    default: null
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
  projectId: {
    type: Number,
    required: true
  },
selectedAiProvider: { type: String, default: null },
  selectedAiModel: { type: String, default: null },
  selectedAiStyle: { type: String, default: null },
  customAiDescription: { type: String, default: null },
});

const emit = defineEmits([
  'reordered',
  'select-chapter',
  'toggle-selection',
  'handle-export',
  'open-delete',
  'open-add-scene',
  'load-scenes-if-needed',
  'apply-suggestion',
  'add-chapter-requested',
  'chapter-updated' // Ajout de l'événement
]);

const localChapters = ref([...props.chapters]);


watch(() => props.chapters, (newChapters) => {
  localChapters.value = [...newChapters];
}, { deep: true });


const { submittingChapter, updateChapter, error: chapterError } = useChapters();

const {
  loadingChapterAnalysis, errorChapterAnalysis, chapterAnalysisResult,
  triggerChapterAnalysis, analyzingChapterId,
} = useAnalysis();



const { getProjectById } = useProjects();

const showAddChapterDialog = ref(false);
const addChapterError = ref(null);
const showEditChapterDialog = ref(false);
const editingChapter = ref(null);
const editChapterError = ref(null);
const showChapterAnalysisDialog = ref(false);


const openAddChapterDialogInternal = () => {
  addChapterError.value = null;
  showAddChapterDialog.value = true;
};

const handleAddChapterDialogClose = () => {
  showAddChapterDialog.value = false;
  addChapterError.value = null;
};


const handleAddChapterDialogSave = (chapterTitle) => {
  addChapterError.value = null;
  emit('add-chapter-requested', chapterTitle);  
  handleAddChapterDialogClose();
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



const submitEditChapter = async (chapterData) => {
  editChapterError.value = null;
  if (!editingChapter.value) return;
  const payload = typeof chapterData === 'string' ? { title: chapterData } : chapterData;
  const success = await updateChapter(editingChapter.value.id, payload);
  if (success) {
    emit('chapter-updated', { projectId: props.projectId, chapterId: editingChapter.value.id }); // Émission de l'événement
    closeEditChapterDialog();    
  } else {    
    editChapterError.value = chapterError.value || 'Erreur lors de la modification du chapitre.';
  }
};

const openChapterAnalysisDialog = async (chapterId) => {
  await triggerChapterAnalysis(chapterId, props.selectedAiProvider, props.selectedAiModel);
  showChapterAnalysisDialog.value = true;
};

const closeChapterAnalysisDialog = () => {
  showChapterAnalysisDialog.value = false;
};

const getChapterTitleById = (chapterId) => {
  const chapter = localChapters.value.find(c => c.id === chapterId);
  return chapter ? chapter.title : 'Chapitre inconnu';
};

const getProjectNameById = (projectId) => {
    const project = getProjectById(projectId);
    return project ? project.title : 'Projet inconnu';
};


const handleApplySuggestion = (suggestion) => {
  emit('apply-suggestion', suggestion);
};

</script>

<style scoped>
.chapters-container {
}

.chapter-group ::v-deep(.v-list-group__items) {
  --v-list-item-padding-left: 0;
}

.list-item-hover-actions {
  position: relative;
}

.action-menu-btn {
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
}

.list-item-hover-actions:hover .action-menu-btn {
  opacity: 1;
}

.drag-handle {
  cursor: grab;
}

.ghost-item {
  opacity: 0.5;
  background-color: rgba(var(--v-theme-primary), 0.05); /* Updated background color */
}

.drag-item {
  background-color: rgba(var(--v-theme-primary), 0.1); /* Updated background color */
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.active-chapter {
  background-color: rgba(var(--v-theme-secondary), 0.1);
  border-left: 3px solid rgb(var(--v-theme-secondary));
}

.chapter-item {
  border-left: 3px solid transparent;
}
</style>