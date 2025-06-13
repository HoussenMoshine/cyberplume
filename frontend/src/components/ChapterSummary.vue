<template>
  <div v-if="summary" class="summary-container mt-4">
    <div class="d-flex align-center mb-2">
      <h3 class="summary-title">Résumé du Chapitre</h3>
      <v-spacer></v-spacer>
      <v-tooltip location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            variant="text"
            size="x-small"
            @click="$emit('refresh-summary')"
            v-bind="props"
          >
            <v-icon>mdi-refresh</v-icon>
          </v-btn>
        </template>
        <span>Rafraîchir le résumé</span>
      </v-tooltip>
    </div>
    <v-textarea
      :model-value="summary"
      readonly
      auto-grow
      rows="3"
      variant="outlined"
      class="summary-content"
    ></v-textarea>
    <v-btn
      @click="copySummary"
      color="primary"
      variant="tonal"
      size="small"
      class="copy-button"
    >
      <v-icon left>mdi-content-copy</v-icon>
      Copier le résumé
    </v-btn>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';

const props = defineProps({
  summary: {
    type: String,
    default: null,
  },
});

const emit = defineEmits(['refresh-summary']);

const { showSnackbar } = useSnackbar();

const copySummary = async () => {
  if (!props.summary) return;
  try {
    await navigator.clipboard.writeText(props.summary);
    showSnackbar('Résumé copié dans le presse-papiers.', 'success');
  } catch (err) {
    console.error('Erreur lors de la copie du résumé: ', err);
    showSnackbar('Impossible de copier le résumé.', 'error');
  }
};
</script>

<style scoped>
.summary-container {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  padding-top: 16px;
}

.summary-title {
  font-size: 1rem;
  font-weight: 500;
  color: #424242;
}

.summary-content {
  font-size: 0.9rem;
  line-height: 1.5;
}

.copy-button {
  margin-top: 8px;
}
</style>