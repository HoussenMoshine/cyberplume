<template>

  <v-app :class="{ 'distraction-free': isDistractionFree }">

    <!-- Masquer la barre d'app en mode sans distraction -->
    <!-- Ajout de elevation="0" pour un style plat -->
    <v-app-bar app color="primary" density="compact" v-if="!isDistractionFree" elevation="0">
      <img src="@/assets/cyberplume.svg" alt="CyberPlume Logo" height="30" class="mr-3 ml-3" />
      <v-tabs v-model="activeTab" align-tabs="center">
        <v-tab value="editor" @click="handleEditorTabClick">
          <IconFileText size="20" class="mr-2" />
          Éditeur
        </v-tab>
        <v-tab value="characters">
          <IconUsers size="20" class="mr-2" />
          Personnages
        </v-tab>
        <v-tab value="config">
          <IconSettings size="20" class="mr-2" />
          Configuration
        </v-tab>
      </v-tabs>
    </v-app-bar>


    <!-- Masquer le gestionnaire de projet en mode sans distraction ou si l'onglet config est actif -->
    <project-manager
      v-if="!isDistractionFree && activeTab !== 'config'"
      @chapter-selected="handleChapterSelection"
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
            :selected-chapter-id="currentChapterId"
            :active-chapter-title="currentChapterTitle"
            :is-distraction-free="isDistractionFree"
            @toggle-distraction-free="toggleDistractionFreeMode"
            @ai-settings-changed="updateGlobalAISettings"
          />
        </v-window-item>
        <v-window-item value="characters">
          <!-- Le CharacterManager ne s'affiche que si l'onglet characters est actif et pas en mode sans distraction -->
          <character-manager v-if="!isDistractionFree && activeTab === 'characters'" />
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
import { ref, onMounted, onUnmounted } from 'vue';
import EditorComponent from './components/EditorComponent.vue';
import ProjectManager from './components/ProjectManager.vue';
import CharacterManager from './components/CharacterManager.vue';
import ApiKeysManager from './components/ApiKeysManager.vue';

// Import des composants Vuetify utilisés
import {
  VApp, VAppBar, VTabs, VTab, VMain, VWindow, VWindowItem, VSnackbar, VBtn // Ajout VSnackbar, VBtn
} from 'vuetify/components';

// Import des icônes Tabler
import { IconFileText, IconUsers, IconSettings } from '@tabler/icons-vue';
import { config } from '@/config.js';

// Import et utilisation du composable Snackbar
import { useSnackbar } from '@/composables/useSnackbar.js';
const { 
  showSnackbar: isSnackbarVisible, // Renommer pour clarté (c'est la ref booléenne)
  snackbarMessage, 
  snackbarColor, 
  snackbarTimeout 
  // displaySnackbar n'est pas appelé directement ici, mais par les autres composants
} = useSnackbar();


// State pour la sélection IA globale
const globalAIProvider = ref(config.defaultProvider);
const globalAIModel = ref(null);
const globalAIStyle = ref('normal');
const globalCustomAIDescription = ref(null);

// State pour l'onglet actif
const activeTab = ref('editor');

// State pour l'ID et le titre du chapitre sélectionné
const currentChapterId = ref(null);
const currentChapterTitle = ref(null);

// Référence vers l'instance de EditorComponent
const editorComponentRef = ref(null);

// State pour le mode sans distraction
const isDistractionFree = ref(false);

// Flag pour différencier un clic sur l'onglet d'une sélection de contenu
let isSelectionEvent = false;

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
    if (editorComponentRef.value && typeof editorComponentRef.value.triggerManualSave === 'function') {
      editorComponentRef.value.triggerManualSave();
    } else {
      console.warn("EditorComponent reference or triggerManualSave method not found!");
    }
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyboardShortcuts);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyboardShortcuts);
});

const handleChapterSelection = (payload) => {
  console.log("App.vue: handleChapterSelection payload:", payload);
  isSelectionEvent = true;
  currentChapterId.value = payload && payload.chapterId !== undefined ? payload.chapterId : null;
  console.log("App.vue: currentChapterId.value set to", currentChapterId.value);
  currentChapterTitle.value = null; // Sera mis à jour par EditorComponent via une prop ou un watch interne
  if (payload && payload.chapterId !== null) {
    activeTab.value = 'editor';
    if (isDistractionFree.value) {
        toggleDistractionFreeMode();
    }
  }
  setTimeout(() => { isSelectionEvent = false; }, 50);
};

const handleInsertGeneratedContent = (content) => {
  if (editorComponentRef.value && typeof editorComponentRef.value.insertGeneratedContent === 'function') {
    editorComponentRef.value.insertGeneratedContent(content);
  } else {
     console.warn("EditorComponent reference or insertGeneratedContent method not found for direct insertion!");
     // Fallback: Peut-être copier dans le presse-papiers ou afficher dans un dialogue
  }
};

const handleApplySuggestionToEditor = (suggestionData) => {
  if (editorComponentRef.value && typeof editorComponentRef.value.handleApplySuggestionToEditor === 'function') {
    editorComponentRef.value.handleApplySuggestionToEditor(suggestionData);
  } else {
    console.warn("EditorComponent reference or handleApplySuggestionToEditor method not found!");
  }
};


const handleEditorTabClick = () => {
  if (isSelectionEvent) {
    // Si c'était une sélection de contenu qui a changé l'onglet, ne rien faire de plus
    return;
  }
  // Si l'utilisateur clique manuellement sur l'onglet Éditeur
  // et qu'aucun chapitre n'est actif, on pourrait vouloir désactiver l'éditeur
  // ou afficher un message. Pour l'instant, on ne fait rien de spécial.
  // Si un chapitre est actif, il reste actif.
};

const updateGlobalAISettings = (settings) => {
  if (settings.provider) globalAIProvider.value = settings.provider;
  if (settings.model) globalAIModel.value = settings.model;
  if (settings.style) globalAIStyle.value = settings.style;
  if (settings.customDescription) globalCustomAIDescription.value = settings.customDescription;
};


</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden; /* Empêche le défilement global de la page */
}

.v-application {
  height: 100vh; /* Assure que v-app prend toute la hauteur de la fenêtre */
  display: flex;
  flex-direction: column;
}

.v-main {
  flex-grow: 1;
  overflow-y: auto; /* Permet le défilement à l'intérieur de v-main si nécessaire */
  display: flex; /* Pour que v-window puisse grandir */
  flex-direction: column;
}

.v-window {
  flex-grow: 1; /* Permet à v-window de prendre l'espace restant */
  display: flex; /* Pour que v-window-item puisse grandir */
  flex-direction: column;
}

.v-window-item {
  flex-grow: 1; /* Permet à v-window-item de prendre l'espace restant */
  display: flex; /* Pour que son contenu (EditorComponent) puisse grandir */
  flex-direction: column;
  height: 100%; /* S'assurer que l'item prend toute la hauteur de la window */
}

.editor-window-item {
  /* S'assurer que l'éditeur peut prendre toute la place */
  height: calc(100vh - var(--v-toolbar-height, 48px) - var(--v-tabs-height, 48px)); /* Ajuster selon la hauteur réelle de l'app-bar et des tabs */
}
.v-app.distraction-free .v-main {
  padding: 0 !important;
}

.v-app.distraction-free .editor-window-item {
  height: 100vh; /* Prend toute la hauteur en mode sans distraction */
}

</style>