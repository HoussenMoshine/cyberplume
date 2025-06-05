import { ref } from 'vue';
import axios from 'axios';
import { useSnackbar } from '@/composables/useSnackbar'; // Assurez-vous que le chemin est correct

export function useSceneIdeas() {
    const isLoading = ref(false);
    const generatedIdeas = ref([]);
    const error = ref(null);
    // Correction: utiliser displaySnackbar et le renommer en showSnackbar pour l'appel local si souhaité,
    // ou utiliser directement displaySnackbar. Ici, nous allons le renommer pour minimiser les changements dans le reste du fichier.
    const { displaySnackbar: showSnackbar } = useSnackbar(); // Renommer displaySnackbar en showSnackbar localement

    const VITE_API_URL = import.meta.env.VITE_API_URL || '/api';
    const VITE_API_KEY = import.meta.env.VITE_API_KEY;

    async function generateIdeas(requestData) {
        isLoading.value = true;
        generatedIdeas.value = [];
        error.value = null;

        try {
            const response = await axios.post(
                `${VITE_API_URL}/ideas/scene/generate`,
                requestData,
                {
                    headers: {
                        'X-API-Key': VITE_API_KEY,
                        'Content-Type': 'application/json',
                    },
                }
            );

            if (response.data && response.data.ideas) {
                generatedIdeas.value = response.data.ideas;
                if (generatedIdeas.value.length === 0) {
                    showSnackbar('Aucune idée n\'a été générée.', 'info');
                }
            } else {
                throw new Error("Réponse invalide du serveur pour la génération d'idées.");
            }
        } catch (err) {
            console.error("Erreur lors de la génération d'idées de scènes:", err);
            let errorMessage = "Une erreur est survenue lors de la génération des idées.";
            if (err.response && err.response.data && err.response.data.detail) {
                errorMessage = err.response.data.detail;
            } else if (err.message) {
                errorMessage = err.message;
            }
            error.value = errorMessage;
            showSnackbar(errorMessage, 'error');
            generatedIdeas.value = []; // S'assurer que les idées sont vides en cas d'erreur
        } finally {
            isLoading.value = false;
        }
    }

    function copyToClipboard(textToCopy) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    showSnackbar('Idée copiée dans le presse-papiers !', 'success');
                })
                .catch(err => {
                    console.error('Erreur lors de la copie dans le presse-papiers:', err);
                    showSnackbar('Erreur lors de la copie.', 'error');
                    // Fallback pour les navigateurs non sécurisés ou sans API clipboard (moins probable avec les navigateurs modernes)
                    fallbackCopyToClipboard(textToCopy);
                });
        } else {
            // Fallback pour HTTP ou contextes non sécurisés
            fallbackCopyToClipboard(textToCopy);
        }
    }

    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed'; // Empêche le défilement en haut de la page
        textArea.style.left = '-9999px'; // Déplace hors de l'écran
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showSnackbar('Idée copiée (fallback) !', 'success');
            } else {
                showSnackbar('La copie (fallback) a échoué.', 'error');
            }
        } catch (err) {
            console.error('Erreur lors du fallback de copie:', err);
            showSnackbar('Erreur lors de la copie (fallback).', 'error');
        }
        document.body.removeChild(textArea);
    }


    return {
        isLoading,
        generatedIdeas,
        error,
        generateIdeas,
        copyToClipboard,
    };
}