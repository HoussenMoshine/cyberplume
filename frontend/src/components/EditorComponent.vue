<template>
  <div class="editor-component-wrapper">
    <v-container :fluid="isDistractionFree" :class="{ 'pa-0': isDistractionFree }">
      <div class="mb-2 d-flex align-center" v-if="!isDistractionFree">
        <v-chip v-if="activeType === 'chapter'" color="blue" label size="small">
          Chapitre Actif
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
        
        <v-divider vertical inset class="mx-1"></v-divider>
        <v-btn icon size="small" @click="editor.chain().focus().setHorizontalRule().run()">
          <IconMinus size="20" />
        </v-btn>
        
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
              plugin-key="textActionsBubbleMenu"
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
import { ref, onMounted, onBeforeUnmount, watch, computed, toRef, nextTick } from 'vue';
import { Editor, EditorContent, BubbleMenu } from '@tiptap/vue-3';
// Les imports d'extensions spécifiques sont gérés par useTiptapEditor

import {
  VContainer, VRow, VCol, VChip, VSpacer, VBtn, VToolbar, VProgressLinear, VAlert, VList, VListItem, VListItemTitle, VSnackbar, VTooltip, VDivider
} from 'vuetify/components';

import {
  IconBold, IconItalic, IconStrikethrough, IconTypography, IconH1, IconH2, IconMinus,
  IconMaximize, IconMinimize
} from '@tabler/icons-vue';

import EnregistrerIconURL from '@/assets/enregistrer.svg';
import ActionPanel from './ActionPanel.vue';
import AiToolbar from './ai-toolbar.vue'; 

import { useChapterContent } from '@/composables/useChapterContent.js';
import { useAIActions } from '@/composables/useAIActions.js';
import { useSnackbar as useSnackbarComposable } from '@/composables/useSnackbar.js'; 
import { useTiptapEditor } from '@/composables/useTiptapEditor.js';


const props = defineProps({
  selectedChapterId: { type: [Number, null], default: null },
  activeChapterTitle: { type: [String, null], default: null },
  isDistractionFree: { type: Boolean, default: false }
});

const emit = defineEmits([
  'update:isDistractionFree',
  'content-changed',
  'ai-action-insert-content',
  'ai-action-replace-content',
  'ai-action-error',
  'manual-save-requested' 
]);

const { showSnackbar, snackbarMessage, snackbarColor, snackbarTimeout, displaySnackbar } = useSnackbarComposable();

const aiToolbarRef = ref(null); 
const currentAiParamsFromToolbar = ref({
  provider: '', // Valeur initiale - A REVOIR: anciennement config.defaultProvider
  model: null,
  style: 'normal', // Style par défaut
  customStyleDescription: null
});

const handleModelSelection = (data) => {
  console.log("Paramètres IA reçus de ai-toolbar:", data);
  currentAiParamsFromToolbar.value = {
    provider: data.provider,
    model: data.model,
    style: data.style,
    customStyleDescription: data.customStyleDescription
  };
};

// Placeholder pour relevantCharactersRef, à gérer ultérieurement
const relevantCharactersForAI = ref(null);


// --- Editor Setup ---
// La ref 'editor' sera maintenant fournie par useTiptapEditor
const { 
  editor, // Récupérer la ref de l'éditeur ici
  initializeEditor: initTiptap, 
  destroyEditor 
} = useTiptapEditor(
  undefined, // Utilise le initialContent par défaut de useTiptapEditor
  (blurredEditorInstance) => { 
    if (activeType.value === 'chapter' && editor.value) { // Assurer que editor.value existe
      saveCurrentChapterIfNeeded(); // saveCurrentChapterIfNeeded est défini plus bas, mais a besoin de 'editor'
    }
  },
  'Commencez à écrire votre chapitre ici...' 
);

const {
  content: chapterContent,
  isLoading: isLoadingChapter,
  isSaving: isSavingChapter,
  loadingError: chapterLoadingError,
  savingError: chapterSavingError, 
  hasUnsavedChanges: chapterHasUnsavedChanges,
  loadChapterContent,
  saveCurrentChapterIfNeeded, // Cette fonction utilise 'editor' qui est maintenant correctement initialisé
  applySuggestionToChapter,
  clearChapterLoadingError
} = useChapterContent(toRef(props, 'selectedChapterId'), editor);


const {
  isAIGenerating,
  currentAIAction,
  aiGenerationError,
  suggestions,
  // generateAIResponse, insertGeneratedContent, replaceSelectedContent sont gérés en interne par useAIActions
  cancelCurrentAction, // Assurons-nous que les autres fonctions nécessaires sont bien là
  triggerSuggest,    // Explicitement déstructurer pour clarté, même si appelées directement plus bas
  triggerContinue,
  triggerDialogue,
  triggerReformulate,
  triggerShorten,
  triggerExpand
} = useAIActions(editor, currentAiParamsFromToolbar, relevantCharactersForAI);


// --- Computed Properties ---
const activeId = computed(() => props.selectedChapterId);
const activeType = computed(() => {
  if (props.selectedChapterId) return 'chapter';
  return null;
});
const activeTitle = computed(() => props.activeChapterTitle);
const isLoading = computed(() => isLoadingChapter.value);
const isSaving = computed(() => isSavingChapter.value);
const loadingError = computed(() => chapterLoadingError.value);
const savingError = computed(() => chapterSavingError.value); 
const hasUnsavedChanges = computed(() => chapterHasUnsavedChanges.value);


onMounted(() => {
  initTiptap({ 
    onUpdate: () => {
      if (activeType.value === 'chapter') {
        chapterHasUnsavedChanges.value = true;
      }
      emit('content-changed', editor.value?.getHTML());
    }
  });

  if (props.selectedChapterId && editor.value) {
    loadChapterContent(props.selectedChapterId);
  } else if (editor.value && props.selectedChapterId === null) {
    editor.value.commands.setContent('<p style="color: grey; text-align: center;">Sélectionnez un chapitre pour commencer l\'édition.</p>');
  }
});

onBeforeUnmount(() => {
  destroyEditor();
});


// --- Watchers ---
watch(() => props.selectedChapterId, (newId, oldId) => {
  // Ne charger que si l'ID change réellement et n'est pas l'appel initial (oldId !== undefined)
  if (newId !== oldId && oldId !== undefined) { 
    if (newId !== null) {
      loadChapterContent(newId);
    } else if (editor.value) {
      editor.value.commands.setContent('<p style="color: grey; text-align: center;">Sélectionnez un chapitre pour commencer l\'édition.</p>');
    }
  } else if (newId !== null && oldId === undefined && editor.value && !editor.value.getText()) {
    // Cas spécifique du premier chargement si onMounted n'a pas pu charger car selectedChapterId était null initialement
    loadChapterContent(newId);
  }
}, { immediate: false }); // immediate: false pour éviter le double chargement avec onMounted


// --- Methods ---
const triggerManualSave = async () => {
  if (!activeId.value) {
    displaySnackbar('Aucun contenu actif à enregistrer.', 'warning');
    return;
  }
  let success = false;
  if (activeType.value === 'chapter' && props.selectedChapterId) {
    success = await saveCurrentChapterIfNeeded(true); 
     if (success) {
      displaySnackbar('Chapitre enregistré.', 'success');
    } else {
      displaySnackbar(`Erreur lors de l'enregistrement du chapitre. ${savingError.value || ''}`, 'error');
    }
  } else {
    displaySnackbar('Aucun chapitre actif à enregistrer.', 'warning');
  }
  emit('manual-save-requested', { type: activeType.value, id: activeId.value, success });
};

const clearLoadingError = () => {
  if (activeType.value === 'chapter') {
    clearChapterLoadingError();
  }
};

const toggleDistractionFree = () => {
  emit('update:isDistractionFree', !props.isDistractionFree);
};


// --- AI Actions ---
// Les fonctions getSelectedText et handleAIAction sont supprimées.
// La logique est maintenant dans useAIActions.js et les fonctions trigger<ActionName>
// déstructurées (triggerSuggest, triggerContinue, etc.) sont appelées directement.

// Les définitions locales de triggerReformulate, triggerShorten, etc. sont supprimées.
// Nous utilisons maintenant directement celles déstructurées depuis useAIActions,
// qui ont été modifiées pour accepter customPrompt.
// Par exemple, l'appel @click="triggerReformulate" dans le template
// utilisera la fonction triggerReformulate de useAIActions.


// La fonction handleModelSelection est maintenant définie plus haut pour mettre à jour currentAiParamsFromToolbar
// et est utilisée par le template pour l'événement @model-selected de ai-toolbar.
// La définition précédente ici est donc supprimée.

const handleApplySuggestionToEditor = (suggestionData) => {
  if (activeType.value === 'chapter' && props.selectedChapterId) {
    applySuggestionToChapter(props.selectedChapterId, suggestionData);
  }
};

defineExpose({ editor, triggerManualSave, handleApplySuggestionToEditor });

</script>

<style lang="scss">
.editor-component-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%; 
}

.v-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.editor-wrapper {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
  background-color: #fff;
  min-height: 300px; 
  flex-grow: 1; 
  overflow-y: auto; 

  .ProseMirror {
    min-height: 280px; 
    outline: none;
    &:focus {
      border-color: var(--v-theme-primary);
    }
    p.is-editor-empty:first-child::before {
      content: attr(data-placeholder);
      float: left;
      color: #adb5bd;
      pointer-events: none;
      height: 0;
    }
  }
}

.distraction-free-editor {
  border: none;
  padding: 20px; 
  min-height: calc(100vh - 40px); 
  font-size: 1.1rem; 
  line-height: 1.7;   
  background-color: #fdfdfd; 
}

.editor-toolbar {
  background-color: #f5f5f5; 
  border-radius: 4px;
  padding: 4px;
  .v-btn.is-active {
    background-color: rgba(var(--v-theme-primary), 0.2);
  }
}

.bubble-menu-style {
  display: flex;
  background-color: #333;
  padding: 0.2rem 0.4rem;
  border-radius: 0.5rem;
  box-shadow: 0px 0px 3px rgba(0, 0, 0, 0.5), 0px 0px 10px rgba(0, 0, 0, 0.1);

  .v-btn {
    color: white !important;
    text-transform: none; 
    font-size: 0.8rem;
    padding: 0.1rem 0.3rem; 
    min-width: auto; 
  }
}

.v-row.fill-height {
  height: 100%;
  .v-col {
    display: flex;
    flex-direction: column;
  }
}

.v-row.fill-height .v-col .editor-wrapper {
   height: 100%;
}

</style>