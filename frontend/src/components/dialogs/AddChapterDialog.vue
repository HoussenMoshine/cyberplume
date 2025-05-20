<template>
  <v-dialog :model-value="show" @update:model-value="handleClose" persistent max-width="500px">
    <v-card>
      <v-card-title>
        <span class="text-h5 font-weight-bold" style="font-family: 'Merriweather', serif;">Ajouter un nouveau chapitre</span>
        <span v-if="projectName" class="text-subtitle-1 ml-2">au projet "{{ projectName }}"</span>
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
           :disabled="!internalChapterTitle.trim() || loading"
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
  error: String,
  projectName: String
});
const emit = defineEmits(['close', 'save']);

import { ref, watch } from 'vue';

const internalChapterTitle = ref('');
const localError = ref(null);

watch(() => props.show, (newValue) => {
  if (newValue) {
    internalChapterTitle.value = '';
    localError.value = null;
  }
});
watch(() => props.error, (newError) => {
  localError.value = newError;
});
watch(internalChapterTitle, () => {
  if (localError.value) {
    localError.value = null;
  }
});

function handleClose() {
  if (!props.loading) emit('close');
}
function submit() {
  if (internalChapterTitle.value.trim() && !props.loading) {
    localError.value = null;
    emit('save', internalChapterTitle.value.trim());
  }
}
</script>