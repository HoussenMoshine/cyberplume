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
import { ref, onMounted, onUnmounted } from 'vue';
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
    // Si un chapitre est sélectionné, s'assurer que l'onglet éditeur est actif
    // et que le mode sans distraction est désactivé si besoin.
    activeTab.value = 'editor';
    if (isDistractionFree.value) {
        toggleDistractionFreeMode();
    }
  }
  // Réinitialiser le flag après un court délai pour permettre au changement d'onglet de se terminer
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
  // et qu'aucun chapitre n'est actuellement sélectionné (ou si on veut forcer le rechargement du dernier),
  // on pourrait ajouter une logique ici. Pour l'instant, on laisse Vuetify gérer le changement d'onglet.
  // Si currentChapterId.value est null, ProjectManager devrait afficher la liste des projets.
};

const updateGlobalAISettings = (settings) => {
  if (settings.provider) globalAIProvider.value = settings.provider;
  if (settings.model) globalAIModel.value = settings.model;
  if (settings.style) globalAIStyle.value = settings.style;
  if (settings.customDescription) globalCustomAIDescription.value = settings.customDescription;
};

// Logique pour s'assurer que ProjectManager est masqué si un onglet autre que 'editor' ou 'characters' est actif
// Ceci est géré par le v-if sur le composant ProjectManager directement dans le template.
// Cependant, il faut s'assurer que si on clique sur "Personnages" ou "Idées de Scènes" ou "Config",
// le currentChapterId est désélectionné pour éviter que l'éditeur ne reste sur un chapitre.
// Ou alors, on laisse l'éditeur afficher le dernier chapitre, et seul ProjectManager est masqué.
// L'approche actuelle masque ProjectManager si activeTab n'est pas 'editor' ou 'characters'.
// J'ai modifié le v-if pour inclure 'sceneIdeas' dans les conditions de masquage de ProjectManager.

</script>

<style>
/* Ajustement pour la densité compacte de la barre d'outils */
:root {
  --v-layout-top: 48px; /* Hauteur de la barre d'app compacte */
}

html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  /* overflow: hidden; Supprimé pour permettre le défilement de la page si nécessaire */
}

.v-application {
  font-family: 'Roboto', sans-serif;
  background-color: #f5f5f5; /* Un gris clair pour le fond général */
  min-height: 100vh; /* Utiliser min-height pour permettre l'expansion */
  display: flex;
  flex-direction: column;
}

.v-application__wrap {
  flex: 1 1 auto; 
  display: flex;
  flex-direction: column;
  /* overflow: hidden; Supprimé */
}

.v-main {
  padding-top: var(--v-layout-top);
  flex: 1 1 auto; /* Permet à v-main de prendre l'espace vertical */
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* Permet à v-main de défiler si son contenu (v-window) est trop grand */
                   /* C'est un fallback si la gestion flex interne ne suffit pas */
}

.v-window {
  flex: 1 1 auto; /* Permet à v-window de s'étendre dans v-main */
  display: flex;
  flex-direction: column;
  min-height: 0; /* Important pour que les enfants flex puissent se réduire */
}

.v-window-item {
  flex: 1 1 auto; /* Permet à v-window-item de s'étendre dans v-window */
  display: flex;
  flex-direction: column;
  min-height: 0; /* Important pour que les enfants flex puissent se réduire */
}

/* Spécifique pour l'éditeur, s'assure qu'il prend toute la hauteur de son parent .v-window-item */
.editor-window-item {
  height: 100%; 
}

/* Mode sans distraction */
.distraction-free .v-main {
  padding-left: 0 !important;
  padding-top: 0 !important; /* En mode sans distraction, la barre d'app est cachée */
}

</style>