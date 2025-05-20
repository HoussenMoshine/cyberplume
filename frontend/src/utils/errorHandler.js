// frontend/src/utils/errorHandler.js

/**
 * Gère les erreurs survenues lors des appels API et retourne un message formaté pour l'utilisateur.
 * @param {Error|object} error - L'objet d'erreur capturé. Il peut s'agir d'une instance d'Error ou d'un objet d'erreur Axios/fetch.
 * @param {string} context - Contexte de l'erreur (ex: 'chargement des modèles', 'génération de texte').
 * @returns {string} Un message d'erreur formaté et compréhensible par l'utilisateur.
 */
export function handleApiError(error, context = 'opération') {
  console.error(`Erreur pendant ${context}:`, error); // Log détaillé pour le débogage

  let userMessage = `Une erreur est survenue pendant ${context}.`;

  if (error.response) {
    // Erreur de réponse de l'API (statut hors 2xx)
    const status = error.response.status;
    const data = error.response.data;
    userMessage = `Erreur ${status} pendant ${context}: ${data?.detail || error.message || 'Erreur serveur inconnue'}.`;
    if (status === 401) {
      userMessage = `Erreur d'authentification (${status}) pendant ${context}. Vérifiez votre clé API.`;
    } else if (status === 400) {
      userMessage = `Erreur de requête (${status}) pendant ${context}: ${data?.detail || 'Vérifiez les paramètres envoyés.'}`;
    } else if (status >= 500) {
      userMessage = `Erreur serveur (${status}) pendant ${context}. Le serveur rencontre peut-être des difficultés. Réessayez plus tard.`;
    }
  } else if (error.request) {
    // La requête a été faite mais aucune réponse n'a été reçue
    userMessage = `Impossible de contacter le serveur pendant ${context}. Vérifiez votre connexion réseau et l'état du serveur backend.`;
  } else if (error.message) {
    // Erreur lors de la configuration de la requête ou autre erreur JS
    userMessage = `Erreur de configuration ou interne pendant ${context}: ${error.message}.`;
  }

  return userMessage;
}