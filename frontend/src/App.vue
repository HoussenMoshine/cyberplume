<template>

  <v-app :class="{ 'distraction-free': isDistractionFree }">

    <!-- Masquer la barre d'app en mode sans distraction -->
    <!-- Ajout de elevation="0" pour un style plat -->
    <v-app-bar app color="primary" density="compact" v-if="!isDistractionFree" elevation="0">
<img src="@/assets/cyberplume.svg" alt="CyberPlume Logo" height="30" class="mr-3 ml-3" />
      <v-tabs v-model="activeTab" align-tabs="center"> <!-- Garder v-model pour le style actif -->
        <v-tab value="editor" @click="handleEditorTabClick"> <!-- Ajouter @click -->
          <!-- Utilisation directe de l'icône importée -->
          <IconFileText size="20" class="mr-2" />
          Éditeur
        </v-tab>
        <v-tab value="characters"> <!-- @click="activeAgent = null" supprimé -->
          <!-- Utilisation directe de l'icône importée -->
          <IconUsers size="20" class="mr-2" />
          Personnages
        </v-tab>

      </v-tabs>
    </v-app-bar>


    <!-- Masquer le gestionnaire de projet en mode sans distraction -->
    <project-manager
      v-if="!isDistractionFree"
      @chapter-selected="handleChapterSelection"
      @scene-selected="handleSceneSelection"
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
            :selected-scene-id="currentSceneId"
            :active-chapter-title="currentChapterTitle"
            :active-scene-title="currentSceneTitle"
            :is-distraction-free="isDistractionFree"
            @toggle-distraction-free="toggleDistractionFreeMode"
            @ai-settings-changed="updateGlobalAISettings"
          />
        </v-window-item>
        <v-window-item value="characters">
          <character-manager v-if="!isDistractionFree" />
        </v-window-item>
        
      </v-window>
    </v-main>

  </v-app>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import EditorComponent from './components/EditorComponent.vue';
import ProjectManager from './components/ProjectManager.vue';
import CharacterManager from './components/CharacterManager.vue';
// import NarrativeTwistGeneratorDialog from './components/dialogs/NarrativeTwistGeneratorDialog.vue'; // Supprimé

// Import des composants Vuetify utilisés
import {
  VApp, VAppBar, VTabs, VTab, VMain, VWindow, VWindowItem,
  // VMenu, VList, VListItem // VMenu, VList, VListItem pourraient être supprimés si plus utilisés ailleurs
} from 'vuetify/components';

// Import des icônes Tabler
import { IconFileText, IconUsers } from '@tabler/icons-vue'; // IconSparkles supprimé
import { config } from '@/config.js';

// State pour la sélection IA globale
const globalAIProvider = ref(config.defaultProvider);
const globalAIModel = ref(null);
const globalAIStyle = ref('normal');
const globalCustomAIDescription = ref(null);

// State pour l'onglet actif
const activeTab = ref('editor');

// State pour l'agent actif (utilisé pour les agents qui ne sont pas des dialogues)
// const activeAgent = ref(null); // Supprimé

// State pour contrôler la visibilité du dialogue de twists narratifs
// const showNarrativeTwistDialog = ref(false); // Supprimé

// State pour l'ID et le titre du chapitre/scène sélectionné
const currentChapterId = ref(null);
const currentChapterTitle = ref(null);
const currentSceneId = ref(null);
const currentSceneTitle = ref(null);

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

const handleChapterSelection = (chapterId) => {
  console.log("App.vue: handleChapterSelection", chapterId);
  isSelectionEvent = true;
  currentChapterId.value = chapterId ?? null;
  currentChapterTitle.value = null;
  currentSceneId.value = null;
  currentSceneTitle.value = null;
  // activeAgent.value = null; // Supprimé
  if (chapterId !== null) {
    activeTab.value = 'editor';
    if (isDistractionFree.value) {
        toggleDistractionFreeMode();
    }
  }
  setTimeout(() => { isSelectionEvent = false; }, 50);
};

const handleSceneSelection = (sceneId) => {
  console.log("App.vue: handleSceneSelection", sceneId);
  isSelectionEvent = true;
  currentSceneId.value = sceneId ?? null;
  currentSceneTitle.value = null;
  // activeAgent.value = null; // Supprimé
  if (sceneId !== null) {
    currentChapterId.value = null;
    currentChapterTitle.value = null;
    activeTab.value = 'editor';
    if (isDistractionFree.value) {
        toggleDistractionFreeMode();
    }
  }
  setTimeout(() => { isSelectionEvent = false; }, 50);
};

const handleInsertGeneratedContent = (content) => {
  console.log("App.vue: handleInsertGeneratedContent");
  if (editorComponentRef.value && typeof editorComponentRef.value.insertContentAtCursor === 'function') {
    editorComponentRef.value.insertContentAtCursor(content);
    activeTab.value = 'editor';
    // activeAgent.value = null; // Supprimé
  } else {
    console.error("EditorComponent reference or insertContentAtCursor method not found!");
  }
};

const handleApplySuggestionToEditor = (suggestionData) => {
  console.log("App.vue: handleApplySuggestionToEditor");
  if (editorComponentRef.value && typeof editorComponentRef.value.applySuggestion === 'function') {
    editorComponentRef.value.applySuggestion(suggestionData);
    activeTab.value = 'editor';
    // activeAgent.value = null; // Supprimé
  } else {
    console.error("EditorComponent reference or applySuggestion method not found!");
  }
};

const updateGlobalAISettings = (settings) => {
  if (settings) {
    globalAIProvider.value = settings.provider;
    globalAIModel.value = settings.model;
    globalAIStyle.value = settings.style;
    globalCustomAIDescription.value = settings.customDescription;
  }
};

const handleEditorTabClick = () => {
  if (!isSelectionEvent) {
    activeTab.value = 'editor';
    // activeAgent.value = null; // Supprimé
  }
};

// const handleAgentSelection = (agentName) => { // Fonction supprimée
//   console.log(`Agent sélectionné: ${agentName}`);
//   if (agentName === 'narrative_twist') {
//     showNarrativeTwistDialog.value = true;
//     activeTab.value = 'editor'; // Rester ou revenir à l'éditeur en arrière-plan
//     activeAgent.value = null; // L'agent est géré par le dialogue modal
//   } else {
//     activeAgent.value = agentName;
//     activeTab.value = 'agents_view'; 
//   }
//   if (isDistractionFree.value) {
//     toggleDistractionFreeMode();
//   }
// };

</script>

<style> 
.v-application {
  background-color: var(--v-theme-background-lighten-1) !important; 
}

.distraction-free .v-main {
  padding: 0 !important;
  margin: 0 !important;
  height: 100vh;
  width: 100vw;
  overflow: hidden; 
}

.editor-window-item {
  height: 100%; 
}

.v-main {
  overflow-y: auto; 
}

</style>