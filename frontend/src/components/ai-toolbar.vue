<template>
  <div> <!-- Div racine -->
    <v-toolbar flat class="ai-toolbar">      
      <v-select
        v-model="selectedProvider"
        :items="providers"
        label="Fournisseur d'IA"
        item-title="title"
        item-value="value"
        :disabled="loadingModels || errorLoadingModels"
        :error="errorLoadingModels"
        class="provider-select" @update:model-value="handleProviderChange"
        density="compact"
        hide-details
      >
        <template v-slot:selection="{ item }">
          {{ item.title }}
        </template>
      </v-select>

      <!-- Recherche Modèle -->
      <v-text-field
        v-if="models.length > 5"
        v-model="modelSearch"
        label="Rechercher modèle..."
        density="compact"
        variant="outlined"
        clearable
        hide-details
        class="model-search-field"
      ></v-text-field>

      <!-- Modèle -->
      <v-select
        v-if="models.length > 0"
        v-model="selectedModel"
        :items="filteredModels"
        :label="modelLabel"
        item-title="formattedName"
        item-value="id"
        :disabled="loadingModels || errorLoadingModels"
        :error="errorLoadingModels"
        class="model-select"
        persistent-placeholder
        density="compact"
        hide-details
        @update:model-value="handleModelOrStyleChange"
      >
      </v-select>

      <!-- Style d'Écriture -->
      <v-select
        v-model="selectedStyleObject"
        :items="processedWritingStyles"
        label="Style d'écriture"
        item-title="text"
        return-object
        :disabled="loadingModels || errorLoadingModels || isCustomStyleActive"
        class="style-select"
        density="compact"
        hide-details
        @update:model-value="handleModelOrStyleChange"
      >
      </v-select>

      <!-- Switch pour activer/désactiver le style personnalisé -->
      <v-switch
        v-if="customStyleDescription"
        :model-value="isCustomStyleActive"
        @update:model-value="handleSwitchChange"
        color="success"
        label="Style Analysé"
        density="compact"
        hide-details
        class="ml-2 custom-style-switch"
      ></v-switch>

       <!-- Bouton pour ouvrir le dialogue d'analyse de style -->
       <v-tooltip location="bottom" text="Analyser un document pour définir un style personnalisé">
         <template v-slot:activator="{ props }">
           <v-btn
             icon="mdi-palette-swatch"
             v-bind="props"
             size="small"
             class="ml-2"
             :disabled="loadingModels"
             @click="showStyleAnalysisDialog = true"
           ></v-btn>
         </template>
       </v-tooltip>


    </v-toolbar>

    <!-- Alerte persistante en cas d'erreur de chargement des modèles -->
    <v-alert
      v-if="errorLoadingModels"
      type="error"
      density="compact"
      variant="tonal"
      class="ma-2"
      closable
      @update:model-value="errorLoadingModels = false"
    >
      Impossible de charger les modèles pour {{ providerInfo[selectedProvider]?.title || selectedProvider }}. Vérifiez la configuration et l'état du serveur.
    </v-alert>

    <!-- Snackbar pour les erreurs et informations -->
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

    <!-- Dialogue d'analyse de style -->
    <StyleAnalysisDialog
      v-model="showStyleAnalysisDialog"
      @style-applied="handleStyleApplied"
    />

  </div> <!-- Fin de la div racine -->
</template>

<script setup>
import { ref, computed, onMounted, watch, defineEmits } from 'vue';
import { config } from '../config.js';
import { handleApiError } from '../utils/errorHandler.js';
// Importer writingStyles directement
import { useAIModels, writingStyles } from '@/composables/useAIModels.js';
import { useCustomStyle } from '@/composables/useCustomStyle.js';
import StyleAnalysisDialog from './dialogs/StyleAnalysisDialog.vue';

// --- Événements émis ---
const emit = defineEmits(['model-selected']);

// --- Snackbar (local au composant) ---
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const snackbarColor = ref('info');
const snackbarTimeout = ref(5000);

const showSnackbarMessage = (message, color = 'error', timeout = 5000) => {
  snackbarMessage.value = message;
  snackbarColor.value = color;
  snackbarTimeout.value = timeout;
  showSnackbar.value = true;
};

// --- Utilisation des Composables ---
const {
  providerInfo,
  providers,
  availableModels,
  loadingModels,
  errorLoadingModels,
  fetchModels,
  selectDefaultModel,
} = useAIModels(showSnackbarMessage);

const {
  customStyleDescription,
  isCustomStyleActive,
  activeCustomStyleDescription,
  activateCustomStyle, // Utiliser pour activer
  deactivateCustomStyle, // Utiliser pour désactiver
  clearCustomStyle,
} = useCustomStyle();

// --- State local ---
const selectedProvider = ref(config.defaultProvider);
const selectedModel = ref(null);
// Initialiser avec l'objet 'normal' ou null
const findInitialStyle = () => writingStyles.find(s => s.value === 'normal') || null;
const selectedStyleObject = ref(findInitialStyle()); // Utiliser l'objet pour le v-select
const modelSearch = ref('');
const showStyleAnalysisDialog = ref(false);

// --- Computed Properties ---
const models = computed(() => availableModels[selectedProvider.value] || []);

const modelLabel = computed(() => {
  const counts = {
    gemini: 'Modèle Gemini',
    mistral: 'Modèle Mistral',
    openrouter: 'Modèle disponible',
  };
  return counts[selectedProvider.value] || 'Modèle';
});

const filteredModels = computed(() => {
  if (!modelSearch.value) {
    return models.value;
  }
  const searchTerm = modelSearch.value.toLowerCase();
  return models.value.filter(model =>
    model.formattedName?.toLowerCase().includes(searchTerm) ||
    model.description?.toLowerCase().includes(searchTerm) ||
    model.id?.toLowerCase().includes(searchTerm)
  );
});

// La liste des styles est maintenant statique
const processedWritingStyles = computed(() => {
  return Array.isArray(writingStyles) ? writingStyles.map(s => ({ ...s })) : [];
});


// --- Methods ---

// Gère le changement de modèle OU de style standard
const handleModelOrStyleChange = () => {  
  if (selectedStyleObject.value && selectedStyleObject.value.value !== 'custom') {
    if (isCustomStyleActive.value) {
      deactivateCustomStyle();
    }
  }
  emitSelection();
};

// Gère le changement d'état du v-switch
const handleSwitchChange = (newValue) => {
  if (newValue) {
    activateCustomStyle(); // Active via le composable
    // Optionnel: réinitialiser le select de style standard si nécessaire
    // selectedStyleObject.value = findInitialStyle();
  } else {
    deactivateCustomStyle(); // Désactive via le composable
  }
  emitSelection(); // Émettre l'état mis à jour
};


// Émet l'événement 'model-selected' avec l'état complet
const emitSelection = () => {
    // Si le style personnalisé est actif, sa description est utilisée, sinon la valeur du style standard sélectionné
    const finalStyleValue = isCustomStyleActive.value ? 'custom' : (selectedStyleObject.value?.value ?? 'normal');
    const styleDescToSend = isCustomStyleActive.value ? activeCustomStyleDescription.value : null;

    emit('model-selected', {
        provider: selectedProvider.value,
        model: selectedModel.value,
        style: finalStyleValue, // Envoyer 'custom' ou la valeur standard
        customStyleDescription: styleDescToSend // Envoyer la description seulement si actif
    });
    console.log("Emitted model-selected:", {
        provider: selectedProvider.value,
        model: selectedModel.value,
        style: finalStyleValue,
        customStyleDescription: styleDescToSend
    });
};

const handleProviderChange = async (newProvider) => {
  console.log(`[handleProviderChange] Début - newProvider: ${newProvider}`);
  modelSearch.value = '';
  selectedModel.value = null;
  errorLoadingModels.value = false;
  // Désactiver le style personnalisé lors du changement de fournisseur
  if (isCustomStyleActive.value) {
      deactivateCustomStyle();
  }
  selectedStyleObject.value = findInitialStyle(); // Revenir à l'objet 'normal'

  console.log(`[handleProviderChange] Appel de fetchModels pour ${newProvider}...`);
  const success = await fetchModels(newProvider);
  if (success) {
      selectedModel.value = selectDefaultModel(newProvider);
      console.log(`[handleProviderChange] Modèle par défaut sélectionné: ${selectedModel.value}`);
  } else {
      console.warn(`[handleProviderChange] Échec du chargement des modèles pour ${newProvider}`);
  }
  emitSelection();
  console.log(`[handleProviderChange] Fin.`);
};


// Gère l'événement émis par le dialogue lorsque le style est appliqué
const handleStyleApplied = (appliedStyleDescription) => {
    console.log("Style applied from dialog:", appliedStyleDescription);
    // Le composable a déjà activé le style (isCustomStyleActive est true).
    // Le switch devrait se mettre à jour automatiquement via :model-value="isCustomStyleActive"
    // On peut optionnellement remettre le select de style standard à 'normal'
    selectedStyleObject.value = findInitialStyle();
    emitSelection(); // Émettre le nouvel état avec le style personnalisé actif
    showSnackbarMessage("Style personnalisé appliqué avec succès !", 'success', 3000);
};


// --- Lifecycle ---
onMounted(async () => {
  console.log("[ai-toolbar] Mounted. Fetching initial models...");
  selectedStyleObject.value = findInitialStyle();
  const success = await fetchModels(selectedProvider.value);
  if (success) {
    selectedModel.value = selectDefaultModel(selectedProvider.value);
    console.log(`[ai-toolbar] Initial default model selected: ${selectedModel.value}`);
  } else {
     console.error("[ai-toolbar] Failed to fetch initial models.");
  }
  // S'assurer que l'état initial du style personnalisé est correctement reflété
  if (isCustomStyleActive.value) {
      console.log("[ai-toolbar] Custom style was active on mount.");
      // Le switch devrait être activé par :model-value
      // On remet le select standard à normal
      selectedStyleObject.value = findInitialStyle();
  }
  emitSelection(); // Émettre l'état initial
});

// --- Watchers ---
// Plus besoin de watcher isCustomStyleActive pour mettre à jour selectedStyleObject


</script>

<style scoped>
.ai-toolbar {
  display: flex;
  gap: 10px;
  padding: 8px 12px;
  flex-wrap: wrap;
  align-items: center;
}

.provider-select,
.model-select,
.style-select {
  min-width: 150px;
  max-width: 200px; /* Réduit légèrement pour faire de la place */
  flex-grow: 1;
}

.model-search-field {
  min-width: 150px;
  max-width: 220px; /* Réduit légèrement */
  flex-grow: 1;
}

.custom-style-switch {
  flex-grow: 0; /* Empêche le switch de prendre trop de place */
  margin-right: 5px; /* Espace avant le bouton */
}

/* Ajustement pour le bouton d'analyse */
.v-tooltip .v-btn {
    box-shadow: none;
}


@media (max-width: 960px) {
  .ai-toolbar {
    gap: 8px;
  }
  .provider-select,
  .model-select,
  .style-select,
  .model-search-field {
    min-width: 130px;
    max-width: 180px; /* Encore réduit */
  }
}

@media (max-width: 760px) { /* Ajusté le breakpoint pour mieux gérer les éléments */
  .ai-toolbar {
    flex-direction: column;
    align-items: stretch;
    padding: 8px;
  }

  .provider-select,
  .model-select,
  .style-select,
  .model-search-field,
  .custom-style-switch { /* Le switch prend toute la largeur aussi */
    width: 100%;
    max-width: none;
    margin-bottom: 8px;
  }

  /* Centrer le bouton d'analyse en mode colonne */
  .v-tooltip {
      display: flex;
      justify-content: center;
      margin-top: 5px;
  }
}
</style>