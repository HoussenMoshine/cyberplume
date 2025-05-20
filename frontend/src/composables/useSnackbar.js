// frontend/src/composables/useSnackbar.js
import { ref } from 'vue';

export function useSnackbar() {
  const showSnackbar = ref(false);
  const snackbarMessage = ref('');
  const snackbarColor = ref('info'); // Default color
  const snackbarTimeout = ref(3000); // Default timeout

  const displaySnackbar = (message, color = 'info', timeout = 3000) => {
    snackbarMessage.value = message;
    snackbarColor.value = color;
    snackbarTimeout.value = timeout;
    showSnackbar.value = true;
  };

  // Retourner les refs et la fonction pour être utilisés par les composants
  // Note: showSnackbar est retourné pour être utilisé avec v-model sur VSnackbar
  return {
    showSnackbar,
    snackbarMessage,
    snackbarColor,
    snackbarTimeout,
    displaySnackbar // La fonction pour déclencher l'affichage
  };
}