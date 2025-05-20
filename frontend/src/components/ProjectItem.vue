<template>
  <v-card
    class="mb-3 project-card"
    variant="outlined"
    elevation="1"
  >
    <v-list-item
      class="list-item-hover-actions project-header pa-2"
      density="default"
      min-height="52px"
      @click.prevent
    >
      <template v-slot:prepend>
        <v-checkbox-btn
          :model-value="selectedProjectIds.includes(project.id)"
          @update:model-value="$emit('toggle-selection', project.id)"
          density="default"
          @click.stop
          class="mr-2 flex-grow-0"
        ></v-checkbox-btn>
        <IconFolder size="24" class="mr-2" />
      </template>

      <v-list-item-title class="text-subtitle-1 font-weight-bold">{{ project.title }}</v-list-item-title>

      <template v-slot:append>
        <v-menu location="bottom end">
          <template v-slot:activator="{ props }">
            <v-btn
              icon
              density="default"
              variant="text"
              v-bind="props"
              @click.stop
              title="Actions Projet"
              class="action-menu-btn"
              size="default"
            >
              <IconDotsVertical size="22" />
            </v-btn>
          </template>
          <v-list density="compact">
            <v-list-item @click="$emit('open-edit', project)" title="Renommer">
              <template v-slot:prepend>
                <img :src="EditerIconURL" alt="Renommer" width="20" height="20" class="mr-3" />
              </template>
            </v-list-item>
            <v-list-item @click="$emit('open-analysis', project.id)" title="Analyser Cohérence">
               <template v-slot:prepend>
                 <IconScan size="20" class="mr-3"/>
               </template>
            </v-list-item>

            <v-divider class="my-1"></v-divider>
            <v-list-subheader>Exporter Projet</v-list-subheader>
            <v-list-item
              @click="$emit('handle-export', project.id, 'docx')"
              :disabled="!!exportingProjectId"
              title="Exporter Projet en DOCX"
            >
              <template v-slot:prepend>
                 <IconFileText size="20" class="mr-3"/>
              </template>
              <v-list-item-title>DOCX</v-list-item-title>
              <template v-slot:append v-if="exportingProjectId === project.id && exportingFormat === 'docx'">
                <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
              </template>
            </v-list-item>
             <v-list-item
              @click="$emit('handle-export', project.id, 'pdf')"
              :disabled="!!exportingProjectId"
              title="Exporter Projet en PDF"
            >
              <template v-slot:prepend>
                 <IconFileTypePdf size="20" class="mr-3"/>
              </template>
              <v-list-item-title>PDF</v-list-item-title>
               <template v-slot:append v-if="exportingProjectId === project.id && exportingFormat === 'pdf'">
                 <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
               </template>
             </v-list-item>
             <v-list-item
              @click="$emit('handle-export', project.id, 'txt')"
              :disabled="!!exportingProjectId"
              title="Exporter Projet en TXT"
            >
               <template v-slot:prepend>
                 <IconFileText size="20" class="mr-3"/>
               </template>
              <v-list-item-title>TXT</v-list-item-title>
               <template v-slot:append v-if="exportingProjectId === project.id && exportingFormat === 'txt'">
                 <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
               </template>
             </v-list-item>
             <v-list-item
              @click="$emit('handle-export', project.id, 'epub')"
              :disabled="!!exportingProjectId"
              title="Exporter Projet en EPUB"
            >
               <template v-slot:prepend>
                 <IconBook size="20" class="mr-3"/>
               </template>
              <v-list-item-title>EPUB</v-list-item-title>
               <template v-slot:append v-if="exportingProjectId === project.id && exportingFormat === 'epub'">
                 <v-progress-circular indeterminate size="16" width="2" color="primary"></v-progress-circular>
               </template>
             </v-list-item>

            <v-divider class="my-1"></v-divider>
            <v-list-item @click="$emit('open-delete', project, 'project')" title="Supprimer" class="text-error">
               <template v-slot:prepend>
                 <img :src="PoubelleIconURL" alt="Supprimer" width="20" height="20" class="mr-3" />
               </template>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-list-item>

    <slot name="chapter-list"></slot>

  </v-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import {
  VCard, VListItem, VListItemTitle, VListSubheader,
  VBtn, VMenu, VDivider, VCheckboxBtn, VProgressCircular, VList
} from 'vuetify/components';

import {
  IconFolder, IconDotsVertical, IconSquarePlus, IconScan, // IconPencil supprimée
  IconFileText, IconFileTypePdf, IconBook // IconTrash supprimée
} from '@tabler/icons-vue';
import EditerIconURL from '@/assets/editer.svg'; // Ajout de l'import pour l'icône SVG
import PoubelleIconURL from '@/assets/poubelle.svg';

const props = defineProps({
  project: {
    type: Object,
    required: true
  },
  selectedProjectIds: {
    type: Array,
    default: () => []
  },
  exportingProjectId: {
    type: [Number, null],
    default: null
  },
  exportingFormat: {
    type: [String, null],
    default: null
  }
});

const emit = defineEmits([
  'toggle-selection',
  'open-edit',
  'open-analysis',
  'handle-export',
  'open-delete'
]);

</script>

<style scoped>
.project-card {
  border-radius: 8px;
  overflow: hidden;
}

.project-header {
  border-bottom: 1px solid #E0E0E0; /* Updated border color */
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

.v-menu__content .action-menu-btn {
    visibility: visible !important;
    opacity: 1 !important;
}
</style>