<template>
  <v-dialog :model-value="show" @update:model-value="$emit('close')" persistent max-width="800px">
    <v-card :loading="loading">
      <v-card-title>
        <span class="text-h5 font-weight-bold">Rapport d'Analyse de Cohérence</span>
        <span v-if="analysisResult" class="text-subtitle-1 ml-2">(Projet {{ analysisResult.project_id }})</span>
      </v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" dense class="mb-3">
          {{ error }}
        </v-alert>
        <div v-if="analysisResult && !loading">
          <p><strong>Chapitres analysés :</strong> {{ analysisResult.total_chapters }}</p>
          <p><strong>Mots analysés :</strong> {{ analysisResult.total_words }}</p>
          <v-divider class="my-3"></v-divider>

          <h3 class="mb-2 text-h6">Entités Nommées Détectées :</h3>
          <v-list density="compact" v-if="analysisResult.entities.length > 0">
            <template v-for="(group, label) in groupedEntities" :key="label">
              <v-list-group v-if="group.length > 0" :value="label">
                <template v-slot:activator="{ props: activatorProps }">
                  <v-list-item
                    v-bind="activatorProps"
                    :title="getGroupTitle(label) + ` (${group.length})`"
                  >
                    <template v-slot:prepend>
                      <component :is="getGroupIcon(label)" class="mr-3" size="20" />
                    </template>
                  </v-list-item>
                </template>
                <v-list-item v-for="(entity, index) in group" :key="`${label}-${index}`" density="compact">
                  <v-list-item-title class="pl-4">{{ entity.text }}</v-list-item-title>
                  <template v-slot:append>
                    <v-chip size="small">{{ entity.count }}</v-chip>
                  </template>
                </v-list-item>
              </v-list-group>
            </template>
          </v-list>
          <p v-else class="text-grey">Aucune entité pertinente détectée.</p>

          <v-divider class="my-3" v-if="analysisResult.warnings.length > 0"></v-divider>
          <h3 class="mb-2 text-h6" v-if="analysisResult.warnings.length > 0">Avertissements :</h3>
          <v-alert type="warning" density="compact" v-for="(warning, index) in analysisResult.warnings" :key="`warn-${index}`" class="mb-2">
            {{ warning }}
          </v-alert>
        </div>
        <div v-if="loading">
          <p class="text-center">Analyse en cours...</p>
        </div>
      </v-card-text>
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn color="grey darken-1" variant="text" @click="$emit('close')">
          Fermer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue';
import { IconUsersGroup, IconMapPin, IconBuildingCommunity, IconTag } from '@tabler/icons-vue';
import { VDialog, VCard, VCardTitle, VCardText, VCardActions, VBtn, VSpacer, VAlert, VList, VListItem, VListGroup, VListItemTitle, VDivider, VChip } from 'vuetify/components';


const props = defineProps({
  show: Boolean,
  loading: Boolean,
  error: String,
  analysisResult: { // { project_id, total_chapters, total_words, entities: [{text, label, count}], warnings: [] }
    type: Object,
    default: null
  }
});

defineEmits(['close']);

const groupedEntities = computed(() => {
  if (!props.analysisResult || !props.analysisResult.entities) {
    return {};
  }
  const groups = { PER: [], LOC: [], ORG: [], MISC: [] };
  props.analysisResult.entities.forEach(entity => {
    if (groups[entity.label]) {
      groups[entity.label].push(entity);
    } else {
      groups.MISC.push(entity);
    }
  });
  Object.values(groups).forEach(group => group.sort((a, b) => b.count - a.count));
  return groups;
});

const getGroupTitle = (label) => ({ PER: 'Personnages', LOC: 'Lieux', ORG: 'Organisations' }[label] || 'Autres');
const getGroupIcon = (label) => {
  switch (label) {
    case 'PER': return IconUsersGroup;
    case 'LOC': return IconMapPin;
    case 'ORG': return IconBuildingCommunity;
    default: return IconTag;
  }
};

</script>

<style scoped>
.text-grey { color: grey; }
.v-list-group .v-list-item { padding-inline-start: calc(16px + var(--v-list-group-header-indent)) !important; }
.v-list-item .v-chip { margin-right: 8px; }
h3 { margin-bottom: 0.5rem; } /* Maintenu, mais la classe text-h6 devrait gérer cela */
</style>