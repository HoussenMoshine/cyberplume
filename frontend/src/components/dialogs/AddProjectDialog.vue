<template>
  <v-dialog :model-value="show" @update:model-value="handleClose" persistent max-width="500px">
    <v-card>
      <v-card-title>
        <span class="text-h5 font-weight-bold" style="font-family: 'Merriweather', serif;">Ajouter un nouveau projet</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-text-field
                label="Titre du projet*"
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
          Ajouter
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const props = defineProps({
  show: Boolean,
  loading: Boolean,
  error: String
});
const emit = defineEmits(['close', 'save']);

import { ref, watch } from 'vue';

const internalProjectTitle = ref('');
const localError = ref(null);

watch(() => props.show, (newValue) => {
  if (newValue) {
    internalProjectTitle.value = '';
    localError.value = null;
  }
});
watch(() => props.error, (newError) => {
  localError.value = newError;
});
watch(internalProjectTitle, () => {
  if (localError.value) {
    localError.value = null;
  }
});

function handleClose() {
  if (!props.loading) emit('close');
}
function submit() {
  if (internalProjectTitle.value.trim() && !props.loading) {
    localError.value = null;
    emit('save', { title: internalProjectTitle.value.trim() });
  }
}
</script>