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
                <v-list-item-subtitle v-if="chapter.summary" class="summary-preview mt-1">
                  Résumé: {{ chapter.summary.substring(0, 70) }}{{ chapter.summary.length > 70 ? '...' : '' }}
                </v-list-item-subtitle>


                <template v-slot:append>
                  <v-tooltip location="top">
                    <template v-slot:activator="{ props: tooltipPropsSummary }">
                      <v-btn
                        v-bind="tooltipPropsSummary"
                        icon
                        density="default"
                        variant="text"
                        size="default"
                        @click.stop="$emit('request-generate-summary', chapter.id)" 
                        :loading="props.generatingSummaryChapterId === chapter.id" 
                        :disabled="props.generatingSummaryChapterId === chapter.id"
                        class="action-btn"
                        title="Générer/Régénérer le résumé"
                      >
                        <v-icon size="20">mdi-text-box-check-outline</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ chapter.summary ? 'Régénérer le résumé' : 'Générer le résumé' }}</span>
                  </v-tooltip>

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
                      <v-list-item @click="openEditChapterDialog(chapter)" title="Modifier le chapitre">
                        <template v-slot:prepend>
                          <IconPencil size="20" class="mr-3"/>
                        </template>
                        <v-list-item-title>Modifier</v-list-item-title>
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
        :loading="props.submittingChapter" 
        :error="addChapterError" 
        :project-name="getProjectNameById(props.projectId)"
        @close="handleAddChapterDialogClose"
        @save="handleAddChapterDialogSave"
      />
      <EditChapterDialog 
        :show="showEditChapterDialog" 
        :loading="props.submittingChapter" 
        :error="editChapterError" 
        :initialTitle="editingChapter?.title || ''"
        :initialSummary="editingChapter?.summary || ''" 
        @close="closeEditChapterDialog" 
        @save="submitEditChapter" 
      />
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
import { defineProps, defineEmits, ref, watch, computed, nextTick, onMounted } from 'vue';
import draggable from 'vuedraggable';
import {
  VListGroup, VListItem, VListItemTitle, VListSubheader, VDivider, VIcon, VTooltip,
  VBtn, VProgressLinear, VAlert, VCheckboxBtn, VMenu, VProgressCircular, VList
} from 'vuetify/components';
import AddChapterDialog from './dialogs/AddChapterDialog.vue';
import EditChapterDialog from './dialogs/EditChapterDialog.vue';
import ChapterAnalysisDialog from './dialogs/ChapterAnalysisDialog.vue';
// import { useChapters } from '@/composables/useChapters.js'; // SUPPRIMÉ
import { useAnalysis } from '@/composables/useAnalysis.js';
import { useAIModels } from '@/composables/useAIModels.js';
import { useProjects } from '@/composables/useProjects.js'; 

import {
  IconGripVertical, IconBook, IconDotsVertical, IconFileText, IconFileTypePdf,
  IconBookDownload, IconPencil, IconSquarePlus, IconFileSearch, IconTrash, IconPlus
} from '@tabler/icons-vue';

const props = defineProps({
  chapters: Array,
  selectedChapterId: [Number, String, null],
  projectId: [Number, String, null],
  loading: Boolean, // Renommé en loadingChapters dans le template pour clarté
  error: String,    // Renommé en errorChapters dans le template
  selectedChapterIds: {
    type: Array,
    default: () => []
  },
  exportingChapterId: { 
    type: [Number, String, null],
    default: null,
  },
  exportingFormat: { 
      type: String,
      default: null,
  },
  showSnackbar: Function,
  // NOUVELLES PROPS pour les états de chargement gérés par le parent
  submittingChapter: Boolean,
  generatingSummaryChapterId: [Number, String, null],
});

const emit = defineEmits([
  'select-chapter',
  'reordered',
  'open-add-scene',
  'open-delete',
  'toggle-selection',
  'handle-export',
  'load-scenes-if-needed',
  'apply-suggestion-to-editor',
  // NOUVEAUX ÉVÉNEMENTS
  'request-add-chapter',
  'request-update-chapter',
  'request-generate-summary',
]);

// Utilisation du composable useChapters SUPPRIMÉE
// const {
//   chapterError: generalChapterError, // Sera géré par le parent ou passé en prop si nécessaire
//   submittingChapter, // Sera une prop
//   generatingSummaryChapterId, // Sera une prop
//   fetchChaptersForProject, // Non utilisé directement ici
//   addChapter, // Sera émis
//   updateChapter, // Sera émis
//   deleteChapter, // Déjà émis via open-delete
//   generateChapterSummary, // Sera émis
// } = useChapters(props.showSnackbar); 


// Dialogs state
const showAddChapterDialog = ref(false);
const addChapterError = ref(null); // Peut être gardé localement pour le dialogue

const showEditChapterDialog = ref(false);
const editingChapter = ref(null); 
const editChapterError = ref(null); // Peut être gardé localement

const showChapterAnalysisDialog = ref(false);
const analyzingChapterId = ref(null);
const chapterAnalysisResult = ref(null);

// Utilisation du composable useAnalysis
const {
    performChapterAnalysis,
    loading: loadingChapterAnalysis, 
    error: errorChapterAnalysis, 
    applySuggestionToContent,
} = useAnalysis(props.showSnackbar);


const localChapters = ref([]);

watch(() => props.chapters, (newChapters) => {
  localChapters.value = newChapters ? [...newChapters] : [];
}, { immediate: true, deep: true });


const loadingChapters = computed(() => props.loading);
const errorChapters = computed(() => props.error);


const openAddChapterDialogInternal = () => {
  addChapterError.value = null;
  showAddChapterDialog.value = true;
};

const handleAddChapterDialogClose = () => {
  showAddChapterDialog.value = false;
};

const handleAddChapterDialogSave = async (title) => {
  if (!props.projectId) {
    addChapterError.value = "ID du projet non défini."; // Garder l'erreur locale au dialogue
    if(props.showSnackbar) props.showSnackbar(addChapterError.value, 'error');
    return;
  }
  addChapterError.value = null;
  // Émettre l'événement au lieu d'appeler addChapter directement
  emit('request-add-chapter', { projectId: props.projectId, title: title });
  // La fermeture du dialogue sera gérée par le parent ou après confirmation de succès
  // Pour l'instant, on suppose que le parent gère la fermeture si l'ajout réussit.
  // Si l'ajout échoue, le parent pourrait ne pas fermer, et addChapterError pourrait être mis à jour via une prop.
  // Pour simplifier, on ferme ici et le parent peut rouvrir ou afficher une erreur globale.
  // Alternative: attendre une confirmation de succès du parent.
  // Pour l'instant, on ne ferme pas ici, on laisse le parent gérer.
  showAddChapterDialog.value = false; // Fermé après émission de la requête. Le parent gère la suite (ex: erreurs).
};

const openEditChapterDialog = (chapter) => {
  editingChapter.value = { ...chapter }; 
  editChapterError.value = null;
  showEditChapterDialog.value = true;
};

const closeEditChapterDialog = () => {
  showEditChapterDialog.value = false;
  editingChapter.value = null;
};

const submitEditChapter = async (dataToSave) => { // dataToSave est { title, summary }
  if (!editingChapter.value || !editingChapter.value.id) return;
  editChapterError.value = null;
  
  const updatePayload = { 
    id: editingChapter.value.id,
    title: dataToSave.title, 
    summary: dataToSave.summary 
  };
  emit('request-update-chapter', updatePayload);
  // La fermeture du dialogue sera gérée par le parent.
  // showEditChapterDialog.value = false; 
  // editingChapter.value = null;
};

const openChapterAnalysisDialog = async (chapterId) => {
    analyzingChapterId.value = chapterId;
    chapterAnalysisResult.value = null; 
    showChapterAnalysisDialog.value = true;
    const result = await performChapterAnalysis(chapterId);
    if (result) {
        chapterAnalysisResult.value = result;
    }
};

const closeChapterAnalysisDialog = () => {
    showChapterAnalysisDialog.value = false;
    analyzingChapterId.value = null;
};

const handleApplySuggestion = (suggestion) => {
    emit('apply-suggestion-to-editor', { chapterId: analyzingChapterId.value, suggestion });
};

const { getProjectById } = useProjects(); 
const getProjectNameById = (pId) => {
    if (!pId) return "Projet inconnu";
    const project = getProjectById(pId); 
    return project ? project.title : "Projet en chargement...";
};

const getChapterTitleById = (chapterId) => {
    if (!chapterId || !localChapters.value) return "Chapitre inconnu";
    const chapter = localChapters.value.find(c => c.id === chapterId);
    return chapter ? chapter.title : "Chapitre inconnu";
};

// handleGenerateSummary est maintenant géré par un emit dans le template:
// @click.stop="$emit('request-generate-summary', chapter.id)"

</script>

<style scoped>
.chapters-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.drag-handle {
  cursor: grab;
  opacity: 0.5;
  margin-right: 8px; 
}
.drag-handle:hover {
  opacity: 1;
}

.ghost-item {
  opacity: 0.5;
  background: #c8ebfb;
}

.chapter-item {
  border-left: 3px solid transparent; 
  transition: background-color 0.1s ease-in-out;
}
.chapter-item:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.v-list-item--active.active-chapter {
  border-left-color: rgb(var(--v-theme-primary)) !important;
}
.v-list-item--active.active-chapter .v-list-item-title {
 font-weight: 500 !important; 
 color: rgb(var(--v-theme-primary));
}


.list-item-hover-actions .action-btn,
.list-item-hover-actions .action-menu-btn {
  opacity: 0.3;
  transition: opacity 0.2s ease-in-out;
}

.list-item-hover-actions:hover .action-btn,
.list-item-hover-actions:hover .action-menu-btn,
.list-item-hover-actions .v-menu--active .action-menu-btn 
 {
  opacity: 1;
}
.summary-preview {
  font-size: 0.7rem; 
  color: rgba(var(--v-theme-on-surface), 0.6); 
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 90%; 
  line-height: 1.2;
  margin-top: 2px; /* Ajout d'un petit espace */
}
.action-btn { /* Style pour s'assurer que les boutons d'action sont bien alignés */
  margin-left: 4px;
}
</style>