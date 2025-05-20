<template>
  <v-list-item
    :key="chapter.id"
    link
    dense
    @click="$emit('select-chapter', chapter.id)"
    :class="{ 'v-list-item--active': isActive }"
    class="ml-4 chapter-list-item"
  >
    <v-list-item-title>{{ chapter.title }}</v-list-item-title>
    <v-list-item-subtitle v-if="chapter.status">Statut: {{ chapter.status }}</v-list-item-subtitle>
  </v-list-item>
</template>

<script setup>
// import { defineProps, defineEmits } from 'vue'; // No longer needed in <script setup>
import { VListItem, VListItemTitle, VListItemSubtitle } from 'vuetify/components';

const props = defineProps({
  chapter: {
    type: Object,
    required: true,
  },
  isActive: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['select-chapter']);

// Log pour voir quand le composant est monté/mis à jour
// import { onMounted, onUpdated } from 'vue';
// onMounted(() => console.log(`DEBUG ChapterListItem MOUNTED: ${props.chapter.id}`));
// onUpdated(() => console.log(`DEBUG ChapterListItem UPDATED: ${props.chapter.id}`));

</script>

<style scoped>
.ml-4 {
  margin-left: 16px !important; /* Conserver l'indentation */
}
.v-list-item--active {
  background-color: rgba(var(--v-theme-primary), 0.1);
  border-left: 3px solid rgb(var(--v-theme-primary));
}
.v-list-item-subtitle {
    font-size: 0.75rem;
    color: grey;
}
</style>