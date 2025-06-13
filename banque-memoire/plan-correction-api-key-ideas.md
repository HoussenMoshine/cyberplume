# Plan de Correction : Récupération Clé API pour Idées de Scènes

**Date :** 03/06/2025

**Problème Identifié :**
L'endpoint `POST /ideas/scene/generate` dans `backend/routers/ideas.py` retourne une erreur 500. L'analyse a révélé que l'appel `settings.get_api_key(request_data.ai_provider)` à la ligne 24 est incorrect car la classe `Settings` dans `backend/config.py` ne possède pas de méthode `get_api_key()`. Les clés API sont stockées comme des attributs individuels (ex: `settings.gemini_api_key`).

**Objectif :**
Corriger la récupération de la clé API dans `backend/routers/ideas.py` pour résoudre l'erreur 500 et assurer le bon fonctionnement de la génération d'idées de scènes.

**Étapes de Correction :**

1.  **Modification de `backend/routers/ideas.py` :**
    *   Remplacer la ligne :
        ```python
        api_key=settings.get_api_key(request_data.ai_provider),
        ```
    *   Par une logique conditionnelle pour récupérer la clé API appropriée depuis l'objet `settings` en fonction de la valeur de `request_data.ai_provider`.

    *   **Exemple de Logique (à adapter pour la robustesse et la gestion d'erreurs) :**
        ```python
        api_key_value = None
        if request_data.ai_provider == "gemini":
            api_key_value = settings.gemini_api_key
        elif request_data.ai_provider == "mistral":
            api_key_value = settings.mistral_api_key
        elif request_data.ai_provider == "openrouter":
            api_key_value = settings.openrouter_api_key
        else:
            # Gérer le cas d'un fournisseur non supporté ou inconnu
            raise HTTPException(status_code=400, detail=f"Fournisseur IA '{request_data.ai_provider}' non supporté.")

        if not api_key_value:
            # Gérer le cas où la clé API pour un fournisseur supporté n'est pas configurée
            raise HTTPException(status_code=500, detail=f"Clé API pour '{request_data.ai_provider}' non configurée.")
        
        # ... dans l'appel à create_adapter:
        # api_key=api_key_value,
        ```

2.  **Cohérence avec les Modules IA Existants :**
    *   Avant d'appliquer la modification, examiner brièvement comment les autres routeurs ou services qui interagissent avec l'IA (ex: pour l'éditeur, les personnages) récupèrent et utilisent les clés API et les adaptateurs.
    *   S'assurer que la solution adoptée dans `ideas.py` est cohérente avec les patrons établis dans le reste de l'application pour la gestion des services IA. Cela inclut la manière dont les erreurs (clé manquante, fournisseur inconnu) sont gérées et communiquées au frontend.

3.  **Validation :**
    *   Après la correction, redémarrer le backend.
    *   Tester la fonctionnalité de génération d'idées de scènes depuis le frontend pour confirmer que l'erreur 500 est résolue.
    *   Vérifier les logs du backend pour s'assurer qu aucune nouvelle erreur liée à la récupération de la clé API n'apparaît.

**Prochaines Étapes après cette Correction :**
Une fois l'erreur 500 résolue, l'investigation se portera sur l'erreur `TypeError: showSnackbar is not a function` dans `frontend/src/composables/useSceneIdeas.js`.