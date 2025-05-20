<template>
  <v-dialog :model-value="show" @update:model-value="$emit('close')" persistent max-width="500px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Modifier la Scène</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-form ref="form" @submit.prevent="saveScene">
            <v-text-field
              v-model="editableTitle"
              label="Nouveau Titre de la Scène*"
              :rules="[rules.required]"
              required
              autofocus
              @keydown.enter="saveScene"
            ></v-text-field>
            <!-- Optionnel: Champ pour l'ordre -->
            <v-text-field
              v-model.number="editableOrder"
              label="Ordre"
              type="number"
              min="0"
              hint="Ordre d'affichage dans le chapitre"
              persistent-hint
            ></v-text-field>
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
          Enregistrer
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
  initialTitle: { type: String, default: '' },
  initialOrder: { type: Number, default: 0 }
});

const emit = defineEmits(['close', 'save']);

const form = ref(null);
const editableTitle = ref('');
const editableOrder = ref(0);

const rules = {
  required: value => !!value || 'Ce champ est requis.',
};

// Update local state when props change (dialog opens)
watch(() => props.show, (newValue) => {
  if (newValue) {
    editableTitle.value = props.initialTitle;
    editableOrder.value = props.initialOrder;
    // Reset validation if form exists
    // setTimeout(() => form.value?.resetValidation(), 100);
  }
}, { immediate: true }); // immediate: true to set initial values

const isFormValid = computed(() => {
  return !!editableTitle.value; // Title is required
});

const closeDialog = () => {
  emit('close');
};

const saveScene = async () => {
  const { valid } = await form.value?.validate();
  if (!valid) return;

  const sceneUpdateData = {
    title: editableTitle.value,
    order: editableOrder.value,
  };
  // Only emit if changes were made? Optional optimization.
  // if (editableTitle.value !== props.initialTitle || editableOrder.value !== props.initialOrder) {
     emit('save', sceneUpdateData);
  // } else {
  //   closeDialog(); // Close if no changes
  // }
};
</script>