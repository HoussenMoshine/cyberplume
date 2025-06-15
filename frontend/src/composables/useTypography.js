import { ref, watch } from 'vue';

// Valeur par défaut si rien n'est dans le localStorage
const DEFAULT_FONT_SIZE = 16; // en pixels

// Clé pour le localStorage
const FONT_SIZE_STORAGE_KEY = 'cyberplume_font_size';

// État global réactif pour la taille de la police
const fontSize = ref(DEFAULT_FONT_SIZE);

// Charger la valeur depuis le localStorage au démarrage
const savedSize = localStorage.getItem(FONT_SIZE_STORAGE_KEY);
if (savedSize) {
  fontSize.value = JSON.parse(savedSize);
}

// Surveiller les changements et sauvegarder dans le localStorage
watch(fontSize, (newSize) => {
  localStorage.setItem(FONT_SIZE_STORAGE_KEY, JSON.stringify(newSize));
}, { deep: true });

/**
 * Composable pour gérer les paramètres de typographie globaux.
 * @returns {{fontSize: import('vue').Ref<number>}}
 */
export function useTypography() {
  return {
    fontSize,
  };
}