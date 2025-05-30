<template>
  <v-toolbar flat density="compact">
    <v-toolbar-title class="text-h6 font-weight-medium">Projets</v-toolbar-title>
    <v-spacer></v-spacer>

     <v-tooltip location="bottom">
       <template v-slot:activator="{ props }">
         <v-btn
           icon
           variant="tonal"
           color="primary"
           @click="$emit('open-add-project-dialog')"
           v-bind="props"
           class="mr-1"
           title="Ajouter un projet"
           size="default"
         >
           <img :src="AjouterIconURL" alt="Ajouter projet" width="22" height="22" />
         </v-btn>
       </template>
       <span>Ajouter un projet</span>
     </v-tooltip>


     <v-tooltip location="bottom" v-if="selectedProjectIds.length > 0 || selectedChapterIds.length > 0">
       <template v-slot:activator="{ props }">
          <v-btn
            color="error"
            icon
            variant="tonal"
            @click="$emit('open-delete-confirm-dialog', 'batch', null)"
            title="Supprimer les éléments sélectionnés"
            v-bind="props"
            size="default"
          >
            <IconTrash size="22" />
          </v-btn>
       </template>
       <span>Supprimer la sélection</span>
     </v-tooltip>
  </v-toolbar>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import {
  VToolbar, VToolbarTitle, VSpacer, VBtn, VTooltip
} from 'vuetify/components';
import { IconTrash } from '@tabler/icons-vue'; 
import AjouterIconURL from '@/assets/ajouter.svg';

const props = defineProps({
  selectedProjectIds: {
    type: Array,
    default: () => []
  },
  selectedChapterIds: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits([
  'open-add-project-dialog',
  'open-delete-confirm-dialog'
]);
</script>

<style scoped>
/* Styles spécifiques à la ProjectToolbar si nécessaire */
</style>