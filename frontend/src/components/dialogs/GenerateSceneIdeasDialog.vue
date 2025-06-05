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
               <!-- Nouveaux champs pour genre, thème principal, température -->
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="generationParams.genre"
                  label="Genre de l'histoire"
                  placeholder="Ex: Science-Fiction, Romance"
                  density="compact"
                  clearable
                  :disabled="isGenerating"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="generationParams.mainTheme"
                  label="Thème principal"
                  placeholder="Ex: La rédemption, La lutte contre l'oppression"
                  density="compact"
                  clearable
                  :disabled="isGenerating"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-slider
                  v-model.number="generationParams.temperature"
                  label="Température (Créativité)"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  thumb-label
                  density="compact"
                  :disabled="isGenerating"
                  class="mt-2"
                ></v-slider>
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
                  :max="10" 
                  density="compact"
                  :disabled="isGenerating"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="generationParams.keyElements"
                  label="Éléments clés ou contraintes (séparés par des virgules)"
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
                    <v-list-item-subtitle style="white-space: pre-wrap;">{{ idea }}</v-list-item-subtitle> <!-- Modifié: idea est maintenant une string -->
                     <!-- Actions par idée, ex: copier -->
                    <template v-slot:append>
                      <v-btn icon variant="text" density="compact" title="Copier l'idée" @click="copyIdeaText(idea)"> <!-- Modifié: utilise copyIdeaText et passe la string idea -->
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
  VList, VListItem, VListItemTitle, VListItemSubtitle, VSlider
} from 'vuetify/components';
import { IconBulb, IconSparkles, IconCopy } from '@tabler/icons-vue';
import SceneIdeaBackgroundURL from '@/assets/scene2.svg'; // Placeholder, à remplacer par une image pertinente
import { useSceneIdeas } from '@/composables/useSceneIdeas';

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

// --- State pour la génération d'idées (via composable) ---
const { 
  isLoading: isGenerating, // Renommer isLoading en isGenerating pour ce contexte
  generatedIdeas, 
  error: generationError, 
  generateIdeas,
  copyToClipboard: copyIdeaText // Renommer pour éviter conflit si une fonction locale copyToClipboard existait
} = useSceneIdeas();

// --- State spécifique à la génération d'idées de scènes ---
const generationParams = reactive({
  projectContext: '',
  sceneType: null,
  involvedCharacters: '',
  mood: '',
  keyElements: '',
  numberOfIdeas: 3,
  // Nouveaux champs pour correspondre à SceneIdeaRequest
  genre: '',
  mainTheme: '',
  temperature: 0.7,
});

const dialogBackgroundImageStyle = computed(() => ({
  backgroundImage: `url(${SceneIdeaBackgroundURL})`,
  backgroundSize: 'cover',
  backgroundPosition: 'center center',
  opacity: 0.1, // Ajustez pour la visibilité souhaitée
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: 0,
}));

const filteredModels = computed(() => {
  const models = availableModels[selectedProvider.value] || [];
  if (!modelSearch.value) {
    return models;
  }
  return models.filter(model => 
    model.formattedName.toLowerCase().includes(modelSearch.value.toLowerCase())
  );
});

const closeDialog = () => {
  emit('update:modelValue', false);
};

// --- Fonctions de gestion des modèles IA ---
const fetchModels = async (provider) => {
  if (!provider) return;
  loadingModels.value = true;
  errorLoadingModels.value = false;
  availableModels[provider] = []; // Vide la liste pour ce provider avant de fetcher

  try {
    const response = await fetch(`/api/models/${provider}`, {
      headers: { 'x-api-key': config.apiKey }
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Erreur inconnue lors du chargement des modèles.' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    if (data && data.models) {
      availableModels[provider] = data.models.map(m => ({
        ...m,
        formattedName: `${m.name} (${m.id.split('/').pop()})` // Pour un affichage plus clair
      }));
      // Sélectionner le modèle par défaut si disponible, sinon le premier de la liste
      const defaultModelIdShort = config.providers[provider]?.defaultModel;
      const foundDefault = defaultModelIdShort ? availableModels[provider].find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
      selectedModel.value = foundDefault ? foundDefault.id : (availableModels[provider][0]?.id || null);

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
  // Validation initiale
  if (!generationParams.projectContext) {
    // Le composable useSceneIdeas gère l'affichage des erreurs via Snackbar si l'appel API échoue.
    // Pour les erreurs de validation client, on pourrait ajouter un appel direct à showSnackbar ici.
    // Par exemple: useSnackbar().showSnackbar("Veuillez remplir tous les champs requis.", "error");
    // Pour l'instant, on se fie aux :disabled du bouton et à la gestion d'erreur du composable.
    console.warn("Validation échouée : projectContext, genre, ou mainTheme manquant.");
    return;
  }
  if (!selectedProvider.value || !selectedModel.value) {
    console.warn("Validation échouée : fournisseur ou modèle IA non sélectionné.");
    return;
  }

  const requestData = {
    ai_provider: selectedProvider.value,
    model: selectedModel.value,
    genre: generationParams.genre,
    main_theme: generationParams.mainTheme,
    key_elements: generationParams.keyElements ? generationParams.keyElements.split(',').map(s => s.trim()).filter(s => s) : [],
    writing_style: selectedStyle.value,
    tone: generationParams.mood || null, // 'mood' du form correspond à 'tone' pour l'API
    number_of_ideas: parseInt(generationParams.numberOfIdeas, 10) || 3,
    story_context: generationParams.projectContext,
    temperature: parseFloat(generationParams.temperature) || 0.7,
    // Inclure d'autres champs si nécessaire, ex: sceneType, involvedCharacters
    // scene_type: generationParams.sceneType || null,
    // involved_characters: generationParams.involvedCharacters ? generationParams.involvedCharacters.split(',').map(s => s.trim()).filter(s => s) : [],
  };

  await generateIdeas(requestData); // Appel au composable

  if (generatedIdeas.value && generatedIdeas.value.length > 0) {
    emit('ideas-generated', generatedIdeas.value);
  }
  // isGenerating et generationError sont gérés par le composable useSceneIdeas
};

// La fonction copyToClipboard est maintenant gérée par le composable via copyIdeaText
// Il n'est plus nécessaire de la définir localement si on utilise copyIdeaText directement dans le template.
// Si une logique spécifique était nécessaire ici avant d'appeler copyIdeaText, on pourrait la garder.

// Charger les modèles pour le fournisseur initial lorsque la dialogue devient visible
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    // Reset des idées précédentes et erreurs lors de l'ouverture
    // generatedIdeas.value = []; // Déjà géré par le composable generateIdeas
    // generationError.value = null; // Déjà géré par le composable generateIdeas
    
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
  background-color: rgba(var(--v-theme-surface), 0.9); /* Légèrement transparent pour laisser voir le fond */
  padding: 20px;
  border-radius: inherit; /* Hérite du radius de la v-card */
}
/* Autres styles si nécessaire */
</style>