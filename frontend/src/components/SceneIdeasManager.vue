<template>
  <v-container fluid class="scene-ideas-manager">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Assistance à la Création de Scènes</h1>
        <p class="mb-6">
          Utilisez les outils ci-dessous pour générer des idées, développer des concepts et surmonter le blocage de l'écrivain lors de la création de vos scènes.
        </p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="6">
        <v-card class="pa-4" elevation="2">
          <v-card-title>
            <IconBulb class="mr-2" /> Générer des Idées de Scènes
          </v-card-title>
          <v-card-text>
            Vous manquez d'inspiration ? Décrivez brièvement votre projet ou le type de scène que vous recherchez, et laissez l'IA vous proposer des pistes créatives.
          </v-card-text>
          <v-card-actions>
            <v-btn color="secondary" @click="openGenerateSceneIdeasDialog" block>
              <IconSparkles class="mr-2" />
              Lancer la Génération d'Idées
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      <!-- D'autres outils d'assistance pour les scènes pourraient être ajoutés ici à l'avenir -->
    </v-row>

    <!-- Boîte de dialogue pour générer des idées de scènes -->
    <generate-scene-ideas-dialog 
      v-model="isGenerateDialogVisible" 
      @ideas-generated="handleIdeasGenerated" 
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { VContainer, VRow, VCol, VCard, VCardTitle, VCardText, VCardActions, VBtn } from 'vuetify/components';
import { IconBulb, IconSparkles } from '@tabler/icons-vue';
import GenerateSceneIdeasDialog from './dialogs/GenerateSceneIdeasDialog.vue'; // Importer la dialogue

// State pour la visibilité du dialogue
const isGenerateDialogVisible = ref(false);

const openGenerateSceneIdeasDialog = () => {
  isGenerateDialogVisible.value = true;
};

const handleIdeasGenerated = (ideas) => {
  console.log('Idées de scènes reçues dans SceneIdeasManager:', ideas);
  // Pour l'instant, les idées sont affichées dans la dialogue elle-même.
  // On pourrait ajouter une logique ici si nécessaire (ex: les stocker, les afficher différemment).
  // displaySnackbar(`${ideas.length} idée(s) générée(s) !`, 'success');
};

// Import du snackbar si nécessaire pour des notifications directes depuis ce composant
// import { useSnackbar } from '@/composables/useSnackbar';
// const { displaySnackbar } = useSnackbar();

</script>

<style scoped>
.scene-ideas-manager {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
}
.v-card {
  transition: box-shadow 0.3s ease-in-out;
}
.v-card:hover {
  box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
}
</style>