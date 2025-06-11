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
            @click="determineDeleteTypeAndEmit"
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
const determineDeleteTypeAndEmit = () => {
  const hasProjects = props.selectedProjectIds.length > 0;
  const hasChapters = props.selectedChapterIds.length > 0;

  if (hasChapters && !hasProjects) {
    // Si seulement des chapitres sont sélectionnés
    emit('open-delete-confirm-dialog', null, 'chapter-selection');
  } else if (hasProjects && !hasChapters) {
    // Si seulement des projets sont sélectionnés
    emit('open-delete-confirm-dialog', null, 'project-selection');
  } else if (hasProjects && hasChapters) {
    // Si des projets ET des chapitres sont sélectionnés (cas mixte)
    // La logique actuelle dans ProjectManager.confirmDelete ne gère pas un type "mixte"
    // pour supprimer les deux types d'entités en une seule action via ce dialogue.
    // Pour l'instant, on pourrait prioriser ou émettre un type spécifique que ProjectManager
    // devrait être adapté pour gérer (par exemple, 'batch-mixed').
    // Option: émettre pour chapitres si présents, sinon projets.
    // Cela nécessiterait que l'utilisateur fasse deux opérations de suppression distinctes
    // s'il veut supprimer des sélections mixtes.
    // Pour ce correctif, nous allons émettre 'chapter-selection' si des chapitres sont sélectionnés,
    // car c'est le bug que nous essayons de résoudre en premier.
    // Une meilleure gestion de la suppression mixte pourrait être une amélioration future.
    // Ou, on pourrait désactiver le bouton de suppression si la sélection est mixte.
    console.warn("Tentative de suppression par lot d'une sélection mixte (projets et chapitres). Traitement comme 'chapter-selection' pour l'instant si des chapitres sont sélectionnés, sinon 'project-selection'.");
    if (hasChapters) {
        emit('open-delete-confirm-dialog', null, 'chapter-selection');
    } else { // Implique hasProjects est vrai
        emit('open-delete-confirm-dialog', null, 'project-selection');
    }
  }
  // Note: Le bouton de suppression (v-if ligne 25) ne s'affiche que si l'une des sélections n'est pas vide.
};
</script>

<style scoped>
/* Styles spécifiques à la ProjectToolbar si nécessaire */
</style>