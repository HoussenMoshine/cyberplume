<template>
  <v-toolbar flat density="compact">
    <v-toolbar-title class="text-h6 font-weight-medium">Projets</v-toolbar-title>
    <v-spacer></v-spacer>

    <v-tooltip location="bottom">
      <template v-slot:activator="{ props }">
        <v-btn
          icon
          variant="tonal"
          color="secondary"
          @click="$emit('open-generate-scene-dialog')"
          v-bind="props"
          class="mr-1"
          title="Générer une ébauche de Scène par IA"
          size="default"
        >
          <!-- Utilisation directe de l'icône importée -->
          <IconMovie size="22" />
        </v-btn>
      </template>
      <span>Générer une ébauche de Scène par IA</span>
    </v-tooltip>

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
           <!-- Remplacement par l'icône SVG personnalisée -->
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
            <!-- Utilisation directe de l'icône importée -->
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
// Import des icônes Tabler nécessaires (importation nommée)
import { IconMovie, IconTrash } from '@tabler/icons-vue'; // IconPlus supprimée
import AjouterIconURL from '@/assets/ajouter.svg'; // Ajout de l'import pour l'icône SVG

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
  'open-generate-scene-dialog',
  'open-add-project-dialog',
  'open-delete-confirm-dialog'
]);
</script>

<style scoped>
/* Styles spécifiques à la ProjectToolbar si nécessaire */
</style>