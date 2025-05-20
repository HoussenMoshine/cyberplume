<template>
  <div class="sticky-action-wrapper">
    <!-- Utilisation de la couleur surface-variant pour le fond du panneau -->
    <v-card flat class="action-panel pa-3" color="surface-variant" rounded="lg">
      <v-card-title class="text-subtitle-1 pa-1 mb-2">Actions IA</v-card-title>
      <!-- Suppression de la v-divider, le fond coloré suffit -->

      <!-- Boutons d'action mis à jour -->
      <v-btn
        @click="$emit('suggest')"
        :disabled="loading"
        :loading="loading && currentAction === 'suggest'"
        color="secondary"
        block
        class="mb-3"
        size="large"  
        title="Générer une suggestion basée sur le contexte actuel"
        variant="elevated" 
      >
        <template v-slot:prepend>
          <IconBulb size="22" class="mr-2"/>
        </template>
        Suggérer
      </v-btn>
      <v-btn
        @click="$emit('continue')"
        :disabled="loading"
        :loading="loading && currentAction === 'continue'"
        color="primary"
        block
        class="mb-3"
        size="large" 
        title="Continuer l'écriture à partir du curseur"
        variant="elevated" 
      >
         <template v-slot:prepend>
           <IconPencilPlus size="22" class="mr-2"/>
         </template>
        Continuer
      </v-btn>
      <v-btn
        @click="$emit('dialogue')"
        :disabled="loading"
        :loading="loading && currentAction === 'dialogue'"
        color="info" 
        block
        class="mb-3"
        size="large" 
        title="Générer un dialogue basé sur la sélection ou le contexte"
        variant="elevated" 
      >
         <template v-slot:prepend>
           <IconMessages size="22" class="mr-2"/>
         </template>
        Dialogue
      </v-btn>
      <!-- TODO: Ajouter d'autres boutons d'action ici si nécessaire -->

      <!-- Bouton Annuler mis à jour -->
      <v-btn
        v-if="loading"
        @click="$emit('cancel')"
        color="error"
        variant="outlined" 
        block
        class="mt-4" 
        size="default" 
        title="Annuler l'action IA en cours"
      >
         <template v-slot:prepend>
           <IconX size="20" class="mr-2"/>
         </template>
        Annuler ({{ currentAction || 'Action IA' }})
      </v-btn>

    </v-card>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
// Import des composants Vuetify utilisés explicitement
import { VCard, VCardTitle, VBtn } from 'vuetify/components';
// Import des icônes Tabler nécessaires
import { IconBulb, IconPencilPlus, IconMessages, IconX } from '@tabler/icons-vue';

// Props pour gérer l'état de chargement global et l'action en cours
const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  currentAction: { // Pour savoir quel bouton afficher en chargement et dans Annuler
    type: String,
    default: null
  }
});

// Définir les événements émis
const emit = defineEmits(['suggest', 'continue', 'dialogue', 'cancel']);
</script>

<style scoped>
.sticky-action-wrapper {
  position: fixed;
  top: 180px;      /* Ajusté : était 100px */
  right: 70px;     /* Valeur initiale, à ajuster après test */
  width: 15%;      /* Ajusté : était 23%. */
  z-index: 10;     /* Valeur initiale, à ajuster si conflits */
  /* background-color: rgba(255,0,0,0.1); */ /* Décommentez pour visualiser la zone */
}

.action-panel {
  /* Suppression de la bordure et du fond spécifiques, gérés par VCard maintenant */
  height: 100%; /* Essayer de prendre la hauteur disponible */
  /* box-shadow: 0 2px 10px rgba(0,0,0,0.2); */ /* Optionnel: ajouter une ombre si le panneau semble flotter bizarrement */
}

/* Suppression du style qui alignait à gauche, pour recentrer */
/* .v-btn {
  justify-content: flex-start; 
  text-transform: none; 
} */

/* Assurer que le texte des boutons n'est pas en majuscules (déjà géré par les defaults Vuetify) */
.v-btn {
  letter-spacing: normal; /* Assurer un espacement normal */
}
</style>