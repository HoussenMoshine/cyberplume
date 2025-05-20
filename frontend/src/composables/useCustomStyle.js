import { ref, computed } from 'vue';

// État global (module scope) pour le style personnalisé
const customStyleDescription = ref(null);
const isCustomStyleActive = ref(false);

/**
 * Composable pour gérer l'état du style d'écriture personnalisé analysé.
 */
export function useCustomStyle() {

  /**
   * Définit la description du style personnalisé analysé.
   * L'activation se fait séparément via `activateCustomStyle`.
   * @param {string|null} description - La description du style ou null pour effacer.
   */
  const setCustomStyle = (description) => {
    customStyleDescription.value = description;
    // Ne pas activer automatiquement, laisser l'utilisateur choisir
    // isCustomStyleActive.value = !!description;
    console.log("Custom style description set:", description);
  };

  /**
   * Active l'utilisation du style personnalisé pour les prochaines générations.
   * Ne fonctionne que si une description de style a été définie.
   */
  const activateCustomStyle = () => {
    if (customStyleDescription.value) {
      isCustomStyleActive.value = true;
      console.log("Custom style activated.");
    } else {
      console.warn("Cannot activate custom style: No description available.");
    }
  };

  /**
   * Désactive l'utilisation du style personnalisé.
   */
  const deactivateCustomStyle = () => {
    isCustomStyleActive.value = false;
    console.log("Custom style deactivated.");
  };

  /**
   * Efface la description du style personnalisé et le désactive.
   */
  const clearCustomStyle = () => {
    customStyleDescription.value = null;
    isCustomStyleActive.value = false;
    console.log("Custom style cleared and deactivated.");
  };

  // Propriété calculée pour obtenir la description actuelle (utile pour l'API)
  const activeCustomStyleDescription = computed(() => {
    return isCustomStyleActive.value ? customStyleDescription.value : null;
  });

  return {
    // State (lecture seule depuis l'extérieur recommandé)
    customStyleDescription: computed(() => customStyleDescription.value),
    isCustomStyleActive: computed(() => isCustomStyleActive.value),
    activeCustomStyleDescription,

    // Actions
    setCustomStyle,
    activateCustomStyle,
    deactivateCustomStyle,
    clearCustomStyle,
  };
}

// Export direct pour une utilisation simple si nécessaire (moins courant avec les composables)
// export default useCustomStyle;