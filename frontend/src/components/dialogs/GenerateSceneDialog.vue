<template>
  <v-dialog :model-value="show" @update:model-value="$emit('close')" persistent max-width="800px">
    <v-card class="scene-dialog-card-container">
      <div class="scene-dialog-background-image" :style="backgroundImageStyle"></div>
      
      <v-card-title class="scene-dialog-content-overlay">
        <span class="text-h5 font-weight-bold">Générer une Ébauche de Scène par IA</span>
      </v-card-title>
      
      <v-card-text class="scene-dialog-content-overlay">
        <v-container>
          <!-- Indicateur chargement modèles -->
          <v-progress-linear v-if="loadingModels" indeterminate color="secondary" class="mb-2"></v-progress-linear>
          <v-alert v-if="errorLoadingModels" type="error" density="compact" class="mb-2">
            Impossible de charger les modèles pour {{ providerInfo[selectedProvider]?.title || selectedProvider }}.
          </v-alert>

          <v-row>
            <!-- Sélecteurs Provider/Modèle/Style -->
            <v-col cols="12" sm="4">
              <v-select
                v-model="selectedProvider"
                :items="providers"
                label="Fournisseur d'IA"
                item-title="title"
                item-value="value"
                :disabled="loadingModels || isGenerating"
                density="compact"
                hide-details
                @update:model-value="handleProviderChange"
              ></v-select>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-if="currentAvailableModels.length > 5"
                v-model="modelSearch"
                label="Rechercher modèle..."
                density="compact"
                variant="outlined"
                clearable
                hide-details
                class="mb-2"
              ></v-text-field>
              <v-select
                v-model="selectedModel"
                :items="filteredModels"
                label="Modèle"
                item-title="formattedName"
                item-value="id"
                :disabled="loadingModels || isGenerating || !selectedProvider || currentAvailableModels.length === 0"
                :no-data-text="loadingModels ? 'Chargement...' : 'Aucun modèle disponible'"
                density="compact"
                hide-details
              ></v-select>
            </v-col>
            <v-col cols="12" sm="4">
              <v-select
                v-model="selectedStyle"
                :items="writingStyles"
                label="Style d'écriture"
                item-title="text"
                item-value="value"
                :disabled="loadingModels || isGenerating"
                density="compact"
                hide-details
              ></v-select>
            </v-col>

            <!-- Champ pour les indications utilisateur (description générale) -->
            <v-col cols="12">
              <v-textarea
                v-model="promptDetails"
                label="Description générale de la scène (optionnel)"
                placeholder="Ex: Nuit pluvieuse en ville, un personnage attend sous un porche, ambiance tendue..."
                rows="2"
                auto-grow
                clearable
                :disabled="isGenerating"
              ></v-textarea>
            </v-col>

            <!-- NOUVEAU: Champs pour enrichir la génération -->
            <v-col cols="12" md="6">
                <v-text-field
                    v-model="sceneGoal"
                    label="Objectif principal de la scène (optionnel)"
                    placeholder="Ex: Introduire le personnage de l'inspecteur"
                    clearable
                    :disabled="isGenerating"
                    density="compact"
                ></v-text-field>
            </v-col>
             <v-col cols="12" md="6">
                <v-autocomplete
                    v-model="selectedCharacters"
                    :items="projectCharacters"
                    item-title="name"
                    item-value="name"  
                    label="Personnages présents (optionnel)"
                    multiple
                    chips
                    closable-chips
                    clearable
                    :disabled="isGenerating || projectCharacters.length === 0"
                    no-data-text="Aucun personnage défini"
                    density="compact"
                ></v-autocomplete>
            </v-col>
            <v-col cols="12">
                <v-textarea
                    v-model="keyElements"
                    label="Éléments ou détails clés à inclure (optionnel)"
                    placeholder="Ex: Le chat noir traverse la rue, mentionner la lettre froissée..."
                    rows="2"
                    auto-grow
                    clearable
                    :disabled="isGenerating"
                ></v-textarea>
            </v-col>
            <!-- FIN NOUVEAU -->


            <!-- Choix de l'action après génération -->
            <v-col cols="12">
                <v-radio-group v-model="generationAction" inline label="Action après génération :" density="compact" hide-details :disabled="isGenerating">
                    <v-radio label="Afficher l'ébauche" value="display"></v-radio>
                    <v-radio label="Insérer dans l'éditeur" value="insert"></v-radio>
                </v-radio-group>
            </v-col>

            <!-- Zone pour afficher le résultat -->
            <v-col cols="12" v-if="generatedText || generationError || isGenerating">
              <v-divider class="my-3"></v-divider>
              <v-progress-linear v-if="isGenerating" indeterminate color="primary" class="mb-3"></v-progress-linear>
              <v-alert v-if="generationError && !isGenerating" type="error" density="compact" class="mb-3">
                {{ generationError }}
              </v-alert>
              <div v-if="generatedText && !isGenerating && generationAction === 'display'"> <!-- Condition pour afficher -->
                <h3 class="mb-2">Ébauche Générée :</h3>
                <v-card variant="outlined" class="pa-3">
                  <p style="white-space: pre-wrap;">{{ generatedText }}</p>
                </v-card>
                <v-btn
                  variant="tonal"
                  size="small"
                  @click="copyGeneratedText"
                  title="Copier le texte de l'ébauche"
                  class="mt-2"
                >
                  <template v-slot:prepend>
                    <IconCopy size="18" />
                  </template>
                  Copier
                </v-btn>
              </div>
               <v-alert v-if="generatedText && !isGenerating && generationAction === 'insert'" type="success" density="compact" class="mb-3">
                 Contenu généré et prêt à être inséré.
               </v-alert>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      
      <v-card-actions class="scene-dialog-content-overlay pa-4">
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="$emit('close')" :disabled="isGenerating">
          Fermer
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          class="text-white"
          @click="submitGeneration"
          :loading="isGenerating"
          :disabled="isGenerating || loadingModels || !selectedProvider || !selectedModel"
        >
          <template v-slot:prepend>
            <IconSparkles size="20" />
          </template>
          Générer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';
import { IconCopy, IconSparkles } from '@tabler/icons-vue';
import SceneBackgroundURL from '@/assets/scene2.svg'; 
import { VDialog, VCard, VCardTitle, VCardText, VCardActions, VContainer, VRow, VCol, VProgressLinear, VAlert, VSelect, VTextField, VTextarea, VDivider, VBtn, VSpacer, VRadioGroup, VRadio, VAutocomplete, VChip } from 'vuetify/components';


const props = defineProps({
  show: Boolean,
  providers: { type: Array, default: () => [] },
  availableModels: { type: Object, default: () => ({}) },
  writingStyles: { type: Array, default: () => [] },
  providerInfo: { type: Object, default: () => ({}) },
  loadingModels: Boolean,
  errorLoadingModels: Boolean,
  projectCharacters: { type: Array, default: () => [] },
  fetchModels: { type: Function, required: true },
  selectDefaultModel: { type: Function, required: true },
  showSnackbar: { type: Function, required: true },
});

const emit = defineEmits(['close', 'insert-content']);

const selectedProvider = ref(config.defaultProvider);
const selectedModel = ref(null);
const selectedStyle = ref('normal');
const modelSearch = ref('');
const promptDetails = ref('');
const isGenerating = ref(false);
const generationError = ref(null);
const generatedText = ref(null);
const generationAction = ref('display');
const sceneGoal = ref('');
const selectedCharacters = ref([]);
const keyElements = ref('');

const backgroundImageStyle = computed(() => ({
  backgroundImage: `url(${SceneBackgroundURL})`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'center center',
  backgroundSize: 'contain',
  opacity: 0.05, // Opacité réduite pour effet filigrane
  position: 'absolute',
  top: '0',
  left: '0',
  right: '0',
  bottom: '0',
  zIndex: 0 // Derrière le contenu qui sera à zIndex 1
}));

const currentAvailableModels = computed(() => props.availableModels[selectedProvider.value] || []);

const filteredModels = computed(() => {
  if (!modelSearch.value) {
    return currentAvailableModels.value;
  }
  const searchTerm = modelSearch.value.toLowerCase();
  return currentAvailableModels.value.filter(model =>
    model.formattedName?.toLowerCase().includes(searchTerm) ||
    model.description?.toLowerCase().includes(searchTerm) ||
    model.id?.toLowerCase().includes(searchTerm)
  );
});

watch(() => props.show, async (newValue) => {
  if (newValue) {
    promptDetails.value = '';
    generationError.value = null;
    generatedText.value = null;
    modelSearch.value = '';
    sceneGoal.value = '';
    selectedCharacters.value = [];
    keyElements.value = '';

    if (!selectedProvider.value) {
      selectedProvider.value = config.defaultProvider;
    }
    if (selectedProvider.value && (!props.availableModels[selectedProvider.value] || props.availableModels[selectedProvider.value].length === 0 || props.errorLoadingModels)) {
      const success = await props.fetchModels(selectedProvider.value);
      if (success) {
        selectedModel.value = props.selectDefaultModel(selectedProvider.value);
      }
    } else if (selectedProvider.value && !selectedModel.value) {
      selectedModel.value = props.selectDefaultModel(selectedProvider.value);
    }
  }
});

watch(selectedProvider, async (newProvider, oldProvider) => {
  if (newProvider && newProvider !== oldProvider) {
    modelSearch.value = '';
    selectedModel.value = null; 
    generatedText.value = null; 
    generationError.value = null;

    const success = await props.fetchModels(newProvider);
    if (success) {
      selectedModel.value = props.selectDefaultModel(newProvider);
    }
  }
});

const handleProviderChange = () => {};

async function submitGeneration() {
  if (!selectedProvider.value || !selectedModel.value) {
    props.showSnackbar("Veuillez sélectionner un fournisseur et un modèle d'IA.", "warning");
    return;
  }

  isGenerating.value = true;
  generationError.value = null;
  generatedText.value = null;

  let fullPrompt = `Génère une ébauche de scène.`;
  if (promptDetails.value) fullPrompt += `\nDescription générale de la scène: ${promptDetails.value}`;
  if (sceneGoal.value) fullPrompt += `\nObjectif principal de la scène: ${sceneGoal.value}`;
  if (selectedCharacters.value.length > 0) {
    const charactersForContext = props.projectCharacters.filter(pc => selectedCharacters.value.includes(pc.name))
                                   .map(pc => ({ name: pc.name, description: pc.description, backstory: pc.backstory }));
    if (charactersForContext.length > 0) {
        fullPrompt += `\nPersonnages présents (avec leurs détails pour contexte): ${JSON.stringify(charactersForContext)}`;
    } else {
        fullPrompt += `\nPersonnages présents: ${selectedCharacters.value.join(', ')}`;
    }
  }
  if (keyElements.value) fullPrompt += `\nÉléments clés à inclure: ${keyElements.value}`;

  try {
    const response = await fetch(`${config.apiUrl}/generate/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
      body: JSON.stringify({
        provider: selectedProvider.value,
        model: selectedModel.value,
        prompt: fullPrompt,
        action: 'generer_scene',
        style: selectedStyle.value,
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Erreur inconnue.' }));
      throw new Error(errorData.detail || `Erreur HTTP ${response.status}`);
    }

    const data = await response.json();
    if (data && data.generated_text) {
      generatedText.value = data.generated_text;
      if (generationAction.value === 'insert') {
        emit('insert-content', data.generated_text);
        props.showSnackbar("Ébauche de scène générée et prête à être insérée.", "success");
      } else {
         props.showSnackbar("Ébauche de scène générée.", "success");
      }
    } else {
      throw new Error("Réponse API invalide.");
    }
  } catch (error) {
    generationError.value = handleApiError(error, "génération de scène");
  } finally {
    isGenerating.value = false;
  }
}

function copyGeneratedText() {
  if (generatedText.value) {
    navigator.clipboard.writeText(generatedText.value)
      .then(() => props.showSnackbar("Texte copié!", "info"))
      .catch(err => props.showSnackbar("Erreur de copie.", "error"));
  }
}
</script>

<style scoped>
.scene-dialog-card-container {
  position: relative; /* Contexte d'empilement pour le div de fond et le contenu */
  background-color: rgb(var(--v-theme-surface)); /* Couleur de fond principale de la carte */
  overflow: hidden; /* Pour s'assurer que le div de fond ne dépasse pas si erreur de positionnement */
}

/* Le .scene-dialog-background-image est stylé en inline via :style="backgroundImageStyle" */
/* On peut ajouter ici des styles qui ne dépendent pas de JS si nécessaire, mais position et dimensions sont dans backgroundImageStyle */
.scene-dialog-background-image {
  /* Styles principaux (backgroundImage, opacity, etc.) sont dans la propriété calculée backgroundImageStyle */
  /* position, top, left, right, bottom, zIndex sont aussi dans backgroundImageStyle */
}


.scene-dialog-content-overlay {
  position: relative; /* Pour être positionné par rapport au flux normal, mais au-dessus du fond */
  z-index: 1; /* Assure que le contenu est au-dessus de l'image de fond (qui est à z-index: 0) */
  background-color: transparent; /* Important pour que l'image de fond soit visible à travers */
}

/* Assurer que le container dans v-card-text est aussi transparent */
.scene-dialog-content-overlay > .v-container {
    background-color: transparent;
}


.v-card-title.scene-dialog-content-overlay {
  /* background-color: rgb(var(--v-theme-primary)); -- Ceci sera masqué par transparent, mais on garde la structure */
  /* color: white; */ /* La couleur du texte est héritée ou définie par Vuetify */
  padding: 12px 24px;
  /* Le fond de la barre de titre doit être géré avec soin pour la lisibilité sur l'image */
  /* Peut-être un fond semi-transparent pour le titre lui-même si nécessaire plus tard */
}
.v-card-actions.scene-dialog-content-overlay {
  /* background-color: #f5f5f5; -- Ceci sera masqué par transparent */
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity)); /* Utiliser les variables Vuetify pour la bordure */
}

/* Améliorer la lisibilité des labels de radio */
.v-radio-group :deep(.v-label) {
  opacity: 1 !important; 
  color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity));
}
</style>