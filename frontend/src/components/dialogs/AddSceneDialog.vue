<template>
  <v-dialog :model-value="show" @update:model-value="$emit('close')" persistent max-width="500px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Ajouter une Scène à "{{ chapterTitle }}"</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-form ref="form" @submit.prevent="saveScene">
            <v-text-field
              v-model="sceneTitle"
              label="Titre de la Scène*"
              :rules="[rules.required]"
              required
              autofocus
              
            ></v-text-field> <!-- Suppression de @keydown.enter="saveScene" -->
            <!-- Optionnel: Champ pour l'ordre ? Pour l'instant, l'ordre est géré automatiquement -->
            <!-- <v-text-field
              v-model.number="sceneOrder"
              label="Ordre (Optionnel)"
              type="number"
              min="0"
            ></v-text-field> -->
            <v-alert v-if="error" type="error" density="compact" class="mt-2">
              {{ error }}
            </v-alert>
          </v-form>
        </v-container>
        <small>*champ requis</small>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey darken-1" text @click="closeDialog" :disabled="loading">
          Annuler
        </v-btn>
        <v-btn
          color="teal"
          @click="saveScene"
          :loading="loading"
          :disabled="!isFormValid"
        >
          Ajouter Scène
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  show: Boolean,
  loading: Boolean,
  error: String,
  chapterTitle: { type: String, default: 'Chapitre' }
});

const emit = defineEmits(['close', 'save']);

const form = ref(null);
const sceneTitle = ref('');
// const sceneOrder = ref(null); // Si on ajoute le champ ordre

const rules = {
  required: value => !!value || 'Ce champ est requis.',
};

// Reset form when dialog opens
watch(() => props.show, (newValue) => {
  if (newValue) {
    sceneTitle.value = '';
    // sceneOrder.value = null;
    // Reset validation if form exists
    // setTimeout(() => form.value?.resetValidation(), 100); // Delay needed?
  }
});

const isFormValid = computed(() => {
  // Basic check, Vuetify's form validation handles the rules
  return !!sceneTitle.value;
});

const closeDialog = () => {
  emit('close');
};

const saveScene = async () => {
  // Validate form using Vuetify's built-in validation
  const { valid } = await form.value?.validate();
  if (!valid) return;

  const sceneData = {
    title: sceneTitle.value,
    // order: sceneOrder.value // Inclure si le champ est ajouté
  };
  emit('save', sceneData);
};
</script>