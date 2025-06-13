<template>
  <div class="chapters-container pl-2 pr-1 py-1">
    <v-progress-linear v-if="props.loading" indeterminate color="secondary" height="2"></v-progress-linear>
    <v-alert v-if="props.error" type="error" density="compact" variant="tonal" class="my-1 mx-2">
      {{ props.error }}
    </v-alert>

    <div v-if="!props.loading && localChapters && localChapters.length > 0">
      <draggable
        v-model="localChapters"
        item-key="id"
        tag="div"
        handle=".drag-handle"
        @end="$emit('reordered', localChapters.map(c => c.id))"
        ghost-class="ghost-item"
        drag-class="drag-item"
      >
        <template #item="{ element: chapter }">
          <div> <!-- Enveloppe pour vuedraggable -->
            <v-list-item
              :key="chapter.id"
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
                      @click.stop="$emit('generate-summary', { projectId: props.projectId, chapterId: chapter.id })"
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
                    <v-list-item @click="$emit('open-edit-dialog', chapter)" title="Modifier le chapitre">
                      <template v-slot:prepend>
                        <IconPencil size="20" class="mr-3"/>
                      </template>
                      <v-list-item-title>Modifier</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="$emit('open-analysis-dialog', chapter.id)" title="Analyser le contenu du chapitre">
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
          </div>
        </template>
      </draggable>

      <v-list-item v-if="localChapters.length === 0 && !props.loading && !props.error" dense class="pl-2 py-1">
        <v-list-item-title class="text-caption font-italic text-disabled">Aucun chapitre</v-list-item-title>
      </v-list-item>
    </div>
     <v-list-item v-else-if="!props.loading && !props.error && (!localChapters || localChapters.length === 0)" dense class="pl-2 py-1">
        <v-list-item-title class="text-caption font-italic text-disabled">Aucun chapitre</v-list-item-title>
      </v-list-item>

    <v-list-item link @click="$emit('open-add-dialog')" class="mt-2">
      <template v-slot:prepend>
        <IconPlus size="20" class="mr-2"/>
      </template>
      <v-list-item-title class="text-body-2">Ajouter un chapitre</v-list-item-title>
    </v-list-item>

    <!-- Dialogues retirés d'ici et déplacés vers ProjectManager.vue -->
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import draggable from 'vuedraggable';
import {
  VListItem, VListItemTitle, VListItemSubtitle, VProgressLinear, VAlert, VBtn, VIcon, VCheckboxBtn,
  VMenu, VList, VListSubheader, VDivider, VProgressCircular
} from 'vuetify/components';
import { IconBook, IconPlus, IconTrash, IconPencil, IconGripVertical, IconDotsVertical, IconFileText, IconFileTypePdf, IconBookDownload, IconFileSearch } from '@tabler/icons-vue';

const props = defineProps({
  projectId: { type: [Number, String], required: true },
  chapters: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null },
  selectedChapterId: { type: [Number, String, null], default: null },
  selectedChapterIds: { type: Array, default: () => [] },
  exportingChapterId: { type: [Number, null], default: null },
  exportingFormat: { type: String, default: null },
  generatingSummaryChapterId: { type: [Number, null], default: null },
  loadingChapterAnalysis: { type: Boolean, default: false },
  analyzingChapterId: { type: [Number, String, null], default: null },
});

const emit = defineEmits([
  'reordered',
  'select-chapter',
  'toggle-selection',
  'handle-export',
  'open-delete',
  'open-add-dialog', // NOUVEAU
  'open-edit-dialog', // NOUVEAU
  'open-analysis-dialog', // NOUVEAU
  'generate-summary', // NOUVEAU
]);

const localChapters = ref([]);
watch(() => props.chapters, (newVal) => {
  localChapters.value = [...(newVal || [])];
}, { immediate: true, deep: true });

</script>

<style scoped>
.chapters-container {
  background-color: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 4px;
}
.dark .chapters-container {
    background-color: #2E2E2E;
    border-color: #3A3A3A;
}

.ghost-item {
  opacity: 0.5;
  background: #c8ebfb;
}
.drag-item {
  background: #e2f3fe;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.drag-handle {
  cursor: move;
  color: #aaa;
}
.dark .drag-handle {
    color: #555;
}

.list-item-hover-actions .action-btn {
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}

.list-item-hover-actions:hover .action-btn {
    visibility: visible;
    opacity: 1;
}
.summary-preview {
  font-size: 0.75rem;
  font-style: italic;
  color: grey;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}
.active-chapter {
  border-left: 3px solid currentColor;
}
</style>