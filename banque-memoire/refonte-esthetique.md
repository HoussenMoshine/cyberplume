# Planification de la Refonte Esthétique - CyberPlume (Mise à jour : 07/05/2025 - 2:38 PM)

*Ce document sert à planifier et suivre la refonte visuelle de l'application CyberPlume.*

## 1. Introduction & Objectifs

### Constat
L'interface actuelle de CyberPlume, bien que fonctionnelle, est jugée trop sobre et utilise les styles par défaut de Vuetify. Elle manque d'une identité visuelle propre et d'une atmosphère propice à la créativité et à la concentration.

### Objectifs
*   Créer une identité visuelle unique et professionnelle pour CyberPlume.
*   Instaurer une ambiance **calme, harmonieuse et inspirante** pour l'utilisateur (écrivain).
*   Améliorer la lisibilité et le confort visuel, notamment pour de longues sessions d'écriture.
*   Moderniser l'apparence générale de l'application.
*   Assurer une cohérence esthétique sur l'ensemble des vues et composants.

## 2. Analyse de l'État Actuel

*(Basée sur les captures d'écran fournies le 29/04/2025)*

*   **Palette de couleurs :** Utilisation prédominante des couleurs par défaut de Vuetify (bleu primaire, gris, blanc). Manque de chaleur et de personnalité.
*   **Typographie :** Polices par défaut, potentiellement petites pour certains textes. Manque de hiérarchie visuelle claire par la typographie.
*   **Icônes :** Utilisation des icônes Material Design Icons (MDI) via Vuetify. Fonctionnelles mais génériques.
*   **Composants :** Styles par défaut pour `v-card`, `v-dialog`, `v-list`, `v-btn`, `v-toolbar`, etc. Manque d'ombres subtiles, de bordures arrondies cohérentes, d'espacements travaillés.
*   **Densité :** L'interface semble parfois un peu dense, notamment dans les dialogues.

## 3. Inspiration & Palette de Couleurs (Validée le 29/04/2025 - Implémentée)

*   **Inspiration :** L'image `new-couleurs-cyberplume.png` fournie le 29/04/2025. Objectif : palette apaisante.
*   **Palette Cible (Implémentée dans `vuetify.js`) :**
    *   **Fond Principal (Blanc cassé/Crème) :** `#F8F6F0` (background)
    *   **Fond Éléments (Blanc) :** `#FFFFFF` (surface) - *Utilisé par défaut pour VCard/VDialog pour lisibilité.*
    *   **Fond Secondaire (Bleu ciel clair) :** `#B0D7E5` (surface-variant) - *Utilisé pour ActionPanel.*
    *   **Primaire (Bleu-vert moyen) :** `#4DB1AB` (primary)
    *   **Secondaire / Accent Fort (Bleu moyen) :** `#3B79B8` (secondary)
    *   **Texte Principal :** `#333333` (on-background, on-surface)
    *   **Texte Secondaire / Désactivé :** `#757575` (implicite)
    *   **Couleurs Sémantiques (Succès, Erreur, Info, Warning) :** Définies dans `vuetify.js`.

## 4. Typographie (Validée le 29/04/2025 - Implémentée)

*   **Police pour Titres (Headers) :** **Merriweather** (Google Font) - Serif élégante et lisible.
*   **Police pour Corps de Texte (Body) :** **Lato** (Google Font) - Sans-serif claire et lisible, nombreuses graisses disponibles.
*   **Tailles & Graisses :** Échelle typographique par défaut de Vuetify utilisée pour l'instant.
*   **Intégration :** Utilisation de Google Fonts via `webfontloader` (confirmé dans `frontend/src/plugins/webfontloader.js`).

## 5. Icônes (Validée le 29/04/2025 - Intégration Bien Avancée)

*   **Stratégie :** Remplacer progressivement les icônes MDI par **Tabler Icons (SVG)** via `@tabler/icons-vue`.
*   **Avantages SVG :** Cohérence, style moderne, personnalisation (couleur, taille via CSS), légèreté.
*   **Intégration :** Utilisation directe des composants icônes importés. En place dans la plupart des composants clés et dialogues.

## 6. Stylisation des Composants Clés

*(Liste non exhaustive, à prioriser lors de l'implémentation)*

*   **`v-app-bar` / `v-navigation-drawer` :** Style global de la navigation. *(`v-app-bar` a reçu une bordure subtile).*
*   **`v-card` :** Ombres, rayons de bordure, espacements internes. *Utilise le fond `surface` (blanc) par défaut pour lisibilité.*
*   **`v-dialog` :** Style de l'en-tête (police Merriweather), pied de page (padding `pa-4`), ombres, arrière-plan. *Utilise le fond `surface` (blanc) par défaut. Styles des boutons harmonisés (Phase 3.5 terminée).*
*   **`v-list` / `v-list-item` :** Espacements, indicateurs de sélection/survol, séparateurs. *(Phase 2 terminée, menu d'export projet semble OK)*
*   **`v-btn` :** Styles pour les différents types (primaire `flat text-white`, secondaire `flat`, texte `variant="text"`), états (hover, focus, disabled), rayons de bordure. *(Phase 2 terminée, affinements en Phase 3.5 terminés pour les dialogues)*
*   **`v-text-field` / `v-select` / `v-textarea` :** Apparence des champs de formulaire. *(Phase 2 terminée)*
*   **`v-chip` :** Style des puces. *(Phase 2 terminée)*
*   **Éditeur TipTap :** Style de la barre d'outils, du contenu édité (via CSS ciblé). *(Phase 3 - Sous-tâche 3.1 Terminée ✅)*
*   **`ProjectManager` / `CharacterManager` :** Mise en page générale, style des listes et éléments interactifs. *(Phase 3 - Sous-tâche 3.2 (ProjectManager) Terminée ✅, Sous-tâche 3.3 (CharacterManager) Terminée ✅)*
*   **`ActionPanel.vue` :** *Restylisé (Phase 3) : fond `surface-variant`, boutons larges, icônes Tabler, élévation.* **Validé.**
*   **Scrollbars :** Styliser les barres de défilement pour une meilleure intégration. *(Phase 2/3 - À vérifier)*

## 7. Plan d'Action Détaillé (État au 07/05/2025 - 2:38 PM)

```mermaid
graph TD
    subgraph Phase 1: Fondations Visuelles (Terminée ✅)
        A[Finaliser Palette & Codes Hex] --> B(Choisir Polices: Merriweather & Lato);
        B --> C(Choisir Icônes: Tabler Icons SVG);
        C --> D(Configurer Thème Vuetify de Base);
    end

    subgraph Phase 2: Style Global & Composants Communs (Terminée ✅)
        E[Styliser Layout Principal (AppBar, Fonds)] --> F(Styliser Composants Communs: v-card, v-btn, v-dialog, v-list, v-text-field...);
        F --> G(Intégrer Icônes Tabler);
        style E fill:#d4edda,stroke:#c3e6cb
        style F fill:#d4edda,stroke:#c3e6cb
        style G fill:#d4edda,stroke:#c3e6cb
    end

    subgraph Phase 3: Style Vues Spécifiques (Terminée ✅)
        H[Adapter Style Éditeur TipTap] --> I(Revoir Esthétique ProjectManager);
        I --> J(Revoir Esthétique CharacterManager);
        J --> K(Ajuster Dialogues Spécifiques);
        style H fill:#d4edda,stroke:#c3e6cb
        style I fill:#d4edda,stroke:#c3e6cb
        style J fill:#d4edda,stroke:#c3e6cb
        style K fill:#d4edda,stroke:#c3e6cb
    end

    subgraph Phase 4: Tests & Ajustements (À venir ➡️)
        L[Tester sur Différents Écrans] --> M(Recueillir Retours & Ajuster);
        M --> N(Vérifier Cohérence Globale);
    end

    Phase 1 --> Phase 2 --> Phase 3 --> Phase 4;

    note right of F
        - VCard/VDialog utilisent fond 'surface' (blanc).
        - Styles de base pour VBtn, VList, VTextField, etc. OK.
    end note
    note right of H
        - **Sous-tâche 3.1 (Style Éditeur TipTap) : TERMINÉE ✅**
        - Part 1 (Bordure toolbar, style liens, boutons bubble menu) : VALIDÉ ✅
        - Part 2 (Styles listes et citations) : VALIDÉ ✅
        - Part 3 (Couleur texte principal, taille police, couleur citations) : VALIDÉ ✅
        - Part 4 (Style hr, vérif mode sans distraction) : VALIDÉ ✅
    end note
    note right of I
        - **Sous-tâche 3.2 (Style ProjectManager & enfants) : TERMINÉE ✅**
        - [`ProjectToolbar.vue`](frontend/src/components/ProjectToolbar.vue:1) : Couleur bouton harmonisée.
        - [`ProjectItem.vue`](frontend/src/components/ProjectItem.vue:1) : Style bordure en-tête amélioré.
        - [`ChapterList.vue`](frontend/src/components/ChapterList.vue:1) : Couleurs chargement/drag & menu export harmonisés.
        - [`SceneList.vue`](frontend/src/components/SceneList.vue:1) : Couleurs chargement/drag harmonisées.
    end note
    note right of J
        - **Sous-tâche 3.3 (Style CharacterManager) : TERMINÉE ✅**
        - [`CharacterManager.vue`](frontend/src/components/CharacterManager.vue:1) : Toolbar, boutons, et bordures de liste harmonisés.
    end note
    note right of K
        - ActionPanel.vue restylisé et validé.
        - Sous-tâche 3.5 (Dialogues Spécifiques) :
            - 3.5.2 (Dialogues Simples) : VALIDÉ.
            - StyleAnalysisDialog.vue (3.5.3) : VALIDÉ.
            - ChapterAnalysisDialog.vue (3.5.3) : VALIDÉ.
            - GenerateSceneDialog.vue (3.5.3) : VALIDÉ (après corrections).
            - DeleteConfirmDialog.vue (3.5.4) : VALIDÉ.
            - AnalysisReportDialog.vue (3.5.4) : VALIDÉ.
        - **SOUS-TÂCHE 3.5 TERMINÉE ✅**
    end note
```

*Ce document sera mis à jour au fur et à mesure de l'avancement de la refonte.*