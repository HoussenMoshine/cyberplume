# Contexte Produit - CyberPlume

## Raison d'être et Problème Résolu

L'écriture créative, en particulier pour des projets longs comme des romans, implique souvent de jongler entre l'édition de texte, l'organisation des idées (intrigue, personnages, lieux), la recherche et parfois l'utilisation d'outils d'assistance. CyberPlume vise à **centraliser ces activités** dans une application de bureau unique et cohérente.

Le problème principal résolu est la **fragmentation des outils et la friction** associée au passage de l'un à l'autre. CyberPlume cherche à offrir un environnement intégré où l'écriture, l'organisation structurelle (projets, chapitres, scènes), la gestion des éléments narratifs (personnages) et l'assistance intelligente coexistent harmonieusement. L'intégration de l'IA vise à surmonter le blocage de l'écrivain, à accélérer certaines tâches répétitives (reformulation, expansion) et à stimuler la créativité (génération d'idées, de dialogues).

## Fonctionnement Attendu

L'utilisateur interagit avec CyberPlume principalement via :

1.  **Un éditeur de texte riche (basé sur TipTap) :** Pour l'écriture principale du contenu des chapitres/scènes. Des menus contextuels (BubbleMenu) et une barre d'outils permettent d'accéder rapidement aux fonctions de formatage et d'assistance IA.
2.  **Un panneau de gestion de projet :** Pour créer, organiser (glisser-déposer), et naviguer entre les projets, chapitres et scènes. C'est aussi le point d'accès aux métadonnées et aux actions globales (export, analyse).
3.  **Un gestionnaire de personnages dédié :** Pour créer et détailler les fiches personnages (description, traits, backstory, etc.) et les lier aux éléments du projet.
4.  **Des dialogues modaux :** Pour les actions spécifiques comme la configuration de l'IA, l'analyse de style/contenu, la confirmation de suppression, etc.
5.  **Une barre d'outils IA globale :** Pour configurer le fournisseur IA, le modèle, le style et les paramètres avancés.

L'application sauvegarde le travail localement dans une base de données SQLite, assurant la confidentialité et l'accès hors ligne (bien que les fonctions IA nécessitent une connexion). L'utilisateur peut exporter son travail dans divers formats standards.

## Objectifs d'Expérience Utilisateur (UX)

*   **Fluidité et Intuitivité :** L'interface (basée sur Vue.js 3 et Vuetify 3) doit être facile à prendre en main et agréable à utiliser.
*   **Ambiance et Esthétique (Terminée le 20/05) :** Créer une identité visuelle unique, calme et inspirante via une refonte esthétique (nouvelle palette, typographie, icônes SVG personnalisées, arrière-plans de dialogues) pour améliorer le confort visuel lors de longues sessions.
*   **Concentration :** Minimiser les distractions pendant la phase d'écriture (ex: mode sans distraction).
*   **Accessibilité IA :** Rendre l'utilisation des fonctions IA simple et contextuelle, intégrée au flux d'écriture naturel.
*   **Organisation Claire :** Fournir une visualisation et une manipulation aisées de la structure du projet.
*   **Contrôle Utilisateur :** Donner à l'utilisateur le contrôle sur la configuration de l'IA et les options d'export.
*   **Performance :** Assurer une bonne réactivité de l'interface, notamment de l'éditeur.

*Ce document est basé sur l'interprétation des objectifs et fonctionnalités décrits dans `docs/plan-cyber-plume.md` et les efforts de refonte en cours.*