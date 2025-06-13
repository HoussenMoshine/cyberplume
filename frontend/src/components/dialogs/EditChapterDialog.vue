<template>
  <v-dialog :model-value="show" @update:model-value="handleClose" persistent max-width="600px">
    <v-card>
      <v-card-title>
        <span class="text-h5 font-weight-bold" style="font-family: 'Merriweather', serif;">Modifier le chapitre</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-text-field
                label="Titre du chapitre*"
                v-model="internalChapterTitle"
                required
                autofocus
                :error-messages="titleError ? [titleError] : []"
                @keyup.enter="submit"
                :disabled="loading"
                variant="outlined"
                density="compact"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-textarea
                label="Résumé du chapitre"
                v-model="internalChapterSummary"
                :disabled="loading"
                variant="outlined"
                rows="5"
                auto-grow
                hint="Résumé généré ou manuel du contenu du chapitre."
                persistent-hint
              ></v-textarea>
            </v-col>
          </v-row>
        </v-container>
        <small>*champ titre requis</small>
      </v-card-text>
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn
          color="grey-darken-1"
          variant="text"
          @click="handleClose"
          :disabled="loading"
        >
          Annuler
        </v-btn>
        <v-btn
           color="primary"
           variant="flat"
           @click="submit"
           :disabled="!canSubmit"
           :loading="loading"
        >
          Enregistrer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: { // Erreur générale passée par le parent (ex: erreur réseau)
    type: String,
    default: null,
  },
  initialTitle: {
      type: String,
      default: ''
  },
  initialSummary: { // NOUVELLE PROP
      type: String,
      default: ''
  }
});

const emit = defineEmits(['close', 'save']);

const internalChapterTitle = ref('');
const internalChapterSummary = ref(''); // NOUVEAU
const titleError = ref(null); // Erreur spécifique au titre
const generalError = ref(null); // Pour les erreurs venant du parent

// Initialize with initial values when dialog opens or props change
watch(() => props.show, (newValue) => {
  if (newValue) {
    internalChapterTitle.value = props.initialTitle || '';
    internalChapterSummary.value = props.initialSummary || '';
    titleError.value = null;
    generalError.value = props.error; // Synchroniser l'erreur générale
  }
});

watch(() => props.initialTitle, (newVal) => {
    if (props.show) internalChapterTitle.value = newVal || '';
});
watch(() => props.initialSummary, (newVal) => {
    if (props.show) internalChapterSummary.value = newVal || '';
});


watch(() => props.error, (newError) => {
    generalError.value = newError;
});

// Clear title error when user starts typing title
watch(internalChapterTitle, (newVal) => {
    if (titleError.value && newVal.trim()) {
        titleError.value = null;
    }
    // Si l'erreur générale était due au titre vide, on la retire aussi
    if (generalError.value && newVal.trim()) {
        generalError.value = null;
    }
});

const hasChanged = computed(() => {
    const titleChanged = (internalChapterTitle.value || '').trim() !== (props.initialTitle || '').trim();
    const summaryChanged = (internalChapterSummary.value || '').trim() !== (props.initialSummary || '').trim();
    return titleChanged || summaryChanged;
});

const canSubmit = computed(() => {
    return (internalChapterTitle.value || '').trim() && hasChanged.value && !props.loading;
});


const handleClose = () => {
  if (!props.loading) {
    emit('close');
  }
};

const submit = () => {
  const trimmedTitle = (internalChapterTitle.value || '').trim();
  const trimmedSummary = (internalChapterSummary.value || '').trim();

  if (!trimmedTitle) {
      titleError.value = "Le titre ne peut pas être vide.";
      return;
  }
  titleError.value = null; // Clear error if title is not empty

  if (canSubmit.value) { // Utilise la computed property canSubmit
    generalError.value = null;
    emit('save', { 
        title: trimmedTitle, 
        summary: trimmedSummary // Envoyer le résumé même s'il n'a pas changé, le backend gère exclude_unset
    });
  } else if (!hasChanged.value && !props.loading) { 
      // If nothing changed, just close
      handleClose();
  }
};
</script>