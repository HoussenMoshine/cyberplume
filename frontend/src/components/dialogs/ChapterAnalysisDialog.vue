<template>
  <v-dialog :model-value="show" @update:model-value="$emit('close')" max-width="800px" persistent scrollable>
    <v-card>
      <v-card-title class="headline text-h5 font-weight-bold">
        Analyse du Contenu : {{ chapterTitle }}
      </v-card-title>

      <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>

      <v-card-text style="max-height: 70vh;">
        <v-alert v-if="error" type="error" density="compact" variant="tonal" class="mb-4">
          {{ error }}
        </v-alert>

        <div v-if="analysisResult && !loading && !error">
          <!-- Section Statistiques -->
          <h3 class="text-h6 mb-2">Statistiques</h3>
          <v-row dense>
            <v-col cols="12" sm="6" v-if="analysisResult.stats && analysisResult.stats.word_count !== null && analysisResult.stats.word_count !== undefined">
              <v-list-item density="compact">
                <template v-slot:prepend>
                  <IconListNumbers class="mr-2" size="20" />
                </template>
                <v-list-item-title>Nombre de mots</v-list-item-title>
                <v-list-item-subtitle>{{ analysisResult.stats.word_count }}</v-list-item-subtitle>
              </v-list-item>
            </v-col>
            <v-col cols="12" sm="6" v-if="analysisResult.stats && analysisResult.stats.character_count !== null && analysisResult.stats.character_count !== undefined">
              <v-list-item density="compact">
                 <template v-slot:prepend>
                   <IconAbc class="mr-2" size="20" />
                 </template>
                <v-list-item-title>Nombre de caractères</v-list-item-title>
                <v-list-item-subtitle>{{ analysisResult.stats.character_count }}</v-list-item-subtitle>
              </v-list-item>
            </v-col>
             <v-col cols="12" sm="6" v-if="analysisResult.stats && analysisResult.stats.sentence_count !== null && analysisResult.stats.sentence_count !== undefined">
               <v-list-item density="compact">
                 <template v-slot:prepend>
                   <IconPilcrow class="mr-2" size="20" />
                 </template>
                 <v-list-item-title>Nombre de phrases</v-list-item-title>
                 <v-list-item-subtitle>{{ analysisResult.stats.sentence_count }}</v-list-item-subtitle>
               </v-list-item>
             </v-col>
             <v-col cols="12" sm="6" v-if="analysisResult.stats && analysisResult.stats.readability_score !== null && analysisResult.stats.readability_score !== undefined">
               <v-list-item density="compact">
                 <template v-slot:prepend>
                   <IconBook class="mr-2" size="20" />
                 </template>
                 <v-list-item-title>Score de lisibilité</v-list-item-title>
                 <v-list-item-subtitle>{{ analysisResult.stats.readability_score.toFixed(2) }}</v-list-item-subtitle>
               </v-list-item>
             </v-col>
             <v-col cols="12" sm="6" v-if="analysisResult.stats && analysisResult.stats.estimated_reading_time_minutes !== null && analysisResult.stats.estimated_reading_time_minutes !== undefined">
               <v-list-item density="compact">
                 <template v-slot:prepend>
                   <IconClockHour8 class="mr-2" size="20" />
                 </template>
                 <v-list-item-title>Temps de lecture estimé</v-list-item-title>
                 <v-list-item-subtitle>{{ analysisResult.stats.estimated_reading_time_minutes.toFixed(1) }} min</v-list-item-subtitle>
               </v-list-item>
             </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <!-- Section Suggestions -->
          <h3 class="text-h6 mb-3">Suggestions d'Amélioration</h3>

          <!-- Filtres et Tri -->
          <v-row dense class="mb-4" v-if="analysisResult && analysisResult.suggestions && analysisResult.suggestions.length > 0">
            <v-col cols="12" md="8">
              <span class="text-caption mr-2">Filtrer par type:</span>
              <v-chip-group
                v-model="selectedSuggestionTypes"
                multiple
                column
                class="d-inline-block"
              >
                <v-chip
                  v-for="type in availableSuggestionTypes"
                  :key="type"
                  :value="type"
                  :color="getSuggestionColor(type)"
                  filter
                  size="small"
                  label
                >
                  {{ type }}
                </v-chip>
              </v-chip-group>
            </v-col>
            <v-col cols="12" md="4">
               <v-select
                 v-model="selectedSortOption"
                 :items="sortOptions"
                 label="Trier par"
                 density="compact"
                 hide-details
                 variant="outlined"
                 class="mt-n2"
               ></v-select>
            </v-col>
          </v-row>

          <div v-if="filteredAndSortedSuggestions && filteredAndSortedSuggestions.length > 0">
            <v-card
              v-for="(suggestion, index) in filteredAndSortedSuggestions"
              :key="index"
              class="mb-3"
              variant="outlined"
            >
              <v-card-text>
                <div class="d-flex align-center mb-2">
                   <v-chip :color="getSuggestionColor(suggestion.suggestion_type)" size="small" label class="mr-2">
                     {{ suggestion.suggestion_type }}
                   </v-chip>
                   <span class="text-caption text-disabled">Original (Indices: {{ suggestion.start_index }} - {{ suggestion.end_index }}) :</span>
                </div>
                <p class="text-body-2 font-italic mb-2" style="color: rgba(var(--v-theme-on-surface), 0.6);">"{{ suggestion.original_text }}"</p>

                <div class="d-flex align-center mb-2">
                   <IconArrowRightRhombus color="success" class="mr-1" size="16" />
                   <span class="text-caption text-disabled">Suggestion :</span>
                </div>
                <p class="text-body-2 font-weight-medium mb-3" style="color: rgb(var(--v-theme-success));">"{{ suggestion.suggested_text }}"</p>

                <p v-if="suggestion.explanation" class="text-caption">
                  <IconInfoCircle size="12" class="mr-1" />
                  {{ suggestion.explanation }}
                </p>
              </v-card-text>
               <!-- AJOUT: Bouton Appliquer -->
               <v-card-actions class="px-2 pb-2">
                 <v-spacer></v-spacer>
                 <!-- <v-btn size="small" variant="text">Ignorer</v-btn> -->
                 <v-btn
                   size="small"
                   color="primary"
                   variant="tonal"
                   @click="applySuggestion(suggestion)"
                 >
                   <template v-slot:prepend>
                     <IconCheck size="16" />
                   </template>
                   Appliquer
                 </v-btn>
               </v-card-actions>
            </v-card>
          </div>
          <p v-else-if="analysisResult && analysisResult.suggestions && analysisResult.suggestions.length > 0" class="text-body-2 text-disabled font-italic">
            Aucune suggestion ne correspond aux filtres sélectionnés.
          </p>
          <p v-else class="text-body-2 text-disabled font-italic">
             Aucune suggestion d'amélioration spécifique trouvée.
          </p>
        </div>

        <div v-if="!analysisResult && !loading && !error" class="text-center text-disabled font-italic mt-4">
            Aucune donnée d'analyse disponible.
        </div>

      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="$emit('close')">Fermer</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { defineProps, defineEmits, computed, ref } from 'vue';
import {
  IconListNumbers, IconAbc, IconPilcrow, IconBook, IconClockHour8,
  IconArrowRightRhombus, IconInfoCircle, IconCheck
} from '@tabler/icons-vue';
import {
  VDialog, VCard, VCardTitle, VCardText, VCardActions, VBtn, VSpacer,
  VProgressLinear, VAlert, VRow, VCol, VList, VListItem, VListItemTitle, VListItemSubtitle,
  VIcon, VDivider, VChip, VChipGroup, VSelect
} from 'vuetify/components';

const props = defineProps({
  show: Boolean,
  loading: Boolean,
  error: String,
  analysisResult: Object, // { chapter_id, stats: {...}, suggestions: [...] }
  chapterTitle: String,
});

// AJOUT: Définir l'événement 'apply-suggestion'
const emit = defineEmits(['close', 'apply-suggestion']);

// --- Filtres et Tri ---
const selectedSuggestionTypes = ref([]); // Types sélectionnés pour le filtre
const selectedSortOption = ref('position'); // Option de tri ('position' ou 'type')

// Déclaration manquante pour les options de tri
const sortOptions = ref([
  { title: 'Position dans le texte', value: 'position' },
  { title: 'Type de suggestion', value: 'type' },
]);

const availableSuggestionTypes = computed(() => {
  if (!props.analysisResult || !props.analysisResult.suggestions) return [];
  const types = new Set(props.analysisResult.suggestions.map(s => s.suggestion_type));
  return Array.from(types);
});

const filteredAndSortedSuggestions = computed(() => {
  if (!props.analysisResult || !props.analysisResult.suggestions) return [];

  let suggestions = [...props.analysisResult.suggestions];

  // Filtrage
  if (selectedSuggestionTypes.value.length > 0) {
    suggestions = suggestions.filter(s => selectedSuggestionTypes.value.includes(s.suggestion_type));
  }

  // Tri
  if (selectedSortOption.value === 'type') {
    suggestions.sort((a, b) => a.suggestion_type.localeCompare(b.suggestion_type));
  } else { // 'position'
    suggestions.sort((a, b) => a.start_index - b.start_index);
  }

  return suggestions;
});

const getSuggestionColor = (type) => {
  switch (type) {
    case 'Grammaire': return 'blue';
    case 'Style': return 'purple';
    case 'Orthographe': return 'red';
    case 'Clarté': return 'green';
    case 'Incohérence': return 'orange';
    default: return 'grey';
  }
};

// AJOUT: Fonction pour émettre l'événement d'application
const applySuggestion = (suggestion) => {
  emit('apply-suggestion', suggestion);
};

</script>

<style scoped>
.headline {
  background-color: #f5f5f5;
  color: #333;
  padding: 16px 24px;
  border-bottom: 1px solid #ddd;
}
</style>