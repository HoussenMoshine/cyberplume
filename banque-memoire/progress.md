# Progression - CyberPlume (Mise à jour : 14/06/2025 - 09:27)

## Ce qui Fonctionne (État Actuel)

*   **Démarrage Application & Logging :** Stables.
*   **Gestion des Projets (CRUD) :** Entièrement fonctionnel.
*   **Gestion des Chapitres (CRUD) :** Entièrement fonctionnel.
*   **Affichage de la liste des chapitres :** Fonctionnel.
*   **Éditeur de texte :** Fonctionnalité de base restaurée.
*   **Sauvegarde et chargement des chapitres :** Le flux "Data Airlock" est en place.
*   **Génération de résumé de chapitre :** Fonctionnel. Utilise le fournisseur et le modèle IA sélectionnés.
*   **Collage de texte dans l'éditeur :** **CORRIGÉ**. Les sauts de ligne sont désormais correctement préservés.
*   **Stabilité Générale :** L'application est dans un état stable.

## Ce qui Reste à Construire / Améliorer

*   **Fonctionnalités futures :** Reprendre le développement des fonctionnalités prévues au `projectbrief.md`.

## Évolution des Décisions

### Session 14 Juin (Après-midi - Branche `fix-paste-bug`)
*   **Objectif :** Corriger le bug de collage dans l'éditeur TipTap.
*   **Actions Clés :**
    1.  **Première Tentative (Échec) :** Utilisation de `transformPastedText` pour convertir les sauts de ligne en HTML. A échoué car la fonction retourne du texte brut et non du HTML interprétable, causant l'affichage de balises `<p>` dans l'éditeur.
    2.  **Seconde Tentative (Succès) :** Réécriture de la logique `handlePaste`. La nouvelle approche utilise l'API de transaction de Prosemirror (`tr.split`, `tr.insertText`) pour diviser le texte collé en lignes et insérer chaque ligne dans un nouveau paragraphe de manière programmatique.
*   **Résultat :** Succès. Le bug de collage est résolu de manière robuste. La session se termine sur cette correction.

### Session 14 Juin (Matin - Branche `resume-chapitre`)
*   **Objectif :** Corriger le bug de sélection du modèle IA pour les résumés et le bug de collage dans l'éditeur.
*   **Actions Clés :**
    1.  **Résumé IA (Succès) :** Le problème a été tracé à une valeur codée en dur dans le backend (`summary_service.py`). Le flux de données a été corrigé de bout en bout.
    2.  **Bug de Collage (Échec Initial) :** Une première tentative de correction via `handlePaste` s'est avérée inefficace.
*   **Résultat :** Succès partiel. La fonctionnalité de résumé a été corrigée, mais le bug de l'éditeur persistait.

### Session 13 Juin (Matin - Correction Finale Suppression)
*   **Objectif :** Corriger les bugs persistants de suppression simple et multiple.
*   **Résultat :** Succès. Le problème de réactivité a été résolu avec une `computed property`.

### Sessions Antérieures
*   Focalisées sur la réparation de régressions et la stabilisation des fonctionnalités de base (CRUD, etc.).