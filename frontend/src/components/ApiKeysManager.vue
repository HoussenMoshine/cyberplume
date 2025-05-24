<template>
  <v-container>
    <v-card class="pa-4">
      <v-card-title class="text-h5 mb-4">
        Gestion des Clés API des Fournisseurs IA
      </v-card-title>
      <v-card-subtitle class="mb-4">
        Configurez ici vos clés API personnelles pour accéder aux services d'IA. Ces clés sont stockées localement et chiffrées.
      </v-card-subtitle>

      <v-alert v-if="errorLoadingStatus" type="error" dense class="mb-4">
        Erreur lors du chargement du statut des clés API: {{ errorLoadingStatus }}
      </v-alert>
      <v-alert v-if="successMessage" type="success" dense class="mb-4">
        {{ successMessage }}
      </v-alert>
      <v-alert v-if="errorMessage" type="error" dense class="mb-4">
        {{ errorMessage }}
      </v-alert>

      <v-row v-if="isLoadingStatus">
        <v-col cols="12" class="text-center">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <p>Chargement du statut des clés...</p>
        </v-col>
      </v-row>

      <v-form v-else @submit.prevent="() => {}">
        <div v-for="provider in providers" :key="provider.name" class="mb-6">
          <v-row align="center">
            <v-col cols="12" md="3">
              <span class="text-subtitle-1 font-weight-medium">{{ provider.displayName }}</span>
              <v-chip x-small :color="provider.isSet ? 'green' : 'grey'" class="ml-2">
                {{ provider.isSet ? 'Configurée' : 'Non configurée' }}
              </v-chip>
            </v-col>
            <v-col cols="12" md="7">
              <v-text-field
                v-model="provider.apiKeyInput"
                :label="`Clé API pour ${provider.displayName}`"
                :placeholder="provider.isSet ? 'Clé configurée (laisser vide pour ne pas changer)' : 'Entrez votre clé API'"
                :type="provider.showKey ? 'text' : 'password'"
                :append-icon="provider.showKey ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="provider.showKey = !provider.showKey"
                outlined
                dense
                hide-details="auto"
                class="mb-2"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="2" class="d-flex">
              <v-btn 
                color="primary" 
                @click="saveApiKey(provider)" 
                :loading="provider.isSaving"
                :disabled="!provider.apiKeyInput && !provider.isSet"
                class="mr-2"
                small
              >
                <v-icon left small>mdi-content-save</v-icon>
                {{ provider.isSet && !provider.apiKeyInput ? 'Sauvée' : 'Sauver' }}
              </v-btn>
              <v-btn 
                v-if="provider.isSet" 
                color="error" 
                @click="initiateDeleteApiKey(provider)"
                :loading="provider.isDeleting"
                outlined
                small
              >
                <v-icon small>mdi-delete</v-icon>
              </v-btn>
            </v-col>
          </v-row>
           <v-divider v-if="provider.name !== providers[providers.length -1].name" class="mt-4"></v-divider>
        </div>
      </v-form>
    </v-card>

    <!-- Dialogue de confirmation de suppression -->
    <v-dialog v-model="showDeleteDialog" persistent max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Confirmer la suppression</v-card-title>
        <v-card-text>
          Êtes-vous sûr de vouloir supprimer la clé API pour 
          <strong>{{ providerToDelete?.displayName }}</strong> ?
          Cette action est irréversible.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cancelDeleteApiKey">Annuler</v-btn>
          <v-btn 
            color="error darken-1" 
            text 
            @click="confirmDeleteApiKey" 
            :loading="providerToDelete?.isDeleting"
          >
            Supprimer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useSnackbar } from '@/composables/useSnackbar'; // Assurez-vous que le chemin est correct

const apiUrl = import.meta.env.VITE_API_URL || '/api'; // Utiliser /api comme fallback
const apiKey = import.meta.env.VITE_API_KEY;

const { displaySnackbar } = useSnackbar();

const providers = ref([
  { name: 'gemini', displayName: 'Google Gemini', apiKeyInput: '', isSet: false, showKey: false, isSaving: false, isDeleting: false },
  { name: 'mistral', displayName: 'Mistral AI', apiKeyInput: '', isSet: false, showKey: false, isSaving: false, isDeleting: false },
  { name: 'openrouter', displayName: 'OpenRouter', apiKeyInput: '', isSet: false, showKey: false, isSaving: false, isDeleting: false },
]);

const isLoadingStatus = ref(true);
const errorLoadingStatus = ref(null);
const successMessage = ref(''); // Peut être conservé pour des messages globaux si besoin, sinon displaySnackbar suffit
const errorMessage = ref(''); // Peut être conservé pour des messages globaux si besoin, sinon displaySnackbar suffit

// Pour le dialogue de confirmation
const showDeleteDialog = ref(false);
const providerToDelete = ref(null);

const getHeaders = () => ({
  'X-API-Key': apiKey,
  'Content-Type': 'application/json',
});

const fetchApiKeysStatus = async () => {
  isLoadingStatus.value = true;
  errorLoadingStatus.value = null;
  // successMessage.value = ''; // Géré par snackbar
  // errorMessage.value = ''; // Géré par snackbar
  try {
    const response = await axios.get(`${apiUrl}/api-keys-config/status`, { headers: getHeaders() });
    const statusData = response.data;
    providers.value.forEach(p => {
      const status = statusData.find(s => s.provider_name === p.name);
      if (status) {
        p.isSet = status.has_key_set;
      }
    });
  } catch (error) {
    console.error("Erreur lors de la récupération du statut des clés API:", error);
    const detailError = error.response?.data?.detail || error.message || 'Une erreur inconnue est survenue lors du chargement du statut.';
    errorLoadingStatus.value = detailError; // Pour l'alerte v-if
    displaySnackbar(detailError, 'error');
  } finally {
    isLoadingStatus.value = false;
  }
};

const saveApiKey = async (provider) => {
  if (!provider.apiKeyInput) {
    if(provider.isSet) {
        displaySnackbar(`Clé pour ${provider.displayName} non modifiée.`, 'info');
        return;
    }
    displaySnackbar(`Veuillez entrer une clé API pour ${provider.displayName}.`, 'warning');
    return;
  }
  provider.isSaving = true;
  // successMessage.value = '';
  // errorMessage.value = '';
  try {
    await axios.post(`${apiUrl}/api-keys-config/${provider.name}`, 
      { api_key: provider.apiKeyInput }, 
      { headers: getHeaders() }
    );
    provider.isSet = true;
    // provider.apiKeyInput = ''; // Optionnel: vider le champ après sauvegarde
    displaySnackbar(`Clé API pour ${provider.displayName} sauvegardée avec succès.`, 'success');
    await fetchApiKeysStatus(); // Recharger le statut
  } catch (error) {
    console.error(`Erreur lors de la sauvegarde de la clé API pour ${provider.displayName}:`, error);
    const detailError = error.response?.data?.detail || error.message || 'Une erreur inconnue est survenue lors de la sauvegarde.';
    // errorMessage.value = detailError;
    displaySnackbar(detailError, 'error');
  } finally {
    provider.isSaving = false;
  }
};

const initiateDeleteApiKey = (provider) => {
  providerToDelete.value = provider;
  showDeleteDialog.value = true;
};

const cancelDeleteApiKey = () => {
  showDeleteDialog.value = false;
  if (providerToDelete.value) {
    providerToDelete.value.isDeleting = false; // Réinitialiser au cas où
  }
  providerToDelete.value = null;
};

const confirmDeleteApiKey = async () => {
  if (!providerToDelete.value) return;

  const provider = providerToDelete.value;
  provider.isDeleting = true;
  // successMessage.value = '';
  // errorMessage.value = '';

  try {
    await axios.delete(`${apiUrl}/api-keys-config/${provider.name}`, { headers: getHeaders() });
    provider.isSet = false;
    provider.apiKeyInput = '';
    displaySnackbar(`Clé API pour ${provider.displayName} supprimée avec succès.`, 'success');
    // Ne pas appeler fetchApiKeysStatus() ici, car cela pourrait causer des problèmes si le dialogue est encore en transition.
    // Le statut est mis à jour localement (provider.isSet = false).
    // Si un re-fetch est absolument nécessaire, il faudrait le gérer avec plus de précautions.
  } catch (error) {
    console.error(`Erreur lors de la suppression de la clé API pour ${provider.displayName}:`, error);
    const detailError = error.response?.data?.detail || error.message || 'Une erreur inconnue est survenue lors de la suppression.';
    // errorMessage.value = detailError;
    displaySnackbar(detailError, 'error');
  } finally {
    provider.isDeleting = false;
    showDeleteDialog.value = false;
    providerToDelete.value = null; 
    // On peut appeler fetchApiKeysStatus ici si on veut s'assurer que l'état global est synchro,
    // mais cela peut être un peu lourd. La mise à jour locale devrait suffire pour l'UI.
    await fetchApiKeysStatus(); // Re-fetch pour s'assurer de la cohérence après la fermeture du dialogue
  }
};

onMounted(() => {
  fetchApiKeysStatus();
});

</script>

<style scoped>
.v-card-subtitle {
  white-space: normal; /* Permet le retour à la ligne pour les sous-titres longs */
}
</style>