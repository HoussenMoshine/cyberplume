<template>
  <v-list-item
    :key="chapter.id"
    link
    dense
    @click="handleItemClick"
    :class="{ 'v-list-item--active': isActive }"
    class="ml-4 chapter-list-item"
  >
    <v-list-item-title>{{ chapter.title }}</v-list-item-title>
    <v-list-item-subtitle v-if="chapter.status">Statut: {{ chapter.status }}</v-list-item-subtitle>
    <v-list-item-subtitle v-if="chapter.summary" class="summary-preview">
      Résumé: {{ chapter.summary.substring(0, 50) }}{{ chapter.summary.length > 50 ? '...' : '' }}
    </v-list-item-subtitle>
    
    <template v-slot:append>
      <v-tooltip location="top">
        <template v-slot:activator="{ props: tooltipProps }">
          <v-btn
            v-bind="tooltipProps"
            icon
            size="x-small"
            variant="text"
            @click.stop="triggerGenerateSummary"
            :loading="isGeneratingSummary"
            :disabled="isGeneratingSummary"
          >
            <v-icon>mdi-text-box-check-outline</v-icon>
          </v-btn>
        </template>
        <span>{{ chapter.summary ? 'Régénérer le résumé' : 'Générer le résumé' }}</span>
      </v-tooltip>
    </template>
  </v-list-item>
</template>

<script setup>
import { computed } from 'vue';
import { VListItem, VListItemTitle, VListItemSubtitle, VBtn, VIcon, VTooltip } from 'vuetify/components';

const props = defineProps({
  chapter: {
    type: Object,
    required: true,
  },
  isActive: {
    type: Boolean,
    default: false,
  },
  generatingSummaryChapterId: { // ID du chapitre dont le résumé est en cours de génération
    type: [Number, null],
    default: null,
  }
});

const emit = defineEmits(['select-chapter', 'generate-summary']);

const isGeneratingSummary = computed(() => {
  return props.generatingSummaryChapterId === props.chapter.id;
});

const handleItemClick = () => {
  if (!isGeneratingSummary.value) { // Empêcher la sélection si un résumé est en cours de génération pour cet item
    emit('select-chapter', props.chapter.id);
  }
};

const triggerGenerateSummary = () => {
  // console.log(`ChapterListItem: Emitting generate-summary for chapter ${props.chapter.id}`);
  emit('generate-summary', props.chapter.id);
};

</script>

<style scoped>
.ml-4 {
  margin-left: 16px !important; 
}
.v-list-item--active {
  background-color: rgba(var(--v-theme-primary), 0.1);
  border-left: 3px solid rgb(var(--v-theme-primary));
}
.v-list-item-subtitle {
    font-size: 0.75rem;
    color: grey;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px; /* Ajustez selon besoin */
}
.summary-preview {
  margin-top: 2px;
  font-style: italic;
}
</style>