# Stratégies de Gestion du Contexte Inter-Chapitres pour CyberPlume

## 1. Introduction et Objectif

Ce document détaille plusieurs approches pour permettre à CyberPlume de maintenir une conscience contextuelle entre les différents chapitres d'un projet d'écriture. L'objectif principal est de fournir aux fonctionnalités d'assistance IA (génération, suggestion, etc.) des informations pertinentes issues des chapitres précédents, sans surcharger la fenêtre de contexte du LLM avec des textes intégraux.

Chaque approche vise à équilibrer la richesse du contexte fourni, la complexité de mise en œuvre, et la consommation de tokens.

## 2. Principes Généraux Applicables

Indépendamment de l'approche choisie, certains principes devraient être considérés :

*   **Granularité du Contexte :** Déterminer la portée du contexte nécessaire (chapitre N-1 uniquement, N derniers chapitres, résumé global du projet, informations spécifiques sur des personnages/intrigues).
*   **Contrôle Utilisateur :** Idéalement, l'utilisateur devrait pouvoir visualiser, et potentiellement modifier ou affiner, le contexte qui sera fourni à l'IA.
*   **Ingénierie des Prompts :** La manière dont le contexte est injecté dans le prompt de l'IA est cruciale. Il doit être clair, concis et bien structuré.
*   **Économie de Tokens :** Toujours optimiser pour minimiser le nombre de tokens utilisés tout en maximisant la pertinence de l'information.
*   **Transparence :** L'utilisateur devrait comprendre (au moins à un haut niveau) comment le contexte est utilisé.
*   **Itération :** Commencer par une approche plus simple et l'améliorer progressivement.

## 3. Approches Détaillées

### Approche 1: Résumés de Chapitres Précédents

*   **Concept :** Générer un résumé concis du ou des chapitres précédents et l'injecter dans le contexte de l'IA lors du travail sur le chapitre actuel.
*   **Implémentation Détaillée :**
    1.  **Stockage des Résumés :**
        *   Modifier le modèle de données `Chapter` (SQLAlchemy et Pydantic) pour inclure un nouveau champ, par exemple `summary (TEXT, nullable=True)`.
        *   Alternative : Créer une nouvelle table `ChapterSummary` liée à `Chapter` (relation one-to-one ou one-to-many si on veut historiser les résumés).
    2.  **Génération des Résumés :**
        *   Créer une nouvelle route API backend (ex: `POST /api/chapters/{chapter_id}/generate-summary`).
        *   Ce service backend prendra l'ID du chapitre, récupérera son contenu textuel complet (en le nettoyant du HTML si stocké ainsi).
        *   Fera un appel à un service IA (ex: Gemini, Mistral) avec un prompt spécifique pour la summarisation (ex: "Résume le texte suivant en X mots/paragraphes, en te concentrant sur les événements clés, l'évolution des personnages et les nouveaux éléments d'intrigue introduits : [contenu du chapitre]").
        *   Le résumé généré est sauvegardé dans le champ `summary` du chapitre concerné.
    3.  **Interface Utilisateur (Frontend) :**
        *   Ajouter un bouton "Générer/Mettre à jour le résumé" sur l'interface de gestion de chapitre.
        *   Permettre à l'utilisateur de visualiser et potentiellement d'éditer le résumé généré.
    4.  **Injection du Contexte dans les Prompts IA :**
        *   Lorsqu'une action IA est demandée pour le chapitre `N` (ex: "continuer l'écriture"), le backend récupère le résumé du chapitre `N-1` (et potentiellement `N-2`, etc., selon la stratégie).
        *   Le prompt système pour l'IA est modifié pour inclure ce résumé. Exemple :
            ```
            Vous êtes un assistant d'écriture. Vous travaillez sur le chapitre {N} d'un roman.
            Voici un résumé du chapitre {N-1} :
            "{résumé du chapitre N-1}"
            ---
            [Texte actuel du chapitre N jusqu'au curseur de l'utilisateur]
            ---
            Continuez l'histoire à partir d'ici / Répondez à la question suivante : [Prompt utilisateur]
            ```
*   **Flux d'Information pour l'IA :** Résumé(s) textuel(s) + texte partiel du chapitre en cours + instruction utilisateur.
*   **Avantages :**
    *   Relativement simple à comprendre et à mettre en œuvre initialement.
    *   Fournit un contexte narratif direct.
*   **Inconvénients :**
    *   La qualité du résumé est cruciale ; un mauvais résumé peut mal orienter l'IA.
    *   Peut encore consommer un nombre significatif de tokens si les résumés sont longs ou si plusieurs résumés sont inclus.
    *   Perte potentielle de détails fins importants non capturés par le résumé.

### Approche 2: Base de Connaissances Dynamique (Story Bible Augmentée)

*   **Concept :** Maintenir une base de connaissances structurée sur les personnages, les arcs narratifs, les lieux, les objets importants, etc., et mettre à jour dynamiquement leur état à la fin de chaque chapitre. Les informations pertinentes de cette base sont fournies à l'IA.
*   **Implémentation Détaillée :**
    1.  **Modélisation des Données Étendue :**
        *   Pour le modèle `Character` : Ajouter des champs comme `current_status_summary (TEXT)`, `key_developments_last_chapter (TEXT)`, `emotional_state (TEXT)`, `current_goals (TEXT)`.
        *   Créer de nouveaux modèles pour `PlotThread`, `Location`, `SignificantObject` avec des champs similaires pour suivre leur évolution.
    2.  **Mise à Jour de la Base de Connaissances :**
        *   Après la finalisation d'un chapitre, une fonction (manuelle ou semi-automatique) est déclenchée.
        *   Backend : Nouvelle route API (ex: `POST /api/projects/{project_id}/update-knowledge-base?chapter_id={chapter_id}`).
        *   Ce service peut utiliser l'IA pour analyser le chapitre terminé et suggérer des mises à jour pour les entités pertinentes. Prompt IA : "Étant donné le contenu de ce chapitre, comment l'état du personnage X a-t-il changé ? Quels sont ses nouveaux objectifs ou défis ? Le fil d'intrigue Y a-t-il progressé ?".
        *   L'utilisateur valide ou modifie ces suggestions.
    3.  **Interface Utilisateur :**
        *   Une section dédiée "Base de Connaissances" / "Story Bible" dans l'interface.
        *   Affichage clair de l'état actuel des personnages, intrigues, etc.
        *   Outils pour lier explicitement des éléments de la base de connaissances aux chapitres.
    4.  **Injection du Contexte dans les Prompts IA :**
        *   Identifier les entités (personnages, intrigues) actives ou pertinentes pour la scène/le passage en cours d'écriture.
        *   Extraire leurs informations `current_status_summary`, `goals`, etc., de la base de connaissances.
        *   Injecter ces informations structurées dans le prompt système. Exemple :
            ```
            Vous êtes un assistant d'écriture. Vous travaillez sur une scène impliquant Alice et Bob.
            Informations sur Alice (état actuel) : {info_alice_status} Objectifs d'Alice : {info_alice_goals}
            Informations sur Bob (état actuel) : {info_bob_status} Objectifs de Bob : {info_bob_goals}
            Contexte de l'intrigue 'La Quête du MacGuffin' : {info_plot_macguffin}
            ---
            [Texte actuel de la scène]
            ---
            Continuez l'histoire / Générez un dialogue : [Prompt utilisateur]
            ```
*   **Flux d'Information pour l'IA :** Données structurées sur des entités spécifiques + texte partiel du chapitre en cours + instruction utilisateur.
*   **Avantages :**
    *   Contexte très ciblé, potentiellement riche et pertinent.
    *   Permet de suivre l'évolution des éléments narratifs de manière granulaire.
*   **Inconvénients :**
    *   Plus complexe à modéliser et à implémenter.
    *   Nécessite un effort de maintenance de la base de connaissances (même assisté par IA, l'utilisateur doit valider).
    *   Risque de devenir une tâche fastidieuse pour l'utilisateur si mal conçue.

### Approche 3: Extraction d'Entités et de Faits Clés Structurés

*   **Concept :** Analyser les chapitres précédents pour extraire des "faits" structurés (ex: "Personnage A a rencontré Personnage B à Lieu C et a appris Information D"). Ces faits sont ensuite fournis à l'IA.
*   **Implémentation Détaillée :**
    1.  **Stockage des Faits :**
        *   Nouvelle table `ChapterFact` (ou `KnowledgeGraphTriple`) : `chapter_id (FK)`, `subject_entity_id`, `predicate (TEXT)`, `object_entity_id_or_value`, `context_details (TEXT)`.
        *   Utiliser les entités existantes (Personnages, etc.) comme sujets/objets lorsque c'est possible.
    2.  **Extraction des Faits :**
        *   Backend : Nouvelle route API (ex: `POST /api/chapters/{chapter_id}/extract-facts`).
        *   Utiliser spaCy (que CyberPlume utilise déjà) pour l'extraction d'entités nommées (NER), l'analyse de dépendances, et potentiellement des modèles de classification de relations.
        *   Alternativement, utiliser un LLM avec un prompt spécifique pour l'extraction de faits : "Extrais les principaux événements, relations et informations clés de ce texte sous forme de triplets (Sujet, Prédicat, Objet) ou de phrases factuelles concises : [contenu du chapitre]".
        *   Les faits extraits sont stockés dans la table `ChapterFact`.
    3.  **Interface Utilisateur :**
        *   Optionnel : Visualisation des faits extraits par chapitre.
    4.  **Injection du Contexte dans les Prompts IA :**
        *   Lorsqu'une action IA est demandée, récupérer les faits pertinents des chapitres précédents (basé sur les personnages impliqués, les thèmes, etc. - peut nécessiter une logique de filtrage).
        *   Injecter ces faits dans le prompt. Exemple :
            ```
            Contexte des chapitres précédents (faits saillants) :
            - Chapitre 1 : Alice a découvert une carte ancienne à Paris.
            - Chapitre 2 : Bob a volé la carte à Alice à Londres.
            - Chapitre 2 : Alice a juré de retrouver Bob.
            Vous écrivez maintenant le chapitre 3, où Alice arrive à Rome, pensant que Bob s'y cache.
            ---
            [Texte actuel du chapitre 3]
            ---
            Continuez l'histoire : [Prompt utilisateur]
            ```
*   **Flux d'Information pour l'IA :** Liste de faits structurés + texte partiel du chapitre en cours + instruction utilisateur.
*   **Avantages :**
    *   Concis et potentiellement très économe en tokens.
    *   Peut être plus objectif qu'un résumé narratif.
*   **Inconvénients :**
    *   Peut manquer de nuances émotionnelles ou stylistiques.
    *   La qualité de l'extraction automatique (spaCy ou LLM) est critique et peut être imparfaite.
    *   Définir la "pertinence" des faits à injecter peut être complexe.

### Approche 4: Récupération Augmentée par Génération (RAG - Retrieval Augmented Generation)

*   **Concept :** Transformer les chapitres précédents en "chunks" (morceaux) de texte, les vectoriser (créer des embeddings numériques), et les stocker dans une base de données vectorielle. Lorsqu'une assistance IA est demandée, la requête utilisateur (ou le dernier paragraphe écrit) est vectorisée, et les chunks les plus sémantiquement similaires des chapitres précédents sont récupérés et fournis en contexte à l'IA.
*   **Implémentation Détaillée :**
    1.  **Infrastructure de Vectorisation et Stockage :**
        *   Choisir un modèle d'embedding (ex: `sentence-transformers` pour du local, ou API d'OpenAI/Cohere).
        *   Choisir une base de données vectorielle (ex: ChromaDB, FAISS pour du local ; Pinecone, Weaviate pour du cloud). ChromaDB est une bonne option pour commencer en local avec Python.
        *   Processus de "chunking" : Diviser les chapitres en morceaux de texte plus petits (ex: par paragraphe, ou par nombre de mots/tokens avec chevauchement).
    2.  **Indexation des Chapitres :**
        *   Lorsqu'un chapitre est sauvegardé/finalisé :
            *   Le découper en chunks.
            *   Pour chaque chunk, générer son embedding.
            *   Stocker le chunk (ou une référence) et son embedding dans la base de données vectorielle, avec des métadonnées (ex: `project_id`, `chapter_id`, `chunk_sequence_number`).
    3.  **Récupération de Contexte :**
        *   Lorsqu'une action IA est demandée (ex: "continuer l'écriture à partir de [dernier paragraphe]") :
            *   Prendre le dernier paragraphe (ou la requête utilisateur explicite) comme "query".
            *   Générer l'embedding de cette query.
            *   Interroger la base de données vectorielle pour trouver les `k` chunks les plus similaires sémantiquement à la query, en filtrant par le projet actuel et les chapitres précédents.
    4.  **Interface Utilisateur :**
        *   Principalement transparent pour l'utilisateur.
        *   Optionnel : Afficher des indicateurs des sources de contexte utilisées (ex: "Contexte récupéré des chapitres X et Y").
    5.  **Injection du Contexte dans les Prompts IA :**
        *   Les `k` chunks récupérés sont injectés dans le prompt système. Exemple :
            ```
            Vous êtes un assistant d'écriture.
            Voici des extraits pertinents des chapitres précédents qui pourraient vous aider :
            Extrait 1 (Source : Chapitre 1, Paragraphe 5) : "{chunk_1_text}"
            Extrait 2 (Source : Chapitre 2, Paragraphe 12) : "{chunk_2_text}"
            ---
            Texte actuel du chapitre en cours :
            [Texte actuel jusqu'au curseur]
            ---
            En vous basant sur le texte actuel ET les extraits ci-dessus, continuez l'histoire : [Prompt utilisateur]
            ```
*   **Flux d'Information pour l'IA :** Chunks de texte sémantiquement pertinents + texte partiel du chapitre en cours + instruction utilisateur.
*   **Avantages :**
    *   Très dynamique et peut fournir un contexte hautement pertinent même pour de grandes quantités de texte.
    *   S'adapte bien à la "dérive" du sujet au sein d'un long texte.
    *   Scalable.
*   **Inconvénients :**
    *   La plus complexe à mettre en place (nécessite des composants supplémentaires : modèle d'embedding, base de données vectorielle, logique de chunking et de recherche).
    *   Le choix du modèle d'embedding, la stratégie de chunking, et le nombre `k` de résultats à récupérer nécessitent du réglage et de l'expérimentation.
    *   Peut parfois ramener des informations non pertinentes si la query est ambiguë.

## 4. Approches Hybrides

Il est tout à fait possible et souvent souhaitable de combiner des éléments des approches ci-dessus. Par exemple :

*   **Résumé + RAG :** Fournir un résumé du chapitre N-1 ET quelques chunks RAG très pertinents.
*   **Story Bible + RAG :** Utiliser la Story Bible pour les informations clés sur les personnages/intrigues actifs, et RAG pour des détails contextuels plus larges.

## 5. Considérations pour l'Implémentation dans CyberPlume

*   **Commencer par une MVP :** Choisir l'approche la plus simple qui apporte une valeur ajoutée (probablement l'Approche 1 : Résumés).
*   **Modularité :** Concevoir le système de gestion de contexte de manière modulaire afin de pouvoir expérimenter avec différentes stratégies ou les combiner plus tard.
*   **Configuration Utilisateur :** Permettre à l'utilisateur de choisir le niveau de contexte ou la stratégie (pour les utilisateurs avancés).
*   **Performance :** S'assurer que la génération/récupération de contexte ne ralentit pas excessivement l'expérience utilisateur. Les opérations d'embedding ou les appels LLM pour résumé peuvent prendre du temps et devraient idéalement être asynchrones avec un retour visuel à l'utilisateur.
*   **Gestion des Clés API :** Si des appels LLM supplémentaires sont nécessaires (ex: pour résumés), s'assurer que la gestion des clés API existante est utilisée.

## 6. Conclusion

L'implémentation d'une gestion efficace du contexte inter-chapitres représente une amélioration significative pour CyberPlume. En évaluant soigneusement les compromis de chaque approche et en commençant par une solution pragmatique, il est possible d'améliorer considérablement la cohérence et la pertinence de l'assistance IA fournie aux écrivains.