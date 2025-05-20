<template>
  <v-container>
    <v-toolbar flat density="compact">
      <v-toolbar-title class="text-h6 font-weight-medium">Gestion des Personnages</v-toolbar-title>
      <v-spacer></v-spacer>
      <!-- Bouton pour ouvrir la dialogue de génération IA -->
      <v-btn color="primary" @click="openGenerateDialog">
        <IconSparkles size="20" class="mr-1"/> <!-- Remplacement MDI -->
        Générer par IA
      </v-btn>
      <!-- Bouton pour ajouter manuellement -->
      <v-btn class="ml-2" variant="outlined" color="primary" @click="openEditDialog(null)">
         <IconPlus size="20" class="mr-1"/> <!-- Remplacement MDI -->
         Ajouter Manuellement
      </v-btn>
    </v-toolbar>

    <v-divider class="my-2"></v-divider>

    <!-- Afficher la liste des personnages existants -->
    <v-progress-linear v-if="loadingCharacters" indeterminate color="primary"></v-progress-linear>
    <v-alert v-if="errorCharacters" type="error" dense text class="mb-2">
      {{ errorCharacters }}
    </v-alert>

    <v-row v-if="!loadingCharacters && characters.length === 0">
       <v-col>
         <p class="text-center text-grey">Aucun personnage trouvé.</p>
       </v-col>
    </v-row>

    <v-list lines="two" v-if="!loadingCharacters && characters.length > 0">
       <v-list-item
         v-for="character in characters"
         :key="character.id"
         :title="character.name"
         :subtitle="character.description || 'Pas de description'"
       >
         <template v-slot:append>
           <!-- Boutons Editer/Supprimer -->
           <v-btn
              variant="text"
              density="compact"
              title="Modifier"
              @click="openEditDialog(character)"
              icon
           ><IconPencil size="20"/></v-btn> <!-- Remplacement MDI -->
           <v-btn
              variant="text"
              density="compact"
              title="Supprimer"
              @click="openDeleteConfirmDialog(character)"
              class="ml-1"
              color="error"
              icon
           ><IconTrash size="20"/></v-btn> <!-- Remplacement MDI -->
         </template>
       </v-list-item>
    </v-list>


    <!-- Dialogue pour la génération IA -->
    <v-dialog v-model="showGenerateDialog" persistent max-width="700px">
      <v-card style="position: relative;"> <!-- Ajout de position: relative ici pour le contexte d'empilement -->
        <!-- NOUVEAU : Div pour l'image de fond -->
        <div :style="characterBackgroundImageStyle"></div>

        <!-- Contenu existant du dialogue, enveloppé -->
        <div class="character-dialog-content-overlay">
          <v-card-title>
            <span class="text-h5">Générer un Personnage par IA</span>
          </v-card-title>
          <v-card-text>
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
                   <!-- Champ de recherche pour les modèles -->
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
                     label="Style d'écriture"
                     item-title="text"
                     item-value="value"
                     :disabled="loadingModels || isGenerating"
                     density="compact"
                     hide-details
                   ></v-select>
                </v-col>

                <!-- Champs pour caractéristiques -->
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="generationOptions.ethnicity"
                    label="Ethnie (optionnel)"
                    density="compact"
                    clearable
                    :disabled="isGenerating"
                    hide-details
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-select
                    v-model="generationOptions.gender"
                    :items="['Homme', 'Femme', 'Autre', 'Non spécifié']"
                    label="Sexe (optionnel)"
                    density="compact"
                    clearable
                    :disabled="isGenerating"
                    hide-details
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="generationOptions.approxAge"
                    label="Âge approximatif (optionnel)"
                    placeholder="Ex: 30 ans, Adolescent"
                    density="compact"
                    clearable
                    :disabled="isGenerating"
                    hide-details
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="generationOptions.nationality"
                    label="Nationalité (optionnel)"
                    density="compact"
                    clearable
                    :disabled="isGenerating"
                    hide-details
                  ></v-text-field>
                </v-col>
                <!-- NOUVEAU: Champs Métier et Vêtements -->
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="generationOptions.job"
                    label="Métier (optionnel)"
                    placeholder="Ex: Ingénieur, Artiste"
                    density="compact"
                    clearable
                    :disabled="isGenerating"
                    hide-details
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="generationOptions.clothing"
                    label="Vêtements (optionnel)"
                    placeholder="Ex: Costume sombre, Robe légère"
                    density="compact"
                    clearable
                    :disabled="isGenerating"
                    hide-details
                  ></v-text-field>
                </v-col>


                <!-- Champ pour les indications utilisateur -->
                <v-col cols="12">
                  <v-textarea
                    v-model="promptDetails"
                    label="Autres indications (optionnel)"
                    placeholder="Ex: Traits de caractère spécifiques, tics, secrets..."
                    rows="3"
                    auto-grow
                    clearable
                    :disabled="isGenerating"
                  ></v-textarea>
                </v-col>

                <!-- Zone pour afficher le résultat -->
                <v-col cols="12" v-if="generatedCharacter || generationError || isGenerating">
                   <v-divider class="my-3"></v-divider>
                   <v-progress-linear v-if="isGenerating" indeterminate color="primary" class="mb-3"></v-progress-linear>
                   <v-alert v-if="generationError && !isGenerating" type="error" density="compact" class="mb-3">
                      {{ generationError }}
                   </v-alert>
                   <div v-if="generatedCharacter && !isGenerating">
                      <h3 class="mb-2">Résultat :</h3>
                      <v-card variant="outlined" class="pa-3">
                         <p><strong>Nom:</strong> {{ generatedCharacter.name }}</p>
                         <p><strong>Description:</strong> {{ generatedCharacter.description || 'N/A' }}</p>
                         <p><strong>Backstory:</strong> {{ generatedCharacter.backstory || 'N/A' }}</p>
                      </v-card>
                      <v-btn color="success" class="mt-3" @click="saveGeneratedCharacter" :loading="isSavingCharacter">
                         Sauvegarder ce personnage
                      </v-btn>
                   </div>
                </v-col>

              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey darken-1" text @click="closeGenerateDialog" :disabled="isGenerating">
              Fermer
            </v-btn>
            <v-btn
              color="primary"
              @click="submitGeneration"
              :loading="isGenerating"
              :disabled="isGenerating || loadingModels || !selectedProvider || !selectedModel"
            >
              Générer
            </v-btn>
          </v-card-actions>
        </div> <!-- Fin de .character-dialog-content-overlay -->
      </v-card>
    </v-dialog>

    <!-- AJOUT: Dialogue pour l'édition/ajout manuel -->
    <v-dialog v-model="showEditDialog" persistent max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editingCharacter && editingCharacter.id ? 'Modifier' : 'Ajouter' }} un Personnage</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editFormData.name"
                  label="Nom*"
                  required
                  :error-messages="editErrors.name"
                  @input="editErrors.name = ''"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editFormData.description"
                  label="Description"
                  rows="3"
                  auto-grow
                ></v-textarea>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editFormData.backstory"
                  label="Backstory"
                  rows="5"
                  auto-grow
                ></v-textarea>
              </v-col>
            </v-row>
            <v-alert v-if="editError" type="error" dense text class="mt-2">
              {{ editError }}
            </v-alert>
          </v-container>
          <small>*champ requis</small>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="closeEditDialog" :disabled="isEditing">
            Annuler
          </v-btn>
          <v-btn
            color="primary"
            @click="submitEditCharacter"
            :loading="isEditing"
            :disabled="isEditing || !editFormData.name"
          >
            Enregistrer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- AJOUT: Dialogue de confirmation de suppression -->
    <v-dialog v-model="showDeleteConfirmDialog" persistent max-width="400px">
      <v-card>
        <v-card-title class="text-h5 error--text d-flex align-center">
          <IconAlertCircle size="24" class="mr-2" color="error"/> <!-- Remplacement MDI -->
          Confirmer la suppression
        </v-card-title>
        <v-card-text>
          Êtes-vous sûr de vouloir supprimer le personnage "<strong>{{ deletingCharacter?.name }}</strong>" ?
          <br>
          <strong>Cette action est irréversible.</strong>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="closeDeleteConfirmDialog" :disabled="isDeleting">
            Annuler
          </v-btn>
          <v-btn
            color="error"
            text
            @click="confirmDeleteCharacter"
            :loading="isDeleting"
          >
            Supprimer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

     <!-- Snackbar -->
     <v-snackbar
       v-model="snackbarVisible"
       :color="snackbarColor"
       :timeout="3000"
       location="bottom right"
     >
       {{ snackbarText }}
       <template v-slot:actions>
         <v-btn color="white" variant="text" @click="snackbarVisible = false">
           Fermer
         </v-btn>
       </template>
     </v-snackbar>

  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { config } from '@/config.js';
import { handleApiError } from '@/utils/errorHandler.js';
// Importer les composants Vuetify nécessaires
import {
  VContainer, VToolbar, VToolbarTitle, VSpacer, VBtn, VDivider, VRow, VCol,
  VDialog, VCard, VCardTitle, VCardText, VTextarea, VCardActions, VAlert, VSnackbar,
  VProgressLinear, VList, VListItem, VSelect, VTextField
} from 'vuetify/components';

// NOUVEAU: Importer l'image SVG pour le fond
import CharacterBackgroundURL from '@/assets/character2.svg';

// --- Données statiques (similaire à ai-toolbar) ---
const providerInfo = {
  gemini: { title: 'Google Gemini', description: 'Modèle avancé de Google' },
  mistral: { title: 'Mistral AI', description: 'Modèles open-source performants' },
  openrouter: { title: 'OpenRouter', description: 'Accès unifié à plusieurs modèles' },
};

const writingStyles = [
  { text: 'Normal', value: 'normal' }, { text: 'Formel', value: 'formel' },
  { text: 'Créatif', value: 'creatif' }, { text: 'Technique', value: 'technique' },
  { text: 'Humoristique', value: 'humoristique' }, { text: 'Poétique', value: 'poetique' },
  { text: 'Adulte', value: 'adulte' },
];

// Import des icônes Tabler nécessaires
import { IconSparkles, IconPlus, IconPencil, IconTrash, IconAlertCircle } from '@tabler/icons-vue';


// --- State ---
const characters = ref([]); // Liste des personnages existants
const loadingCharacters = ref(false);
const errorCharacters = ref(null);

// State Génération IA
const showGenerateDialog = ref(false);
const promptDetails = ref('');
const isGenerating = ref(false);
const generationError = ref(null);
const generatedCharacter = ref(null); // { name: '', description: '', backstory: '', raw_response: '' }
const isSavingCharacter = ref(false); // Pour le bouton Sauvegarder

// State pour les options de génération supplémentaires
const generationOptions = reactive({
  ethnicity: '',
  gender: null, // Utiliser null pour v-select avec clearable
  approxAge: '',
  nationality: '',
  job: '', // NOUVEAU
  clothing: '' // NOUVEAU
});

// State Sélecteurs IA
const providers = ref(Object.entries(providerInfo).map(([value, info]) => ({ ...info, value })));
const availableModels = reactive({}); // Stocke les modèles par provider: { gemini: [], mistral: [], ... }
const loadingModels = ref(false);
const errorLoadingModels = ref(false);
const selectedProvider = ref(config.defaultProvider);
const selectedModel = ref(null);
const selectedStyle = ref('normal');
const modelSearch = ref('');

// AJOUT: State Édition/Ajout Manuel
const showEditDialog = ref(false);
const editingCharacter = ref(null); // null pour ajout, objet pour édition
const editFormData = reactive({ id: null, name: '', description: '', backstory: '' });
const isEditing = ref(false); // Pour le chargement de l'enregistrement
const editError = ref(null); // Erreur spécifique à la dialogue d'édition
const editErrors = reactive({ name: '' }); // Erreurs de validation par champ

// AJOUT: State Suppression
const showDeleteConfirmDialog = ref(false);
const deletingCharacter = ref(null);
const isDeleting = ref(false);

// Snackbar state
const snackbarVisible = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');

// --- Computed ---
const filteredModels = computed(() => {
  const modelsForProvider = availableModels[selectedProvider.value] || [];
  if (!modelSearch.value) {
    return modelsForProvider;
  }
  const searchTerm = modelSearch.value.toLowerCase();
  return modelsForProvider.filter(model =>
    model.formattedName?.toLowerCase().includes(searchTerm) ||
    model.description?.toLowerCase().includes(searchTerm) ||
    model.id?.toLowerCase().includes(searchTerm)
  );
});

// NOUVEAU: Computed property pour le style de l'image de fond du dialogue personnage
const characterBackgroundImageStyle = computed(() => ({
  backgroundImage: `url(${CharacterBackgroundURL})`,
  opacity: 0.060,
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: 0,
  backgroundSize: 'cover',
  backgroundPosition: 'center center',
  pointerEvents: 'none', // Empêche le div de fond d'intercepter les clics
}));

// --- Methods ---

// Charger les personnages existants
const fetchCharacters = async () => {
  loadingCharacters.value = true;
  errorCharacters.value = null;
  try {
    const response = await fetch(`${config.apiUrl}/api/characters/`, {
      headers: { 'x-api-key': config.apiKey },
    });
    if (!response.ok) {
      // Gestion d'erreur améliorée
      let errorBody = null;
      try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
      const error = new Error(`HTTP error! status: ${response.status}`);
      error.response = { status: response.status, data: errorBody };
      throw error;
    }
    characters.value = await response.json();
  } catch (error) {
    errorCharacters.value = handleApiError(error, 'chargement des personnages');
    showSnackbar(errorCharacters.value, 'error');
    console.error("Fetch characters error:", error);
  } finally {
    loadingCharacters.value = false;
  }
};

// Charger les modèles pour le fournisseur sélectionné
const fetchModels = async (provider = selectedProvider.value) => {
  if (!provider) return;
  console.log(`[fetchModels] Début pour provider: ${provider}`);
  loadingModels.value = true;
  errorLoadingModels.value = false;
  // Ne pas réinitialiser selectedModel ici, attendre la fin du chargement

  try {
    const url = `${config.apiUrl}/models/${provider}`;
    const headers = { 'x-api-key': config.apiKey };
    const response = await fetch(url, { headers });
    if (!response.ok) {
      let errorBody = null;
      try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
      const error = new Error(`HTTP error! status: ${response.status}`);
      error.response = { status: response.status, data: errorBody };
      throw error;
    }
    const data = await response.json();
    if (data && data.models) {
       const normalizedModels = data.models.map(model => {
         try {
           const baseModel = typeof model === 'string' ? { id: model, name: model } : { ...model };
           const name = baseModel.name?.toString() ? baseModel.name.toString() : (baseModel.id?.toString() || '');
           // Correction: Utiliser l'ID complet pour OpenRouter si le nom n'est pas unique
           const formattedName = (provider === 'openrouter' && name.includes('/')) ? name : name.replace(/^models\//, '');
           const normalized = {
             id: baseModel.id?.toString() || '',
             name: name,
             description: baseModel.description?.toString() || 'Aucune description',
             formattedName: formattedName
           };
           return normalized.id ? normalized : null;
         } catch (e) { console.error("Erreur normalisation modèle:", e, model); return null; }
       }).filter(m => m !== null);

       availableModels[provider] = normalizedModels; // Stocker dans l'objet réactif
       console.log(`Normalized models for ${provider}:`, availableModels[provider]);

       // Sélectionner le modèle par défaut ou le premier si le modèle actuel n'est plus valide
       const currentModelIsValid = availableModels[provider].some(m => m.id === selectedModel.value);
       if (!currentModelIsValid || !selectedModel.value) {
           const defaultModelIdShort = config.providers[provider]?.defaultModel;
           const foundDefault = defaultModelIdShort ? availableModels[provider].find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
           selectedModel.value = foundDefault ? foundDefault.id : (availableModels[provider].length > 0 ? availableModels[provider][0].id : null);
           console.log(`Selected default/first model ID for ${provider}: ${selectedModel.value}`);
       } else {
           console.log(`Current model ${selectedModel.value} is still valid for ${provider}.`);
       }

    } else {
       console.error('Réponse API invalide ou structure de données inattendue:', data);
       throw new Error('Réponse API invalide ou structure de données inattendue.');
    }
  } catch (error) {
    const userMessage = handleApiError(error, `chargement des modèles pour ${providerInfo[provider]?.title || provider}`);
    showSnackbar(userMessage, 'error', 6000);
    availableModels[provider] = []; // Vider en cas d'erreur
    selectedModel.value = null; // Désélectionner le modèle
    errorLoadingModels.value = true;
  } finally {
    loadingModels.value = false;
    console.log(`[fetchModels] Fin pour provider: ${provider}`);
  }
};

// Gérer le changement de fournisseur
const handleProviderChange = async (newProvider) => {
  console.log(`Provider changed to: ${newProvider}`);
  selectedProvider.value = newProvider; // Assurer la mise à jour
  modelSearch.value = ''; // Réinitialiser la recherche
  selectedModel.value = null; // Réinitialiser le modèle sélectionné
  if (!availableModels[newProvider] || availableModels[newProvider].length === 0) { // Charger seulement si pas déjà en cache ou vide
    await fetchModels(newProvider);
  } else {
     // Si déjà chargé, sélectionner le défaut/premier
     const models = availableModels[newProvider];
     const defaultModelIdShort = config.providers[newProvider]?.defaultModel;
     const foundDefault = defaultModelIdShort ? models.find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
     selectedModel.value = foundDefault ? foundDefault.id : (models.length > 0 ? models[0].id : null);
     console.log(`Using cached models for ${newProvider}. Selected default/first model ID: ${selectedModel.value}`);
  }
};

// Ouvrir la dialogue de génération IA
const openGenerateDialog = () => {
  promptDetails.value = '';
  generationError.value = null;
  generatedCharacter.value = null;
  isSavingCharacter.value = false;
  // Réinitialiser les options de génération
  generationOptions.ethnicity = '';
  generationOptions.gender = null;
  generationOptions.approxAge = '';
  generationOptions.nationality = '';
  generationOptions.job = ''; // NOUVEAU
  generationOptions.clothing = ''; // NOUVEAU

  // Charger les modèles pour le fournisseur par défaut si nécessaire
  if (!availableModels[selectedProvider.value] || availableModels[selectedProvider.value].length === 0) {
      fetchModels(selectedProvider.value);
  } else if (!selectedModel.value || !availableModels[selectedProvider.value].some(m => m.id === selectedModel.value)) {
      // Si modèles chargés mais aucun sélectionné ou invalide, sélectionner défaut
      const models = availableModels[selectedProvider.value];
      const defaultModelIdShort = config.providers[selectedProvider.value]?.defaultModel;
      const foundDefault = defaultModelIdShort ? models.find(m => m.id === defaultModelIdShort || m.id.endsWith('/' + defaultModelIdShort)) : null;
      selectedModel.value = foundDefault ? foundDefault.id : (models.length > 0 ? models[0].id : null);
  }
  showGenerateDialog.value = true;
};

const closeGenerateDialog = () => {
  showGenerateDialog.value = false;
};

// Soumettre la génération IA
const submitGeneration = async () => {
  isGenerating.value = true;
  generationError.value = null;
  generatedCharacter.value = null;
  isSavingCharacter.value = false;

  const provider = selectedProvider.value;
  const model = selectedModel.value;
  const style = selectedStyle.value;

  if (!provider || !model) {
      generationError.value = "Veuillez sélectionner un fournisseur et un modèle IA.";
      isGenerating.value = false;
      return;
  }

  try {
    const response = await fetch(`${config.apiUrl}/api/characters/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': config.apiKey,
      },
      body: JSON.stringify({
        provider: provider,
        model: model,
        style: style,
        prompt_details: promptDetails.value || null,
        // Ajout des options de génération
        ethnicity: generationOptions.ethnicity || null,
        gender: generationOptions.gender || null,
        approx_age: generationOptions.approxAge || null, // Utiliser snake_case pour l'API
        nationality: generationOptions.nationality || null,
        job: generationOptions.job || null, // NOUVEAU
        clothing: generationOptions.clothing || null, // NOUVEAU
      }),
    });

    if (!response.ok) {
      let errorBody = null;
      try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
      const error = new Error(`HTTP error! status: ${response.status}`);
      error.response = { status: response.status, data: errorBody };
      throw error;
    }

    const result = await response.json();
    generatedCharacter.value = result;

  } catch (error) {
    generationError.value = handleApiError(error, 'génération du personnage');
    console.error("Character generation error:", error);
  } finally {
    isGenerating.value = false;
  }
};

// Sauvegarder le personnage généré (appelé depuis la dialogue de génération)
const saveGeneratedCharacter = async () => {
   if (!generatedCharacter.value) return;
   await saveCharacter({
       name: generatedCharacter.value.name,
       description: generatedCharacter.value.description,
       backstory: generatedCharacter.value.backstory,
   });
   // Si succès, la dialogue est fermée par saveCharacter
};

// AJOUT: Ouvrir la dialogue d'édition/ajout manuel
const openEditDialog = (character) => {
  editingCharacter.value = character; // null pour ajout, objet pour édition
  editError.value = null;
  editErrors.name = ''; // Reset validation errors
  if (character) {
    // Mode édition: pré-remplir le formulaire
    editFormData.id = character.id;
    editFormData.name = character.name;
    editFormData.description = character.description || '';
    editFormData.backstory = character.backstory || '';
  } else {
    // Mode ajout: réinitialiser le formulaire
    editFormData.id = null;
    editFormData.name = '';
    editFormData.description = '';
    editFormData.backstory = '';
  }
  showEditDialog.value = true;
};

const closeEditDialog = () => {
  showEditDialog.value = false;
  editingCharacter.value = null;
};

// AJOUT: Soumettre l'édition/ajout manuel
const submitEditCharacter = async () => {
  if (!editFormData.name) {
    editErrors.name = 'Le nom est requis.';
    return;
  }
  await saveCharacter({ ...editFormData });
};

// AJOUT: Fonction générique pour sauvegarder (créer ou mettre à jour)
const saveCharacter = async (characterData) => {
  const isUpdate = !!characterData.id;
  const url = isUpdate ? `${config.apiUrl}/api/characters/${characterData.id}` : `${config.apiUrl}/api/characters/`;
  const method = isUpdate ? 'PUT' : 'POST';

  // Définir l'état de chargement approprié
  if (showEditDialog.value) isEditing.value = true;
  else if (showGenerateDialog.value) isSavingCharacter.value = true;
  editError.value = null; // Reset error in edit dialog

  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': config.apiKey,
      },
      // Ne pas envoyer l'ID dans le body pour la création
      body: JSON.stringify(isUpdate ? characterData : { name: characterData.name, description: characterData.description, backstory: characterData.backstory }),
    });

    if (!response.ok) {
      let errorBody = null;
      try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
      const error = new Error(`HTTP error! status: ${response.status}`);
      error.response = { status: response.status, data: errorBody };
      throw error;
    }

    // Fermer la dialogue active, rafraîchir la liste et afficher un succès
    if (showEditDialog.value) closeEditDialog();
    if (showGenerateDialog.value) closeGenerateDialog(); // Fermer aussi si sauvegarde depuis génération IA
    await fetchCharacters(); // Recharger la liste
    showSnackbar(`Personnage ${isUpdate ? 'mis à jour' : 'ajouté'} avec succès !`, 'success');

  } catch (error) {
    const saveErrorMsg = handleApiError(error, `${isUpdate ? 'mise à jour' : 'ajout'} du personnage`);
    if (showEditDialog.value) {
      editError.value = saveErrorMsg; // Afficher l'erreur dans la dialogue d'édition
    } else {
      showSnackbar(saveErrorMsg, 'error'); // Afficher dans snackbar si depuis génération IA
    }
    console.error("Save character error:", error);
    // Laisser la dialogue ouverte en cas d'erreur
  } finally {
    if (showEditDialog.value) isEditing.value = false;
    else if (showGenerateDialog.value) isSavingCharacter.value = false;
  }
};

// AJOUT: Ouvrir la dialogue de confirmation de suppression
const openDeleteConfirmDialog = (character) => {
  deletingCharacter.value = character;
  showDeleteConfirmDialog.value = true;
};

const closeDeleteConfirmDialog = () => {
  showDeleteConfirmDialog.value = false;
  deletingCharacter.value = null;
};

// AJOUT: Confirmer et exécuter la suppression
const confirmDeleteCharacter = async () => {
  if (!deletingCharacter.value) return;

  isDeleting.value = true;
  try {
    const response = await fetch(`${config.apiUrl}/api/characters/${deletingCharacter.value.id}`, {
      method: 'DELETE',
      headers: { 'x-api-key': config.apiKey },
    });

    if (!response.ok) {
      let errorBody = null;
      try { errorBody = await response.json(); } catch (e) { /* Ignore */ }
      const error = new Error(`HTTP error! status: ${response.status}`);
      error.response = { status: response.status, data: errorBody };
      throw error;
    }

    closeDeleteConfirmDialog();
    await fetchCharacters(); // Recharger la liste
    showSnackbar('Personnage supprimé avec succès.', 'success');

  } catch (error) {
    const deleteErrorMsg = handleApiError(error, 'suppression du personnage');
    showSnackbar(deleteErrorMsg, 'error');
    console.error("Delete character error:", error);
    // Laisser la dialogue ouverte en cas d'erreur ? Non, fermons-la.
    closeDeleteConfirmDialog();
  } finally {
    isDeleting.value = false;
  }
};

// Afficher le Snackbar
const showSnackbar = (text, color = 'success', timeout = 3000) => {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbarVisible.value = true;
};

// --- Lifecycle ---
onMounted(() => {
  fetchCharacters(); // Charger les personnages au montage
  fetchModels(selectedProvider.value); // Charger les modèles pour le fournisseur initial
});

</script>

<style scoped>
/* Styles spécifiques si nécessaire */
.v-list-item {
  border-bottom: 1px solid #E0E0E0; /* Updated border color */
}

/* NOUVEAU: Style pour le contenu par-dessus l'image de fond */
.character-dialog-content-overlay {
  position: relative;
  z-index: 1;
  background-color: transparent; /* Important pour voir l'image derrière */
  /* Vous pouvez ajouter un léger fond semi-transparent ici si le texte est difficile à lire */
  /* background-color: rgba(255, 255, 255, 0.5); */
}
</style>