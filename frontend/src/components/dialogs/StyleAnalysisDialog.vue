<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Analyser le Style d'un Document</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <p class="mb-4">
            Uploadez un document (PDF, DOCX, ODT, TXT) pour que l'IA analyse son style d'écriture.
            Le style détecté pourra ensuite être utilisé pour guider les générations futures.
          </p>
          <v-file-input
            v-model="selectedFile"
            label="Sélectionner un document"
            accept=".pdf,.docx,.odt,.txt"
            show-size
            clearable
            :prepend-icon="IconFileUpload"
            :loading="isAnalyzing"
            :disabled="isAnalyzing"
            @update:modelValue="clearAnalysis"
          ></v-file-input>

          <v-alert
            v-if="generationError"
            type="error"
            dense
            class="mt-4"
          >
            {{ generationError }}
          </v-alert>

          <div v-if="analyzedStyleResult" class="mt-4">
            <v-alert
              type="success"
              variant="outlined"
              :icon="IconCircleCheck"
            >
              <p class="font-weight-bold">Style Analysé :</p>
              <p>{{ analyzedStyleResult }}</p>
            </v-alert>
          </div>

          <v-progress-linear
            v-if="isAnalyzing"
            indeterminate
            color="primary"
            class="mt-4"
          ></v-progress-linear>

        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="closeDialog" :disabled="isAnalyzing">
          Fermer
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          @click="analyzeStyle"
          :disabled="!(selectedFile && selectedFile.length > 0) || isAnalyzing || !!analyzedStyleResult"
        >
          <IconSparkles size="20" class="mr-2" />
          Analyser le Style
        </v-btn>
        <v-btn
          color="secondary"
          variant="flat"
          @click="applyStyle"
          :disabled="!analyzedStyleResult || isAnalyzing"
        >
          <IconCheck size="20" class="mr-2" />
          Utiliser ce Style
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import {
  IconFileUpload,
  IconCircleCheck,
  IconSparkles,
  IconCheck
} from '@tabler/icons-vue';
// Importer les composables
import { useAIActions } from '@/composables/useAIActions';
import { useCustomStyle } from '@/composables/useCustomStyle';

const props = defineProps({
  modelValue: Boolean, // Pour v-model
});

const emit = defineEmits(['update:modelValue', 'style-applied']);

const dialog = ref(props.modelValue);
const selectedFile = ref(null); // v-file-input retourne un tableau de File
const analyzedStyleResult = ref(null); // Stockage local du résultat pour l'affichage

// Utiliser les composables
const { analyzeStyleUpload, isAnalyzing, generationError } = useAIActions(ref(null), ref(null));
const { setCustomStyle, activateCustomStyle } = useCustomStyle();

watch(() => props.modelValue, (newValue) => {
  dialog.value = newValue;
  if (newValue) {
    selectedFile.value = null; 
    clearAnalysis();
  }
});

watch(dialog, (newValue) => {
  if (!newValue) {
    emit('update:modelValue', false);
  }
});

const clearAnalysis = () => {
  analyzedStyleResult.value = null;
};

const closeDialog = () => {
  emit('update:modelValue', false);
};

const analyzeStyle = async () => {
  // selectedFile.value est un tableau même pour un seul fichier avec v-file-input
  const fileToUpload = selectedFile.value && selectedFile.value.length > 0 ? selectedFile.value[0] : null;

  if (!fileToUpload) {
    console.warn("StyleAnalysisDialog: No file selected to analyze.");
    // Peut-être afficher une erreur à l'utilisateur ici aussi
    // generationError.value = "Veuillez sélectionner un fichier."; 
    return;
  }
  analyzedStyleResult.value = null; // Effacer l'ancien résultat

  try {
    // Passer le premier fichier du tableau (l'objet File lui-même)
    const result = await analyzeStyleUpload(fileToUpload);
    analyzedStyleResult.value = result; 
  } catch (err) {
    // L'erreur est déjà gérée et stockée dans generationError par le composable useAIActions
    console.error("StyleAnalysisDialog: analysis failed", err);
    // Pas besoin de la redéfinir ici, sauf si on veut un message spécifique au dialogue
  }
};

const applyStyle = () => {
  if (analyzedStyleResult.value) {
    setCustomStyle(analyzedStyleResult.value);
    activateCustomStyle(); 
    console.log("Applying style via composable:", analyzedStyleResult.value);
    emit('style-applied', analyzedStyleResult.value); 
    closeDialog();
  }
};

</script>

<style scoped>
/* Styles spécifiques si nécessaire */
</style>