<template>

  <v-app :class="{ 'distraction-free': isDistractionFree }" :style="appStyle">

    <!-- Masquer la barre d'app en mode sans distraction -->
    <!-- Ajout de elevation="0" pour un style plat -->
    <v-app-bar app color="primary" density="compact" v-if="!isDistractionFree" elevation="0">
      <img src="@/assets/cyberplume.svg" alt="CyberPlume Logo" height="30" class="mr-3 ml-3" />
      <v-tabs v-model="activeTab" align-tabs="center">
        <v-tab value="editor">
          <IconFileText size="20" class="mr-2" />
          Éditeur
        </v-tab>
        <v-tab value="characters">
          <IconUsers size="20" class="mr-2" />
          Personnages
        </v-tab>
        <v-tab value="sceneIdeas">
          <IconBulb size="20" class="mr-2" />
          Idées de Scènes
        </v-tab>
        <v-tab value="config">
          <IconSettings size="20" class="mr-2" />
          Configuration
        </v-tab>
      </v-tabs>
    </v-app-bar>


    <!-- Masquer le gestionnaire de projet en mode sans distraction ou si l'onglet config ou sceneIdeas est actif -->
    <project-manager
      v-if="!isDistractionFree && activeTab !== 'config' && activeTab !== 'sceneIdeas'"
      :selected-chapter-id="currentChapterId"
      @chapter-selected="handleChapterAirlock"
      @insert-generated-content="handleInsertGeneratedContent"
      @apply-suggestion-to-editor="handleApplySuggestionToEditor"
      :current-ai-provider="globalAIProvider"
      :current-ai-model="globalAIModel"
      :current-ai-style="globalAIStyle"
      :current-custom-ai-description="globalCustomAIDescription"
    />


    <v-main>
      <v-window v-model="activeTab">
        <v-window-item value="editor" class="editor-window-item">
          <editor-component
            ref="editorComponentRef"
            :is-distraction-free="isDistractionFree"
            @toggle-distraction-free="toggleDistractionFreeMode"
            @ai-settings-changed="updateGlobalAISettings"
          />
        </v-window-item>
        <v-window-item value="characters">
          <!-- Le CharacterManager ne s'affiche que si l'onglet characters est actif et pas en mode sans distraction -->
          <character-manager v-if="!isDistractionFree && activeTab === 'characters'" />
        </v-window-item>
        <v-window-item value="sceneIdeas">
          <!-- Le SceneIdeasManager ne s'affiche que si l'onglet sceneIdeas est actif et pas en mode sans distraction -->
          <scene-ideas-manager v-if="!isDistractionFree && activeTab === 'sceneIdeas'" />
        </v-window-item>
        <v-window-item value="config">
           <!-- Le ApiKeysManager ne s'affiche que si l'onglet config est actif et pas en mode sans distraction -->
          <api-keys-manager v-if="!isDistractionFree && activeTab === 'config'" />
        </v-window-item>
        
      </v-window>
    </v-main>

    <!-- Snackbar Global -->
    <v-snackbar
      v-model="isSnackbarVisible"
      :timeout="snackbarTimeout"
      :color="snackbarColor"
      location="bottom right"
      multi-line
    >
      {{ snackbarMessage }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="isSnackbarVisible = false"
        >
          Fermer
        </v-btn>
      </template>
    </v-snackbar>

  </v-app>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useTypography } from '@/composables/useTypography.js';
import EditorComponent from './components/EditorComponent.vue';
import ProjectManager from './components/ProjectManager.vue';
import CharacterManager from './components/CharacterManager.vue';
import SceneIdeasManager from './components/SceneIdeasManager.vue'; // Ajout de l'import
import ApiKeysManager from './components/ApiKeysManager.vue';

// Import des composants Vuetify utilisés
import {
  VApp, VAppBar, VTabs, VTab, VMain, VWindow, VWindowItem, VSnackbar, VBtn
} from 'vuetify/components';

// Import des icônes Tabler
import { IconFileText, IconUsers, IconSettings, IconBulb } from '@tabler/icons-vue'; // Ajout de IconBulb
import { config } from '@/config.js';

// Gestion de la typographie
const { fontSize } = useTypography();
const appStyle = computed(() => ({
  fontSize: `${fontSize.value}px`,
}));

// Import et utilisation du composable Snackbar
import { useSnackbar } from '@/composables/useSnackbar.js';
const { 
  showSnackbar: isSnackbarVisible, 
  snackbarMessage, 
  snackbarColor, 
  snackbarTimeout 
} = useSnackbar();


// State pour la sélection IA globale
const globalAIProvider = ref(config.defaultProvider);
const globalAIModel = ref(null);
const globalAIStyle = ref('normal');
const globalCustomAIDescription = ref(null);

// State pour l'onglet actif
const activeTab = ref('editor');

// State pour l'ID du chapitre sélectionné
const currentChapterId = ref(null);

// Référence vers l'instance de EditorComponent
const editorComponentRef = ref(null);

// State pour le mode sans distraction
const isDistractionFree = ref(false);

const toggleDistractionFreeMode = () => {
  isDistractionFree.value = !isDistractionFree.value;
};

const handleKeyboardShortcuts = (event) => {
  if (event.key === 'Escape' && isDistractionFree.value) {
    toggleDistractionFreeMode();
    return;
  }
  const isCtrlOrCmd = event.ctrlKey || event.metaKey;
  if (isCtrlOrCmd && event.key === 's') {
    event.preventDefault();
    if (editorComponentRef.value && typeof editorComponentRef.value.saveChapter === 'function') {
      editorComponentRef.value.saveChapter(true); // true for manual save
    } else {
      console.warn("EditorComponent reference or saveChapter method not found!");
    }
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyboardShortcuts);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboardShortcuts);
});

/**
 * Gère la sélection d'un chapitre en orchestrant la sauvegarde et le chargement.
 * C'est le "Data Airlock" pour prévenir les race conditions.
 */
async function handleChapterAirlock(payload) {
  if (!editorComponentRef.value) {
    console.error("La référence du composant éditeur n'est pas disponible.");
    return;
  }

  // 1. Sauvegarder le chapitre actuel (la méthode interne vérifie s'il y a des changements)
  const saveSuccess = await editorComponentRef.value.saveChapter(false); // false for auto-save

  if (!saveSuccess) {
    // Pour l'instant, on avertit et on continue. On pourrait demander confirmation à l'utilisateur.
    console.warn("La sauvegarde du chapitre précédent a échoué. Le chargement continue, mais des changements pourraient être perdus.");
  }

  // 2. Mettre à jour l'ID du chapitre sélectionné globalement
  const newChapterId = payload && payload.chapterId !== undefined ? payload.chapterId : null;
  currentChapterId.value = newChapterId;

  // 3. Charger le nouveau chapitre dans l'éditeur
  await editorComponentRef.value.loadChapter(newChapterId);
  
  // 4. S'assurer que l'onglet éditeur est actif si un chapitre est sélectionné
  if (newChapterId !== null) {
    activeTab.value = 'editor';
  }
}


const handleInsertGeneratedContent = (content) => {
  if (editorComponentRef.value && typeof editorComponentRef.value.insertGeneratedContent === 'function') {
    editorComponentRef.value.insertGeneratedContent(content);
  } else {
    console.warn("EditorComponent reference or insertGeneratedContent method not found!");
  }
};

const handleApplySuggestionToEditor = (content) => {
  if (editorComponentRef.value && typeof editorComponentRef.value.setContent === 'function') {
    editorComponentRef.value.setContent(content);
  } else {
    console.warn("EditorComponent reference or setContent method not found!");
  }
};

const updateGlobalAISettings = (settings) => {
  globalAIProvider.value = settings.provider;
  globalAIModel.value = settings.model;
  globalAIStyle.value = settings.style;
  globalCustomAIDescription.value = settings.customDescription;
};

</script>

<style>
.distraction-free .v-main {
  padding: 0 !important;
}

/* Assure que l'éditeur TipTap hérite de la taille de police globale */
.ProseMirror {
  font-size: inherit !important;
}
</style>