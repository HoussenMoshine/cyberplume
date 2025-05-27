<template>
  <div class="editor-component-wrapper">
    <v-container :fluid="isDistractionFree" :class="{ 'pa-0': isDistractionFree }">
      <div class="mb-2 d-flex align-center" v-if="!isDistractionFree">
        <v-chip v-if="activeType === 'chapter'" color="blue" label size="small">
          Chapitre Actif
        </v-chip>
        <v-chip v-else-if="activeType === 'scene'" color="green" label size="small">
          Scène Active
        </v-chip>
        <v-chip v-else color="grey" label size="small">
          Aucun contenu sélectionné
        </v-chip>

        <span v-if="activeTitle" class="ml-2 font-weight-bold text-subtitle-1">{{ activeTitle }}</span>
        <v-spacer></v-spacer>

        <v-tooltip location="bottom">
          <template v-slot:activator="{ props: tooltipProps }">
            <v-btn
              icon
              variant="tonal"
              :color="isDistractionFree ? 'grey' : 'secondary'"
              @click="toggleDistractionFree"
              v-bind="tooltipProps"
              size="small"
              class="mr-2"
            >
              <!-- Utilisation directe de l'icône importée -->
              <component :is="isDistractionFree ? IconMinimize : IconMaximize" size="20" />
            </v-btn>
          </template>
          <span>{{ isDistractionFree ? 'Quitter le mode sans distraction' : 'Mode sans distraction' }}</span>
        </v-tooltip>

        <v-tooltip location="bottom">
          <template v-slot:activator="{ props: tooltipProps }">
            <v-btn
              icon
              variant="tonal"
              color="primary"
              @click="triggerManualSave"
              :disabled="isSaving || !activeId"
              :loading="isSaving"
              v-bind="tooltipProps"
              size="small"
            >
              <!-- Remplacement par l'icône SVG personnalisée -->
              <img :src="EnregistrerIconURL" alt="Enregistrer" width="20" height="20" />
            </v-btn>
          </template>
          <span>Enregistrer ({{ hasUnsavedChanges ? 'Modifications non enregistrées' : 'À jour' }})</span>
        </v-tooltip>
      </div>

      <v-toolbar density="compact" flat class="mb-2 editor-toolbar" v-if="editor && editor.isEditable && !isDistractionFree">
        <v-btn icon size="small" @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }">
          <IconBold size="20" />
        </v-btn>
        <v-btn icon size="small" @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }">
          <IconItalic size="20" />
        </v-btn>
        <v-btn icon size="small" @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }">
          <IconStrikethrough size="20" />
        </v-btn>
        <v-divider vertical inset class="mx-1"></v-divider>
        <v-btn icon size="small" @click="editor.chain().focus().setParagraph().run()" :class="{ 'is-active': editor.isActive('paragraph') }">
          <IconTypography size="20" />
        </v-btn>
        <v-btn icon size="small" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }">
          <IconH1 size="20" />
        </v-btn>
        <v-btn icon size="small" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }">
          <IconH2 size="20" />
        </v-btn>
        <!-- Bouton pour ajouter une règle horizontale (si souhaité) -->
        
        <v-divider vertical inset class="mx-1"></v-divider>
        <v-btn icon size="small" @click="editor.chain().focus().setHorizontalRule().run()">
          <IconMinus size="20" />
        </v-btn>
        -->
      </v-toolbar>

      <v-progress-linear
        indeterminate
        color="primary"
        v-if="isLoading || isSaving || isAIGenerating"
        class="mb-1"
        height="3"
      ></v-progress-linear>

      <v-row :class="{ 'fill-height': isDistractionFree }">
        <v-col cols="12" :md="isDistractionFree ? 12 : 9">
          <div class="editor-wrapper mb-4" :class="{ 'distraction-free-editor': isDistractionFree }">
            <editor-content :editor="editor" />
            <bubble-menu
              v-if="editor && !isDistractionFree"
              :editor="editor"
              :tippy-options="{ duration: 100, placement: 'top-start' }"
              plugin-key="textActions"
              class="bubble-menu-style"
            >
              <v-btn density="compact" variant="text" @click="triggerReformulate" :disabled="isAIGenerating" class="ma-1">
                Reformuler
              </v-btn>
              <v-btn density="compact" variant="text" @click="triggerShorten" :disabled="isAIGenerating" class="ma-1">
                Raccourcir
              </v-btn>
              <v-btn density="compact" variant="text" @click="triggerExpand" :disabled="isAIGenerating" class="ma-1">
                Développer
              </v-btn>
            </bubble-menu>
          </div>

          <ai-toolbar
            v-if="!isDistractionFree"
            ref="aiToolbarRef"
            @model-selected="handleModelSelection"
          ></ai-toolbar>

          <div v-if="suggestions && suggestions.length && !isDistractionFree" class="mt-4">
            <h2>Suggestions IA :</h2>
            <v-list density="compact">
              <v-list-item v-for="(suggestion, index) in suggestions" :key="index">
                <v-list-item-title style="white-space: pre-wrap;">{{ suggestion }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </div>

          <v-alert
            v-if="aiGenerationError"
            type="error"
            density="compact"
            variant="tonal"
            closable
            @update:model-value="aiGenerationError = null"
            class="mt-4"
          >
            {{ aiGenerationError }}
          </v-alert>

          <v-alert
            v-if="loadingError"
            type="warning"
            density="compact"
            variant="tonal"
            closable
            @update:model-value="clearLoadingError"
            class="mt-4"
          >
            Erreur chargement: {{ loadingError }}
          </v-alert>

        </v-col>
        <v-col cols="12" md="3" v-if="!isDistractionFree">
          <action-panel
            :loading="isAIGenerating"
            :current-action="currentAIAction"
            @suggest="triggerSuggest"
            @continue="triggerContinue"
            @dialogue="triggerDialogue"
            @cancel="cancelCurrentAction"
          />
        </v-col>
      </v-row>

       <v-btn
         v-if="isDistractionFree"
         icon
         color="grey-darken-1"
         position="fixed"
         location="top right"
         class="ma-4"
         @click="toggleDistractionFree"
         title="Quitter le mode sans distraction"
         elevation="4"
       >
         <!-- Utilisation directe de l'icône importée -->
         <IconMinimize size="22" />
       </v-btn>


      <v-snackbar
        v-model="showSnackbar"
        :timeout="snackbarTimeout"
        :color="snackbarColor"
        location="bottom right"
        multi-line
      >
        {{ snackbarMessage }}
        <template v-slot:actions>
          <v-btn
            variant="text"
            @click="showSnackbar = false"
          >
            Fermer
          </v-btn>
        </template>
      </v-snackbar>

    </v-container>
  </div>
</template>

<script setup>
import { ref, watch, toRef, computed, defineExpose, defineEmits, defineProps } from 'vue';
import { EditorContent, BubbleMenu } from '@tiptap/vue-3';
import AiToolbar from './ai-toolbar.vue';
import ActionPanel from './ActionPanel.vue';

// Import des composants Vuetify utilisés
import {
  VContainer, VChip, VSpacer, VTooltip, VBtn, VToolbar, VDivider, VProgressLinear,
  VRow, VCol, VList, VListItem, VListItemTitle, VAlert, VSnackbar
} from 'vuetify/components';

// Import des icônes Tabler nécessaires (importation nommée)
import {
  IconMinimize, IconMaximize, IconBold, IconItalic, // IconDeviceFloppy supprimée
  IconStrikethrough, IconTypography, IconH1, IconH2, IconMinus // Ajout IconMinus pour hr si besoin
} from '@tabler/icons-vue';
import EnregistrerIconURL from '@/assets/enregistrer.svg'; // Ajout de l'import pour l'icône SVG

// Import des composables
import { useTiptapEditor } from '@/composables/useTiptapEditor.js';
import { useChapterContent } from '@/composables/useChapterContent.js';
import { useSceneContent } from '@/composables/useSceneContent.js';
import { useAIActions } from '@/composables/useAIActions.js';
import { useSnackbar } from '@/composables/useSnackbar.js';

// --- Props ---
const props = defineProps({
  selectedChapterId: { type: [Number, null], default: null },
  selectedSceneId: { type: [Number, null], default: null },
  activeChapterTitle: { type: [String, null], default: null },
  activeSceneTitle: { type: [String, null], default: null },
  isDistractionFree: { type: Boolean, default: false }
});

// --- Emits ---
const emit = defineEmits(['toggle-distraction-free', 'ai-settings-changed']);

// --- Snackbar ---
const { showSnackbar, snackbarMessage, snackbarColor, snackbarTimeout, displaySnackbar } = useSnackbar(); // Ajout de displaySnackbar

// --- Composables ---
const { editor } = useTiptapEditor();
const {
  content: chapterContent,
  isLoading: isLoadingChapter,
  isSaving: isSavingChapter,
  loadingError: chapterLoadingError,
  savingError: chapterSavingError,
  hasUnsavedChanges: chapterHasUnsavedChanges,
  fetchChapterContent: loadChapterContent,
  // saveChapterContent, // Garder pour l'instant, mais ne pas utiliser directement pour la sauvegarde manuelle
  saveCurrentChapterIfNeeded, // CORRIGÉ: Déstructurer la bonne fonction
  applySuggestionToChapter,
  clearChapterLoadingError
} = useChapterContent(toRef(props, 'selectedChapterId'), editor); // Appel corrigé

const {
  content: sceneContent,
  isLoading: isLoadingScene,
  isSaving: isSavingScene,
  loadingError: sceneLoadingError,
  savingError: sceneSavingError,
  hasUnsavedChanges: sceneHasUnsavedChanges,
  loadSceneContent,
  // saveSceneContent, // Garder pour l'instant, mais ne pas utiliser directement pour la sauvegarde manuelle
  saveCurrentSceneIfNeeded, // CORRIGÉ: Déstructurer la bonne fonction
  applySuggestionToScene,
  clearSceneLoadingError
} = useSceneContent(toRef(props, 'selectedSceneId'), editor); // Appel corrigé

const aiToolbarRef = ref(null); // Référence pour le composant ai-toolbar (pourrait être utile pour autre chose)
const selectedAiParams = ref(null); // Référence pour stocker les paramètres IA sélectionnés

// Appel corrigé à useAIActions: passer la ref des paramètres IA
// relevantCharactersRef n'est pas géré ici, on passe null pour l'instant
const {
  suggestions,
  isGenerating: isAIGenerating,
  error: aiGenerationError,
  currentAction: currentAIAction,
  // Récupérer les fonctions spécifiques exportées par le composable
  triggerSuggest: triggerSuggestFromComposable,
  triggerContinue: triggerContinueFromComposable,
  triggerDialogue: triggerDialogueFromComposable,
  triggerReformulate: triggerReformulateFromComposable,
  triggerShorten: triggerShortenFromComposable,
  triggerExpand: triggerExpandFromComposable,
  cancelCurrentAction // Récupérer la fonction d'annulation
} = useAIActions(editor, selectedAiParams, ref(null)); // Passer editor, selectedAiParams, et ref(null) pour characters


// --- Computed Properties ---
const activeId = computed(() => props.selectedChapterId ?? props.selectedSceneId);
const activeType = computed(() => {
  if (props.selectedChapterId) return 'chapter';
  if (props.selectedSceneId) return 'scene';
  return null;
});
const activeTitle = computed(() => props.activeChapterTitle ?? props.activeSceneTitle);
const isLoading = computed(() => isLoadingChapter.value || isLoadingScene.value);
const isSaving = computed(() => isSavingChapter.value || isSavingScene.value);
const loadingError = computed(() => chapterLoadingError.value ?? sceneLoadingError.value);
const savingError = computed(() => chapterSavingError.value ?? sceneSavingError.value); // Non utilisé directement, mais disponible
const hasUnsavedChanges = computed(() => chapterHasUnsavedChanges.value || sceneHasUnsavedChanges.value);

// --- Watchers ---
watch(() => props.selectedChapterId, (newId, oldId) => {
  if (newId !== oldId && newId !== null) {
    console.log(`EditorComponent: Watching chapter change. New ID: ${newId}`);
    loadChapterContent(newId);
  } else if (newId === null && props.selectedSceneId === null) {
    editor.value?.commands.setContent('<p style="color: grey; text-align: center;">Sélectionnez un chapitre ou une scène pour commencer l\'édition.</p>'); // Message par défaut
  }
});

watch(() => props.selectedSceneId, (newId, oldId) => {
  if (newId !== oldId && newId !== null) {
    console.log(`EditorComponent: Watching scene change. New ID: ${newId}`);
    loadSceneContent(newId);
  } else if (newId === null && props.selectedChapterId === null) {
    editor.value?.commands.setContent('<p style="color: grey; text-align: center;">Sélectionnez un chapitre ou une scène pour commencer l\'édition.</p>'); // Message par défaut
  }
});

// --- Methods ---
// CORRIGÉ: Utiliser les fonctions ...IfNeeded et rendre async
const triggerManualSave = async () => {
  if (activeType.value === 'chapter' && props.selectedChapterId) {
    console.log(`EditorComponent: Triggering manual save for chapter ${props.selectedChapterId}`);
    const success = await saveCurrentChapterIfNeeded(true); // Appeler la bonne fonction avec forceSave=true
    if (success) {
      displaySnackbar('Chapitre enregistré.', 'success');
    } else {
      displaySnackbar('Erreur lors de la sauvegarde du chapitre.', 'error');
    }
  } else if (activeType.value === 'scene' && props.selectedSceneId) {
    console.log(`EditorComponent: Triggering manual save for scene ${props.selectedSceneId}`);
    const success = await saveCurrentSceneIfNeeded(true); // Appeler la bonne fonction avec forceSave=true
     if (success) {
      displaySnackbar('Scène enregistrée.', 'success');
    } else {
      displaySnackbar('Erreur lors de la sauvegarde de la scène.', 'error');
    }
  } else {
    console.warn("EditorComponent: Manual save triggered but no active chapter or scene ID found.");
    displaySnackbar('Aucun chapitre ou scène active à enregistrer.', 'warning');
  }
};

const clearLoadingError = () => {
  if (activeType.value === 'chapter') {
    clearChapterLoadingError();
  } else if (activeType.value === 'scene') {
    clearSceneLoadingError();
  }
};

const toggleDistractionFree = () => {
  emit('toggle-distraction-free');
};

// --- AI Actions ---
// La fonction getAIActionContext est supprimée car les paramètres IA sont maintenant
// passés directement au composable useAIActions via la ref selectedAiParams.



// Fonctions locales appelant les fonctions correspondantes du composable
const triggerReformulate = () => {
  if (!editor.value?.state.selection.empty) {
    triggerReformulateFromComposable(); // Appel de la fonction du composable
  } else {
    displaySnackbar("Veuillez sélectionner du texte à reformuler.", "warning");
  }
};

const triggerShorten = () => {
  if (!editor.value?.state.selection.empty) {
    triggerShortenFromComposable(); // Appel de la fonction du composable
  } else {
    displaySnackbar("Veuillez sélectionner du texte à raccourcir.", "warning");
  }
};

const triggerExpand = () => {
  if (!editor.value?.state.selection.empty) {
    triggerExpandFromComposable(); // Appel de la fonction du composable
  } else {
    displaySnackbar("Veuillez sélectionner du texte à développer.", "warning");
  }
};

const triggerSuggest = () => {
  triggerSuggestFromComposable(); // Appel de la fonction du composable
};

const triggerContinue = () => {
  triggerContinueFromComposable(); // Appel de la fonction du composable
};

const triggerDialogue = () => {
  triggerDialogueFromComposable(); // Appel de la fonction du composable
};

// La fonction cancelCurrentAction est fournie par useAIActions et peut être appelée directement
// depuis le template si nécessaire (ex: @cancel="cancelCurrentAction" dans ActionPanel)

// --- Insertion & Application ---
const insertContentAtCursor = (content) => {
  if (editor.value) {
    editor.value.chain().focus().insertContent(content).run();
  }
};

const applySuggestion = (suggestionData) => {
  if (activeType.value === 'chapter' && props.selectedChapterId) {
    applySuggestionToChapter(props.selectedChapterId, suggestionData);
  } else if (activeType.value === 'scene' && props.selectedSceneId) {
    applySuggestionToScene(props.selectedSceneId, suggestionData);
  }
};

// Met à jour la référence des paramètres IA lorsque la sélection change dans ai-toolbar
const handleModelSelection = (modelInfo) => {
  console.log('EditorComponent: handleModelSelection called with:', modelInfo);
  selectedAiParams.value = modelInfo; // Mettre à jour la référence réactive
emit('ai-settings-changed', modelInfo);
};


// --- Expose ---
// Exposer les méthodes nécessaires pour App.vue ou autres parents
defineExpose({
  triggerManualSave,
  insertContentAtCursor,
  applySuggestion
  // focusEditor: () => editor.value?.commands.focus() // Si besoin pour le mode sans distraction
});

</script>

<style lang="scss">
.editor-component-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-wrapper {
  border: 1px solid #ccc;
  border-radius: 4px; /* Ajusté pour correspondre aux defaults */
  background-color: #fff;
  min-height: 400px; /* Hauteur minimale pour l'éditeur */
  padding: 10px;
  position: relative; /* Pour le positionnement du bubble menu */
  flex-grow: 1; /* Permet à l'éditeur de grandir */
  overflow-y: auto; /* Ajoute une scrollbar si nécessaire */

  &.distraction-free-editor {
    border: none;
    border-radius: 0;
    min-height: 100%;
    height: 100%;
    width: 100%;
    padding: 20px 40px; /* Plus de padding en mode sans distraction */
    box-shadow: none;
  }

  .ProseMirror {
    outline: none;
    min-height: inherit; /* Hérite de la hauteur minimale du wrapper */
    height: 100%; /* Occupe toute la hauteur disponible */
    font-family: 'Lato', 'Roboto', sans-serif; // Police Lato prioritaire pour le contenu
    font-size: 1.1rem; /* Taille de police augmentée */
    color: #000000; /* Couleur de texte principale en noir pur */
    line-height: 1.6; /* Hauteur de ligne confortable par défaut */

    p {
      margin-bottom: 0.75em; /* Espace entre les paragraphes */
      line-height: 1.6; /* Hauteur de ligne confortable */
    }

    h1, h2 {
      font-family: 'Merriweather', serif; /* Appliquer la police de titre */
      margin-top: 1.5em;
      margin-bottom: 0.5em;
      line-height: 1.3;
    }
    h1 { font-size: 1.8em; } /* Maintenir la taille relative des titres */
    h2 { font-size: 1.4em; } /* Maintenir la taille relative des titres */

    a {
      color: rgb(var(--v-theme-primary));
      text-decoration: none;
      cursor: pointer;

      &:hover {
        text-decoration: underline;
      }
    }

    ul, ol {
      padding-left: 1.5em; // Indentation standard pour les listes
      margin-bottom: 0.75em;
      li {
        margin-bottom: 0.25em; // Espace entre les items de liste
        p { // Si les items de liste contiennent des paragraphes
          margin-bottom: 0.25em;
        }
      }
    }

    blockquote {
      border-left: 3px solid rgb(var(--v-theme-primary));
      margin-left: 0;
      margin-right: 0;
      padding-left: 1em;
      font-style: italic;
      color: rgba(0, 0, 0, 0.7); // Ajusté pour être basé sur le noir pur
      margin-bottom: 0.75em;

      p {
        margin-bottom: 0.25em; // Réduire l'espace si le dernier élément est un p
        &:last-child {
          margin-bottom: 0;
        }
      }
    }

    hr {
      border: none;
      border-top: 1px solid rgba(0, 0, 0, 0.12); // Style pour règle horizontale
      margin-top: 1.5em;
      margin-bottom: 1.5em;
    }

    &:focus {
      outline: none;
    }
  }
}

.editor-toolbar {
  border: 1px solid rgba(0, 0, 0, 0.12); // Bordure adoucie
  border-radius: var(--v-border-radius-lg, 8px); /* Utiliser variable Vuetify si possible, sinon fallback */
  padding: 4px;
  background-color: rgb(var(--v-theme-surface)); /* Utiliser couleur surface du thème */

  .v-btn {
    &.is-active {
      background-color: rgba(var(--v-theme-primary), 0.2);
      color: rgb(var(--v-theme-primary));
    }
  }
}

.bubble-menu-style {
  display: flex;
  background-color: rgb(var(--v-theme-surface)); /* Utiliser couleur surface */
  padding: 0.4rem; /* Augmentation du padding */
  border-radius: var(--v-border-radius-lg, 8px); /* Utiliser arrondi Vuetify */
  box-shadow: 0px 3px 5px -1px rgba(0,0,0,0.2), /* Élévation standard Vuetify */
              0px 6px 10px 0px rgba(0,0,0,0.14),
              0px 1px 18px 0px rgba(0,0,0,0.12);

  .v-btn {
    /* Les props density, size, class="ma-1" sont déjà dans le template */
    /* Le variant="text" est maintenant appliqué dans le template */
    border: none;
    text-transform: none; /* Assuré par les defaults maintenant */
    letter-spacing: normal; /* Assuré par les defaults maintenant */
    font-size: 0.9rem; /* Augmentation de la taille de police */
    /* Le hover est géré par Vuetify pour variant="text" */
  }
}

/* Ajustement pour le bouton flottant en mode sans distraction */
.v-btn--fixed {
  z-index: 1007; /* Assurer qu'il est au-dessus de l'éditeur */
}

</style>