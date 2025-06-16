<template>
  <div class="editor-component-wrapper">
    <v-container :fluid="isDistractionFree" :class="{ 'pa-0': isDistractionFree }">
      <div class="mb-2 d-flex align-center" v-if="!isDistractionFree">
        <v-chip v-if="localChapterId" color="blue" label size="small">
          Chapitre Actif
        </v-chip>
        <v-chip v-else color="grey" label size="small">
          Aucun contenu sélectionné
        </v-chip>

        <span v-if="localTitle" class="ml-2 font-weight-bold text-subtitle-1">{{ localTitle }}</span>
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
              :disabled="isSaving || !localChapterId"
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

      <!-- Indicateur de chargement chapitre / sauvegarde -->
      <v-progress-linear
        indeterminate
        color="primary"
        v-if="isLoading || isSaving" 
        class="mb-1"
        height="3"
      ></v-progress-linear>

      <v-row :class="{ 'fill-height': isDistractionFree }" style="position: relative;">
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

          <!-- Overlay pour le chargement IA -->
          <v-overlay
            :model-value="isAIGenerating"
            class="align-center justify-center"
            persistent
            contained 
            scrim="#E0E0E0" 
          >
            <v-progress-circular
              color="primary"
              indeterminate
              size="64"
            ></v-progress-circular>
            <div class="text-primary mt-2">Traitement IA en cours...</div>
          </v-overlay>

          <chapter-summary 
            :summary="localSummary" 
            class="mb-4"
            @refresh-summary="handleRefreshSummary"
          />

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
            @update:model-value="loadingError = null"
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
        v-model="isSnackbarVisible"
        :color="snackbarColor"
        :timeout="snackbarTimeout"
        location="bottom right"
        variant="tonal"
      >
        {{ snackbarMessage }}
        <template v-slot:actions>
          <v-btn icon @click="isSnackbarVisible = false">
            <IconX />
          </v-btn>
        </template>
      </v-snackbar>
    </v-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { EditorContent, BubbleMenu } from '@tiptap/vue-3';
import { useTiptapEditor } from '@/composables/useTiptapEditor.js';
import { useAIActions } from '@/composables/useAIActions.js';
import { useChapterContent } from '@/composables/useChapterContent.js';
import { useSnackbar } from '@/composables/useSnackbar.js';

import ActionPanel from './ActionPanel.vue';
import AiToolbar from './ai-toolbar.vue';
import ChapterSummary from './ChapterSummary.vue';

import {
  IconBold, IconItalic, IconStrikethrough, IconTypography, IconH1, IconH2, IconMinus,
  IconMaximize, IconMinimize, IconX
} from '@tabler/icons-vue';
import EnregistrerIconURL from '@/assets/enregistrer.svg';

// --- Composables ---
const { 
  displaySnackbar, 
  showSnackbar: isSnackbarVisible, 
  snackbarMessage, 
  snackbarColor, 
  snackbarTimeout 
} = useSnackbar();

const { editor, initializeEditor, destroyEditor, applySuggestion } = useTiptapEditor();

const { 
  isLoading, isSaving, loadingError, savingError, 
  fetchChapterContent, saveChapterContent 
} = useChapterContent();

// --- Local State ---
const localChapterId = ref(null);
const localTitle = ref('');
const localSummary = ref(null);
const localProjectId = ref(null);
const lastSavedContent = ref('');

const isDistractionFree = ref(false);
const aiToolbarRef = ref(null);

// State for AI Actions
const selectedAiParams = ref({
  provider: null,
  model: null,
  style: 'standard',
  customStyleDescription: null
});

const {
  isAIGenerating,
  aiGenerationError,
  currentAIAction,
  suggestions,
  triggerAIAction, // Renamed for clarity
  cancelCurrentAction,
} = useAIActions(editor, selectedAiParams, ref(null)); // Pass correct refs

// --- Computed Properties ---
const hasUnsavedChanges = computed(() => {
  if (!editor.value || !localChapterId.value) {
    return false;
  }
  const currentContent = editor.value.getHTML();
  return currentContent !== lastSavedContent.value;
});

// --- AI Action Triggers ---
// Wrapper functions to call triggerAIAction with the correct action name
const triggerContinue = () => triggerAIAction('continue');
const triggerSuggest = () => triggerAIAction('suggest');
const triggerDialogue = () => triggerAIAction('dialogue');
const triggerReformulate = () => triggerAIAction('reformulate');
const triggerShorten = () => triggerAIAction('shorten');
const triggerExpand = () => triggerAIAction('expand');


// --- Core Logic Methods ---

async function loadChapter(chapterId) {
  if (!editor.value) return;

  if (chapterId === null) {
    editor.value.commands.setContent('<p style="color: grey; text-align: center;">Sélectionnez un chapitre pour commencer l\'édition.</p>');
    lastSavedContent.value = '';
    localChapterId.value = null;
    localTitle.value = '';
    localSummary.value = null;
    localProjectId.value = null;
    return;
  }

  editor.value.setEditable(false);
  editor.value.commands.setContent(`<p>Chargement du chapitre ${chapterId}...</p>`);

  const chapterData = await fetchChapterContent(chapterId);

  if (chapterData) {
    const contentToLoad = chapterData.content || '<p>Ce chapitre est vide.</p>';
    editor.value.commands.setContent(contentToLoad);
    lastSavedContent.value = contentToLoad;
    localChapterId.value = chapterData.id;
    localTitle.value = chapterData.title;
    localSummary.value = chapterData.summary;
    localProjectId.value = chapterData.project_id;
  } else {
    editor.value.commands.setContent(`<p>Erreur lors du chargement du chapitre ${chapterId}.</p>`);
    lastSavedContent.value = '';
    localChapterId.value = chapterId; // Keep id to show error context
    localTitle.value = 'Erreur';
    localSummary.value = null;
    localProjectId.value = null;
  }
  editor.value.setEditable(true);
  editor.value.commands.focus();
}

async function saveChapter(isManualSave = false) {
  if (!localChapterId.value || !editor.value || isSaving.value) {
    return false;
  }

  const currentContent = editor.value.getHTML();
  
  // Sauvegarde seulement si c'est manuel ou s'il y a des changements
  if (!isManualSave && !hasUnsavedChanges.value) {
      return true;
  }

  const chapterData = {
    title: localTitle.value,
    content: currentContent,
    summary: localSummary.value,
    project_id: localProjectId.value
  };

  const success = await saveChapterContent(localChapterId.value, chapterData);

  if (success) {
    lastSavedContent.value = currentContent;
    if (isManualSave) {
      displaySnackbar('Chapitre enregistré avec succès.', 'success');
    }
    return true;
  } else {
    displaySnackbar(`Erreur lors de la sauvegarde: ${savingError.value}`, 'error');
    return false;
  }
}

// --- Event Handlers ---

function toggleDistractionFree() {
  isDistractionFree.value = !isDistractionFree.value;
}

async function triggerManualSave() {
  await saveChapter(true);
}

const emit = defineEmits(['toggle-distraction-free', 'ai-settings-changed']);

function handleModelSelection(settings) {
  selectedAiParams.value = { ...selectedAiParams.value, ...settings };
  emit('ai-settings-changed', selectedAiParams.value);
  displaySnackbar(`Modèle IA sélectionné: ${settings.provider} - ${settings.model}`, 'info');
}

async function handleRefreshSummary() {
    if (!localChapterId.value) return;
    // Pour l'instant, on recharge simplement les données du chapitre.
    // Une future version pourrait appeler un endpoint de régénération.
    await loadChapter(localChapterId.value);
    displaySnackbar('Résumé rafraîchi.', 'info');
}

// --- Lifecycle & Exposed Methods ---

onMounted(() => {
  initializeEditor();
});

onBeforeUnmount(() => {
  destroyEditor();
});

defineExpose({
  loadChapter,
  saveChapter,
  applySuggestion
});

</script>

<style lang="scss">
.editor-component-wrapper {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;

  .v-container {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .v-row {
    flex: 1;
  }
}

.editor-wrapper {
  border: 1px solid #dcdcdc;
  border-radius: 4px;
  padding: 1rem;
  background-color: #fff;
  min-height: 400px;
  position: relative;

  .ProseMirror {
    min-height: 350px;
    outline: none;
  }
}

.distraction-free-editor {
  border: none;
  padding: 2rem;
  margin: 0 auto;
  max-width: 800px;
  background-color: #fdfdfd;
  min-height: 100vh;
}

.editor-toolbar {
  border: 1px solid #dcdcdc;
  border-radius: 4px;
  .v-btn {
    &.is-active {
      background-color: rgba(var(--v-theme-primary), 0.1);
      color: rgb(var(--v-theme-primary));
    }
  }
}

.bubble-menu-style {
  display: flex;
  background-color: #2c3e50;
  padding: 0.2rem;
  border-radius: 0.5rem;
  color: white;

  .v-btn {
    color: white;
  }
}
</style>