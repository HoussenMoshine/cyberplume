<template>
  <v-dialog :model-value="show" @update:model-value="$emit('close')" persistent max-width="400px">
    <v-card v-if="deleteTarget"> <!-- Ajout de v-if ici pour s'assurer que deleteTarget existe -->
      <v-card-title class="text-h5 error--text font-weight-bold">
        <IconAlertTriangle size="24" class="mr-2" />
        Confirmer la suppression
      </v-card-title>
      <v-card-text>
        <!-- Cas de la suppression simple -->
        <span v-if="deleteTarget && deleteType === 'project'">
          Êtes-vous sûr de vouloir supprimer le projet "<strong>{{ deleteTarget.title }}</strong>" et tous ses chapitres ?
        </span>
        <span v-else-if="deleteTarget && deleteType === 'chapter'">
          Êtes-vous sûr de vouloir supprimer le chapitre "<strong>{{ deleteTarget.title }}</strong>" ?
        </span>

        <!-- Cas de la suppression par sélection -->
        <span v-else-if="deleteType === 'project-selection' || deleteType === 'chapter-selection'">
          Êtes-vous sûr de vouloir supprimer :
          <ul>
            <li v-if="targetCounts.projects > 0">{{ targetCounts.projects }} projet(s) sélectionné(s) (et leurs chapitres)</li>
            <li v-if="targetCounts.chapters > 0">{{ targetCounts.chapters }} chapitre(s) sélectionné(s)</li>
          </ul>
        </span>
        
        <br><br>
        <strong>Cette action est irréversible.</strong>
      </v-card-text>
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn color="grey darken-1" variant="text" @click="$emit('close')" :disabled="loading">
          Annuler
        </v-btn>
        <v-btn
          color="error"
          variant="flat"
@click="() => { console.log('[DeleteConfirmDialog] Delete button clicked'); $emit('confirm'); }"
          :loading="loading"
        >
          Supprimer
        </v-btn>
      </v-card-actions>
    </v-card>
     <!-- Optionnel: Afficher quelque chose si deleteTarget est null mais show est true (ne devrait pas arriver) -->
     <v-card v-else>
        <v-card-text>Chargement...</v-card-text>
     </v-card>
  </v-dialog>
</template>

<script setup>
import { IconAlertTriangle } from '@tabler/icons-vue';
import { VDialog, VCard, VCardTitle, VCardText, VCardActions, VBtn, VSpacer } from 'vuetify/components';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
deleteType: {
    type: String,
    default: ''
  },
  deleteTarget: {
    type: [Object, null], // Autoriser null
    default: null 
  },
  // Pour l'affichage de la suppression multiple
  targetCounts: {
      type: Object, // { projects: number, chapters: number }
      default: () => ({ projects: 0, chapters: 0 })
  }
});

defineEmits(['close', 'confirm']);
</script>

<style scoped>
.error--text {
  color: rgb(var(--v-theme-error));
}
strong {
  font-weight: bold;
}
ul {
    padding-left: 20px;
    margin-top: 5px;
}
</style>