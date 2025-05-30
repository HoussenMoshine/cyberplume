<template>
  <v-dialog :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)" persistent max-width="800px">
    <v-card>
      <div :style="dialogBackgroundImageStyle"></div>
      <div class="dialog-content-overlay">
        <v-card-title>
          <span class="text-h5"><IconBulb class="mr-2" />Générer des Idées de Scènes</span>
        </v-card-title>
        <v-card-text>
          <v-container>
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
                  v-if="availableModels[selectedProvider]?.length > 5"
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
                  :disabled="loadingModels || isGenerating || !selectedProvider || availableModels[selectedProvider]?.length === 0"
                  :no-data-text="loadingModels ? 'Chargement...' : 'Aucun modèle disponible'"
                  density="compact"
                  hide-details
                ></v-select>
              </v-col>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="selectedStyle"
                  :items="writingStyles"
                  label="Style d'écriture souhaité"
                  item-title="text"
                  item-value="value"
                  :disabled="loadingModels || isGenerating"
                  density="compact"
                  hide-details
                ></v-select>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>

            <h3 class="text-subtitle-1 mb-3">Détails pour la génération :</h3>
            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="generationParams.projectContext"
                  label="Contexte du projet / Histoire globale"
                  placeholder="Ex: Roman de fantasy se déroulant dans un royaume assiégé..."
                  rows="2"
                  auto-grow
                  clearable
                  :disabled="isGenerating"
                  density="compact"
                ></v-textarea>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="generationParams.sceneType"
                  :items="['Action', 'Dialogue', 'Introspection', 'Description', 'Exposition', 'Mystère', 'Conflit', 'Résolution', 'Transition', 'Autre']"
                  label="Type de scène (optionnel)"
                  density="compact"
                  clearable
                  :disabled="isGenerating"
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="generationParams.involvedCharacters"
                  label="Personnages principaux impliqués (optionnel)"
                  placeholder="Ex: Arthur, Merlin"
                  density="compact"
                  clearable
                  :disabled="isGenerating"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="generationParams.mood"
                  label="Ambiance / Émotion dominante (optionnel)"
                  placeholder="Ex: Sombre, Joyeuse, Tendue"
                  density="compact"
                  clearable
                  :disabled="isGenerating"
                ></v-text-field>
              </v-col>
               <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="generationParams.numberOfIdeas"
                  label="Nombre d'idées à générer"
                  type="number"
                  :min="1"
                  :max="5"
                  density="compact"
                  :disabled="isGenerating"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="generationParams.keyElements"
                  label="Éléments clés ou contraintes à inclure (optionnel)"
                  placeholder="Ex: Doit contenir une révélation, se passer la nuit..."
                  rows="2"
                  auto-grow
                  clearable
                  :disabled="isGenerating"
                  density="compact"
                ></v-textarea>
              </v-col>
            </v-row>

            <!-- Zone pour afficher le résultat -->
            <v-col cols="12" v-if="generatedIdeas.length > 0 || generationError || isGenerating" class="mt-4">
              <v-divider class="my-3"></v-divider>
              <v-progress-linear v-if="isGenerating" indeterminate color="primary" class="mb-3"></v-progress-linear>
              <v-alert v-if="generationError && !isGenerating" type="error" density="compact" class="mb-3">
                {{ generationError }}
              </v-alert>
              <div v-if="generatedIdeas.length > 0 && !isGenerating">
                <h3 class="text-subtitle-1 mb-3">Idées Générées :</h3>
                <v-list lines="three" density="compact">
                  <v-list-item
                    v-for="(idea, index) in generatedIdeas"
                    :key="index"
                    class="mb-2 pa-3"
                    elevation="1"
                    border
                  >
                    <v-list-item-title class="font-weight-bold mb-1">Idée #{{ index + 1 }}</v-list-item-title>
                    <v-list-item-subtitle style="white-space: pre-wrap;">{{ idea.text || idea }}</v-list-item-subtitle>
                     <!-- Actions par idée, ex: copier -->
                    <template v-slot:append>
                      <v-btn icon variant="text" density="compact" title="Copier l'idée" @click="copyToClipboard(idea.text || idea)">
                        <IconCopy size="18" />
                      </v-btn>
                    </template>
                  </v-list-item>
                </v-list>
              </div>
            </v-col>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="closeDialog" :disabled="isGenerating">
            Fermer
          </v-btn>
          <v-btn
            color="primary"
            @click="submitGeneration"
            :loading="isGenerating"
            :disabled="isGenerating || loadingModels || !selectedProvider || !selectedModel || !generationParams.projectContext"
          >
            <IconSparkles class="mr-2" />Générer les Idées
          </v-btn>
        </v-card-actions>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';
import { 
  VDialog, VCard, VCardTitle, VCardText, VCardActions, VContainer, VRow, VCol, 
  VSelect, VTextField, VTextarea, VBtn, VSpacer, VProgressLinear, VAlert, VDivider,
  VList, VListItem, VListItemTitle, VListItemSubtitle
} from 'vuetify/components';
import { IconBulb, IconSparkles, IconCopy } from '@tabler/icons-vue';
import SceneIdeaBackgroundURL from '@/assets/scene2.svg'; // Placeholder, à remplacer par une image pertinente

// Props & Emits
const props = defineProps({
  modelValue: Boolean, // Pour v-model
});
const emit = defineEmits(['update:modelValue', 'ideas-generated']);

// --- State pour la gestion des modèles IA (inspiré de CharacterManager) ---
const providerInfo = {
  gemini: { title: 'Google Gemini', description: 'Modèle avancé de Google' },
  mistral: { title: 'Mistral AI', description: 'Modèles open-source performants' },
  openrouter: { title: 'OpenRouter', description: 'Accès unifié à plusieurs modèles' },
};
const writingStyles = [
  { text: 'Normal', value: 'normal' }, { text: 'Formel', value: 'formel' },
  { text: 'Créatif', value: 'creatif' }, { text: 'Technique', value: 'technique' },
  { text: 'Humoristique', value: 'humoristique' }, { text: 'Poétique', value: 'poetique' },
  { text: 'Sombre', value: 'sombre' }, { text: 'Épique', value: 'epique' },
];

const providers = ref(Object.entries(providerInfo).map(([value, info]) => ({ ...info, value })));
const availableModels = reactive({});
const loadingModels = ref(false);
const errorLoadingModels = ref(false);
const selectedProvider = ref(config.defaultProvider);
const selectedModel = ref(null);
const selectedStyle = ref('normal');
const modelSearch = ref('');

// --- State spécifique à la génération d'idées de scènes ---
const generationParams = reactive({
  projectContext: '',
  sceneType: null,
  involvedCharacters: '',
  mood: '',
  keyElements: '',
  numberOfIdeas: 3,
});
const isGenerating = ref(false);
const generationError = ref(null);
const generatedIdeas = ref([]); // Tableau pour stocker les idées [{ text: '...' }, ...]

// --- Computed ---
const filteredModels = computed(() => {
  const modelsForProvider = availableModels[selectedProvider.value] || [];
  if (!modelSearch.value) return modelsForProvider;
  const searchTerm = modelSearch.value.toLowerCase();
  return modelsForProvider.filter(model =>
    model.formattedName?.toLowerCase().includes(searchTerm) ||
    model.description?.toLowerCase().includes(searchTerm) ||
    model.id?.toLowerCase().includes(searchTerm)
  );
});

const dialogBackgroundImageStyle = computed(() => ({
  backgroundImage: `url(${SceneIdeaBackgroundURL})`,
  opacity: 0.05, // Plus subtil
  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
  zIndex: 0, backgroundSize: 'cover', backgroundPosition: 'center center',
  pointerEvents: 'none',
}));

// --- Methods ---
const closeDialog = () => {
  emit('update:modelValue', false);
};

const fetchModels = async (provider = selectedProvider.value) => {
  if (!provider) return;
  loadingModels.value = true;
  errorLoadingModels.value = false;
  try {
    const response = await fetch(`${config.apiUrl}/models/${provider}`, { headers: { 'x-api-key': config.apiKey } });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    if (data && data.models) {
      const normalizedModels = data.models.map(model => {
        const baseModel = typeof model === 'string' ? { id: model, name: model } : { ...model };
        const name = baseModel.name?.toString() || baseModel.id?.toString() || '';
        const formattedName = (provider === 'openrouter' && name.includes('/')) ? name : name.replace(/^models\//, '');
        return { id: baseModel.id?.toString() || '', name, description: baseModel.description?.toString() || 'Aucune description', formattedName };
      }).filter(m => m.id);
      availableModels[provider] = normalizedModels;

      const currentModelIsValid = availableModels[provider].some(m => m.id === selectedModel.value);
      if (!currentModelIsValid || !selectedModel.value) {
        const defaultModelIdShort = config.providers[provider]?.defaultModel;
        const foundDefault = defaultModelIdShort ? availableModels[provider].find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
        selectedModel.value = foundDefault ? foundDefault.id : (availableModels[provider][0]?.id || null);
      }
    } else {
      throw new Error('Réponse API invalide.');
    }
  } catch (error) {
    errorLoadingModels.value = true;
    availableModels[provider] = [];
    selectedModel.value = null;
    console.error(handleApiError(error, `chargement des modèles pour ${providerInfo[provider]?.title || provider}`));
  } finally {
    loadingModels.value = false;
  }
};

const handleProviderChange = async (newProvider) => {
  selectedProvider.value = newProvider;
  modelSearch.value = '';
  selectedModel.value = null;
  if (!availableModels[newProvider] || availableModels[newProvider].length === 0) {
    await fetchModels(newProvider);
  } else {
    const models = availableModels[newProvider];
    const defaultModelIdShort = config.providers[newProvider]?.defaultModel;
    const foundDefault = defaultModelIdShort ? models.find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
    selectedModel.value = foundDefault ? foundDefault.id : (models[0]?.id || null);
  }
};

const submitGeneration = async () => {
  if (!generationParams.projectContext) {
    generationError.value = "Le contexte du projet est requis pour générer des idées.";
    return;
  }
  isGenerating.value = true;
  generationError.value = null;
  generatedIdeas.value = [];

  try {
    const payload = {
      provider: selectedProvider.value,
      model: selectedModel.value,
      style: selectedStyle.value,
      project_context: generationParams.projectContext,
      scene_type: generationParams.sceneType || null,
      involved_characters: generationParams.involvedCharacters || null,
      mood: generationParams.mood || null,
      key_elements: generationParams.keyElements || null,
      num_ideas: generationParams.numberOfIdeas || 3,
    };
    // TODO: Remplacer par l'appel API réel
    // const response = await fetch(`${config.apiUrl}/api/ai/generate-scene-ideas`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json', 'x-api-key': config.apiKey },
    //   body: JSON.stringify(payload),
    // });
    // if (!response.ok) {
    //   const errorData = await response.json().catch(() => ({ detail: 'Erreur inconnue lors de la génération.' }));
    //   throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    // }
    // const result = await response.json();
    // generatedIdeas.value = result.ideas || []; // Supposant que l'API retourne { ideas: [{text: '...'}, ...] }

    // --- Simulation d'appel API ---
    await new Promise(resolve => setTimeout(resolve, 1500));
    const numIdeas = payload.num_ideas;
    const exampleIdeas = [];
    for (let i = 0; i < numIdeas; i++) {
      exampleIdeas.push({ 
        text: `Exemple d'idée de scène #${i + 1} pour le contexte: ${payload.project_context.substring(0,50)}... (Style: ${payload.style})` 
      });
    }
    generatedIdeas.value = exampleIdeas;
    // --- Fin Simulation ---

    if (generatedIdeas.value.length === 0) {
        generationError.value = "L'IA n'a retourné aucune idée. Essayez d'affiner vos paramètres.";
    } else {
        emit('ideas-generated', generatedIdeas.value);
    }

  } catch (error) {
    generationError.value = handleApiError(error, 'génération des idées de scènes');
    console.error("Scene ideas generation error:", error);
  } finally {
    isGenerating.value = false;
  }
};

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    // Optionnel: afficher un snackbar de succès
    // import { useSnackbar } from '@/composables/useSnackbar'; // à importer globalement ou passer en prop
    // const { displaySnackbar } = useSnackbar();
    // displaySnackbar('Idée copiée dans le presse-papiers !', 'success');
    alert('Idée copiée dans le presse-papiers !'); // Simple alerte pour l'instant
  } catch (err) {
    console.error('Erreur lors de la copie : ', err);
    alert('Erreur lors de la copie.');
  }
};


// Charger les modèles pour le fournisseur initial lorsque la dialogue devient visible
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    generatedIdeas.value = []; // Reset des idées précédentes
    generationError.value = null;
    if (!availableModels[selectedProvider.value] || availableModels[selectedProvider.value].length === 0) {
      fetchModels(selectedProvider.value);
    } else if (!selectedModel.value || !availableModels[selectedProvider.value].some(m => m.id === selectedModel.value)) {
        const models = availableModels[selectedProvider.value];
        const defaultModelIdShort = config.providers[selectedProvider.value]?.defaultModel;
        const foundDefault = defaultModelIdShort ? models.find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
        selectedModel.value = foundDefault ? foundDefault.id : (models[0]?.id || null);
    }
  }
});

</script>

<style scoped>
.dialog-content-overlay {
  position: relative;
  z-index: 1;
  background-color: transparent;
}
.v-list-item {
  background-color: rgba(0,0,0,0.02);
}
.v-list-item:hover {
  background-color: rgba(0,0,0,0.04);
}
</style>