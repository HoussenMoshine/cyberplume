# Idées d'Icônes pour CyberPlume (Mise à jour : 17/05/2025)

Ce document recense les icônes existantes, celles intégrées, celles disponibles et les suggestions pour de nouvelles icônes afin d'améliorer l'interface utilisateur de CyberPlume. Toutes les icônes sont prévues au format SVG pour une meilleure scalabilité et personnalisation.

## Icônes Fournies par l'Utilisateur (Initialement)

Liste des icônes présentes dans `frontend/src/assets/` avant la session d'intégration du 17 Mai.

*   **`cyberplume.svg`**: Logo principal de l'application.
    *   *Utilisations suggérées :* Barre de navigation, écran de chargement, page "À propos".
    *   **Statut : [Intégrée le 17/05]** - Barre de navigation ([`App.vue`](frontend/src/App.vue:8)).
*   **`plume.svg`**: Icône alternative ou générique pour l'écriture/édition.
    *   *Utilisations suggérées :* Actions d'édition, identité visuelle secondaire.
*   **`livre.svg`**: Représente un projet ou un livre.
    *   *Utilisations suggérées :* Liste des projets, bouton "Ajouter projet", barre d'outils projet.
*   **`chapitre.svg`**: Représente un chapitre.
    *   *Utilisations suggérées :* Liste des chapitres, bouton "Ajouter chapitre", onglets de chapitre.
*   **`scene.svg`**: Représente une scène.
    *   *Utilisations suggérées :* Liste des scènes, bouton "Ajouter scène" (pour future implémentation).
*   **`personnage.svg`**: Représente un personnage.
    *   *Utilisations suggérées :* Gestionnaire de personnages, fiches personnages, outils liés aux personnages.

*Les icônes suivantes étaient également présentes dans `frontend/src/assets/` et ont été traitées lors de la session du 17 Mai :*

*   **`ajouter.svg`**:
    *   **Statut : [Intégrée le 17/05]** - Bouton "Ajouter Projet" dans [`ProjectToolbar.vue`](frontend/src/components/ProjectToolbar.vue:37) (remplace `IconPlus`).
*   **`editer.svg`**:
    *   **Statut : [Intégrée le 17/05]** - Option "Renommer Projet" dans [`ProjectItem.vue`](frontend/src/components/ProjectItem.vue:45) (remplace `IconPencil`).
*   **`enregistrer.svg`**:
    *   **Statut : [Intégrée le 17/05]** - Bouton "Sauvegarde manuelle" dans [`EditorComponent.vue`](frontend/src/components/EditorComponent.vue:49) (remplace `IconDeviceFloppy`).

## Autres Icônes Disponibles dans `frontend/src/assets/` (État au 17/05/2025)

Ces icônes sont présentes dans le dossier `frontend/src/assets/` mais n'ont pas encore été assignées à une fonctionnalité spécifique ou intégrées. Elles pourront être utilisées lors des prochaines sessions d'amélioration de l'UX :

*   `aide.svg`
*   `assistance-ia.svg`
*   `configuration.svg`
*   `export.svg` (Décision de ne pas l'intégrer pour l'instant le 17/05)
*   `generer-continuer.svg`
*   `glisser-deposer.svg`
*   `graphique-barre.svg`
*   `graphique.svg`
*   `mode-sombre.svg`
*   `poubelle.svg`
*   `raccourcir-etendre.svg`
*   `reformuler.svg`
*   `sans-distraction.svg`

*Note : Les icônes `plume.svg`, `livre.svg`, `chapitre.svg`, `scene.svg`, `personnage.svg` sont listées dans "Icônes Fournies par l'Utilisateur" mais leur intégration effective reste à planifier si elles ne sont pas déjà couvertes par des icônes Tabler existantes.*

## Suggestions de Nouvelles Icônes (Fonctionnalités non encore couvertes par des SVG personnalisés)

### Actions et Fonctionnalités Générales

1.  **Assistance IA (Générique) :** (Voir `assistance-ia.svg` disponible)
    *   *Idées :* Cerveau stylisé, baguette magique, ampoule, étoiles/étincelles.
    *   *Pertinence :* Boutons généraux d'accès aux fonctions IA.

2.  **Actions IA Spécifiques :** (Voir `generer-continuer.svg`, `reformuler.svg`, `raccourcir-etendre.svg` disponibles)
    *   **Générer/Continuer :** Flèche vers la droite, signe "+", document avec étincelle.
    *   **Reformuler :** Deux flèches circulaires, crayon qui édite.
    *   **Raccourcir/Étendre :** Flèches qui se contractent/s'étendent, loupe +/-.
    *   *Pertinence :* Menus contextuels de l'éditeur, panneau d'actions IA.

3.  **Analyse :** (Voir `graphique.svg`, `graphique-barre.svg` disponibles)
    *   *Idées :* Loupe, graphique stylisé, œil.
    *   *Pertinence :* Fonctions d'analyse (cohérence, style, contenu).

4.  **Configuration/Paramètres :** (Voir `configuration.svg` disponible)
    *   *Idées :* Engrenage, curseurs de réglage.
    *   *Pertinence :* Accès aux paramètres.

5.  **Actions CRUD Génériques :**
    *   **Supprimer :** (Voir `poubelle.svg` disponible) Corbeille.
    *   **Réorganiser/Déplacer :** (Voir `glisser-deposer.svg` disponible) Flèches haut/bas, "drag handles".
    *   *Pertinence :* Boutons dans listes, barres d'outils.

6.  **Mode sans Distraction :** (Voir `sans-distraction.svg` disponible)
    *   *Idées :* Œil barré, écran épuré, flèches qui s'étendent.
    *   *Pertinence :* Bouton d'activation/désactivation.

7.  **Tableau de Bord/Statistiques :** (Voir `graphique-barre.svg`, `graphique.svg` disponibles)
    *   *Idées :* Graphique à barres, compteur, icône de "dashboard".
    *   *Pertinence :* Pour un futur tableau de bord détaillé.

8.  **Informations/Aide :** (Voir `aide.svg` disponible)
    *   *Idées :* Point d'interrogation, "i" dans un cercle.
    *   *Pertinence :* Infobulles, accès à l'aide.

9.  **Thème/Apparence :** (Voir `mode-sombre.svg` disponible)
    *   *Idées :* Palette de peintre, soleil/lune (mode sombre/clair).
    *   *Pertinence :* Options de personnalisation du thème.

### Conseils pour la Création
*   **Cohérence Visuelle :** Maintenir un style uniforme (épaisseur de trait, remplissage, niveau de détail).
*   **Simplicité et Reconnaissance :** Privilégier des designs clairs, même à petite taille.
*   **Format SVG :** Continuer avec SVG pour la scalabilité et la personnalisation CSS.