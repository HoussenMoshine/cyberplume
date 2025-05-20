<template>
  <v-dialog :model-value="show" @update:model-value="handleClose" persistent max-width="500px">
    <v-card>
      <v-card-title>
        <span class="text-h5 font-weight-bold" style="font-family: 'Merriweather', serif;">Renommer le projet</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-text-field
                label="Nouveau titre du projet*"
                v-model="internalProjectTitle"
                required
                autofocus
                :error-messages="localError ? [localError] : []"
                @keyup.enter="submit"
                :disabled="loading"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-container>
        <small>*champ requis</small>
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
           :disabled="!internalProjectTitle.trim() || loading"
           :loading="loading"
        >
          Enregistrer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
  initialTitle: {
      type: String,
      default: ''
  }
});

const emit = defineEmits(['close', 'save']);

const internalProjectTitle = ref('');
const localError = ref(null);

// Initialize with initialTitle when dialog opens
watch(() => props.show, (newValue) => {
  if (newValue) {
    internalProjectTitle.value = props.initialTitle;
    localError.value = null;
  }
});

watch(() => props.error, (newError) => {
    localError.value = newError;
});

// Clear local error when user starts typing
watch(internalProjectTitle, () => {
    if (localError.value) {
        localError.value = null;
    }
});

const handleClose = () => {
  if (!props.loading) {
    emit('close');
  }
};

const submit = () => {
  // Only emit save if title has changed and is not empty
  if (internalProjectTitle.value.trim() && internalProjectTitle.value.trim() !== props.initialTitle && !props.loading) {
    localError.value = null;
    emit('save', internalProjectTitle.value.trim());
  } else if (internalProjectTitle.value.trim() === props.initialTitle && !props.loading) {
      // If title hasn't changed, just close the dialog
      handleClose();
  }
};
</script>