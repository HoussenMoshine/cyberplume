**Date actuelle :** 15 mai 2025

**Référence principale :** [https://github.com/pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)

## Table des Matières

1.  **Introduction à Pydantic AI**
      * Principes de base
      * Installation
2.  **Configuration Initiale : Gestion des Clés API avec un fichier `.env`**
      * Installation de `python-dotenv`
      * Création et structure du fichier `.env`
3.  **Concepts Clés de Pydantic AI**
      * `PydanticAI`: Le cœur de la bibliothèque
      * Définition des modèles de sortie (Pydantic Models)
      * Gestion des entrées
4.  **Utilisation avec Google Gemini**
      * Configuration (avec `.env`)
      * Exemples de code (chargement depuis `.env`)
5.  **Utilisation avec Mistral AI**
      * Configuration (avec `.env`)
      * Exemples de code (chargement depuis `.env`)
6.  **Utilisation avec OpenRouter**
      * Configuration (avec `.env`)
      * Exemples de code (chargement depuis `.env`)
7.  **Bonnes Pratiques et Dépannage**
      * Gestion des erreurs
      * Optimisation des prompts
      * Débogage (en tenant compte du `.env`)

-----

## 1\. Introduction à Pydantic AI

### Principes de base

Pydantic AI est une bibliothèque Python conçue pour intégrer de manière transparente les modèles de langage (LLMs) avec les capacités de validation de données et de gestion de schémas de Pydantic. Elle permet de structurer les entrées et les sorties des LLMs, garantissant la fiabilité et la prévisibilité de vos applications basées sur l'IA. Pydantic AI agit comme une couche d'abstraction, facilitant l'interaction avec divers LLMs tout en s'assurant que les réponses sont conformes aux schémas que vous définissez.

### Installation

Assurez-vous d'avoir Python installé (version 3.8 ou ultérieure recommandée). Vous pouvez installer Pydantic AI via pip :

```bash
pip install pydantic-ai
```

Selon le LLM que vous souhaitez utiliser, des bibliothèques supplémentaires seront nécessaires :

  * Pour Google Gemini : `pip install google-generativeai`
  * Pour Mistral AI : `pip install mistralai`
  * Pour les services compatibles OpenAI (comme OpenRouter) : `pip install openai`

-----

## 2\. Configuration Initiale : Gestion des Clés API avec un fichier `.env`

Pour gérer vos clés API de manière sécurisée et éviter de les coder en dur dans vos scripts, nous utiliserons un fichier `.env`.

### Installation de `python-dotenv`

Cette bibliothèque charge les variables d'environnement à partir d'un fichier `.env`.

```bash
pip install python-dotenv
```

### Création et structure du fichier `.env`

Créez un fichier nommé `.env` à la racine de votre dossier de projet (au même niveau que vos scripts Python). **Ajoutez ce fichier à votre `.gitignore` pour ne jamais le versionner.**

**Contenu type de votre fichier `.env` :**

```env
# Clé API pour Google Gemini
GOOGLE_API_KEY="VOTRE_CLE_API_GEMINI_ICI"

# Clé API pour Mistral AI
MISTRAL_API_KEY="VOTRE_CLE_API_MISTRAL_ICI"

# Clé API pour OpenRouter (commence souvent par sk-or-v1...)
OPENROUTER_API_KEY="VOTRE_CLE_API_OPENROUTER_ICI"

# Base URL pour OpenRouter (utilisée avec le client OpenAI)
OPENAI_API_BASE="https://openrouter.ai/api/v1"

# Optionnel, pour des configurations OpenRouter avancées (modèles gratuits)
# YOUR_SITE_URL="http://localhost:3000"
# YOUR_APP_NAME="MonAppPydanticAI"
```

Remplacez les valeurs `"VOTRE_CLE_..."` par vos clés API réelles.

Au début de chaque script Python, vous chargerez ces variables comme suit :

```python
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
# S'assure que load_dotenv() est appelé avant d'accéder à os.environ pour les clés.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # Assure que le .env est cherché au bon endroit
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Essayer de charger depuis le répertoire courant si __file__ n'est pas défini (ex: REPL)
    load_dotenv()

# Vos clés sont maintenant accessibles via os.environ.get("NOM_DE_LA_CLE")
```

-----

## 3\. Concepts Clés de Pydantic AI

### `PydanticAI`: Le cœur de la bibliothèque

La classe `PydanticAI` est le point d'entrée. Vous l'instanciez en spécifiant le moteur LLM à utiliser (par son nom ou en passant une instance de client LLM). Elle prendra en compte les clés API chargées dans l'environnement.

### Définition des modèles de sortie (Pydantic Models)

Vous définissez la structure de la sortie attendue du LLM en créant une classe héritant de `pydantic.BaseModel`. Les descriptions dans `Field` aident le LLM à comprendre ce qui est attendu.

**Exemple :**

```python
from pydantic import BaseModel, Field
from typing import List

class Auteur(BaseModel):
    nom: str = Field(description="Nom de l'auteur")
    email: str = Field(description="Adresse email de l'auteur")

class Article(BaseModel):
    titre: str = Field(description="Titre de l'article")
    contenu: str = Field(description="Corps principal de l'article")
    tags: List[str] = Field(description="Liste de mots-clés ou tags pour l'article")
    auteur_info: Auteur = Field(description="Informations sur l'auteur de l'article")
```

### Gestion des entrées

Vous fournissez un prompt (instruction/question) au LLM. Pydantic AI s'attend à ce que le LLM réponde d'une manière qui puisse être analysée et validée par votre modèle Pydantic.

-----

## 4\. Utilisation avec Google Gemini

### Configuration (avec `.env`)

1.  Assurez-vous que `GOOGLE_API_KEY="VOTRE_CLE_API_GEMINI_ICI"` est présent et correct dans votre fichier `.env`.
2.  Vérifiez que `google-generativeai` et `python-dotenv` sont installés.

### Exemples de code (chargement depuis `.env`)

**Exemple 1 : Extraction d'informations utilisateur**

```python
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import PydanticAI
from typing import List

# Charger les variables d'environnement
load_dotenv() # Cherchera .env dans le répertoire courant ou celui du script

class UserProfile(BaseModel):
    nom: str = Field(description="Nom complet de la personne")
    age: int = Field(description="Âge de la personne")
    ville: str = Field(description="Ville de résidence")
    interests: List[str] = Field(description="Liste des centres d'intérêt")

# Récupérer la clé API depuis l'environnement
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GEMINI_API_KEY:
    # PydanticAI utilisera automatiquement la clé GOOGLE_API_KEY de l'environnement
    # si elle est définie lors de l'initialisation avec un moteur Google.
    llm_gemini = PydanticAI(llm_engine_name='google/gemini-pro') 
    # Autres modèles Gemini: 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest'

    texte_description = "Alice Martin a 28 ans, vit à Paris et adore la photographie et les voyages."
    print(f"Demande d'extraction pour Gemini ('{llm_gemini.llm_engine_name}'):")

    try:
        profil_utilisateur = llm_gemini(
            input_text=texte_description,
            pydantic_model=UserProfile,
            instruction="Extrais les informations du profil utilisateur à partir du texte."
        )
        print("\nProfil utilisateur extrait:")
        print(f"  Nom: {profil_utilisateur.nom}")
        print(f"  Âge: {profil_utilisateur.age}")
        print(f"  Ville: {profil_utilisateur.ville}")
        print(f"  Intérêts: {', '.join(profil_utilisateur.interests)}")
    except Exception as e:
        print(f"\nErreur avec Gemini: {e}")
        print("Vérifiez votre GOOGLE_API_KEY dans .env, sa validité, et vos quotas Google AI.")
else:
    print("Clé GOOGLE_API_KEY non trouvée. Veuillez la définir dans votre fichier .env.")
```

-----

## 5\. Utilisation avec Mistral AI

### Configuration (avec `.env`)

1.  Assurez-vous que `MISTRAL_API_KEY="VOTRE_CLE_API_MISTRAL_ICI"` est présent et correct dans votre fichier `.env`.
2.  Vérifiez que `mistralai` et `python-dotenv` sont installés.

### Exemples de code (chargement depuis `.env`)

**Exemple 1 : Génération de résumé de texte**

```python
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import PydanticAI
from typing import List

load_dotenv()

class Resume(BaseModel):
    titre_original: str = Field(description="Le titre approximatif ou sujet du texte original.")
    points_cles: List[str] = Field(description="Une liste des points les plus importants du texte.")
    resume_court: str = Field(description="Un résumé concis du texte en une ou deux phrases.")

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

if MISTRAL_API_KEY:
    # PydanticAI utilisera MISTRAL_API_KEY de l'environnement pour les moteurs Mistral.
    # Modèles Mistral: 'mistralai/mistral-tiny', 'mistralai/mistral-small-latest', 'mistralai/mistral-medium-latest', 'mistralai/mistral-large-latest'
    # Ou pour la plateforme ouverte : 'mistral-7b-instruct', 'open-mistral-nemo' (vérifiez noms exacts)
    llm_mistral = PydanticAI(llm_engine_name='mistralai/mistral-small-latest') 

    long_texte = (
        "L'intelligence artificielle (IA) est un domaine en pleine expansion de l'informatique "
        "qui vise à créer des machines capables d'imiter des fonctions cognitives humaines "
        "telles que l'apprentissage, la résolution de problèmes et la prise de décision. "
        "Ses applications sont vastes, allant des moteurs de recherche aux voitures autonomes, "
        "en passant par la médecine et la finance. Les progrès récents, notamment dans "
        "l'apprentissage profond, ont conduit à des avancées spectaculaires."
    )
    print(f"\nDemande de résumé pour Mistral ('{llm_mistral.llm_engine_name}'):")

    try:
        resume_genere = llm_mistral(
            input_text=long_texte,
            pydantic_model=Resume,
            instruction="Résume ce texte en identifiant ses points clés et en fournissant un bref résumé."
        )
        print("\nRésumé généré:")
        print(f"  Sujet: {resume_genere.titre_original}")
        print("  Points clés:")
        for point in resume_genere.points_cles:
            print(f"    - {point}")
        print(f"  Résumé court: {resume_genere.resume_court}")
    except Exception as e:
        print(f"\nErreur avec Mistral: {e}")
        print("Vérifiez votre MISTRAL_API_KEY dans .env, sa validité, et vos quotas Mistral AI.")
else:
    print("Clé MISTRAL_API_KEY non trouvée. Veuillez la définir dans votre fichier .env.")
```

-----

## 6\. Utilisation avec OpenRouter

OpenRouter agit comme un agrégateur, donnant accès à de nombreux LLMs via une API compatible OpenAI.

### Configuration (avec `.env`)

1.  Dans votre fichier `.env`, assurez-vous d'avoir :
    ```env
    OPENROUTER_API_KEY="sk-or-v1-VOTRE_CLE_OPENROUTER_ICI"
    OPENAI_API_BASE="https://openrouter.ai/api/v1" 
    # Optionnel, pour certains modèles gratuits sur OpenRouter qui demandent des en-têtes:
    # YOUR_SITE_URL="http://votre-site.com" # Mettez une URL (même localhost)
    # YOUR_APP_NAME="MonApplicationPydantic" # Mettez un nom d'application
    ```
2.  Vérifiez que `openai` (la bibliothèque, car PydanticAI l'utilise souvent pour les backends compatibles) et `python-dotenv` sont installés.

PydanticAI, lorsqu'il utilise un backend de type OpenAI, cherchera `OPENAI_API_KEY` et `OPENAI_API_BASE` dans les variables d'environnement. Nous allons donc nous assurer que `OPENAI_API_KEY` est défini à partir de votre `OPENROUTER_API_KEY`.

### Exemples de code (chargement depuis `.env`)

**Exemple 1 : Traduction et identification de langue via un modèle sur OpenRouter**

```python
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import PydanticAI
# Pour une configuration client plus avancée (si nécessaire pour des en-têtes spécifiques)
# from openai import OpenAI 

load_dotenv()

class TraductionInfo(BaseModel):
    texte_original: str
    langue_detectee: str = Field(description="Code ISO 639-1 de la langue détectée (ex: fr, en, es)")
    texte_traduit: str = Field(description="Le texte traduit en anglais.")
    modele_utilise: str = Field(description="Le nom du modèle qui a effectué la tâche.")

# Récupérer les configurations pour OpenRouter
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE = os.environ.get("OPENAI_API_BASE")

# S'assurer que la clé API OpenRouter est utilisée comme OPENAI_API_KEY pour PydanticAI
# et que la base URL est correcte.
if OPENROUTER_KEY and not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = OPENROUTER_KEY # PydanticAI/OpenAI client will pick this up

if OPENROUTER_BASE != "https://openrouter.ai/api/v1":
    print(f"Avertissement: OPENAI_API_BASE ('{OPENROUTER_BASE}') n'est pas l'URL OpenRouter standard. "
          "Assurez-vous qu'elle est correcte dans votre .env ('https://openrouter.ai/api/v1').")
    # Forcer pour l'exemple si mal configuré mais clé présente (mieux vaut corriger .env)
    # if OPENROUTER_KEY: os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"


# Vérifier si les variables nécessaires pour OpenRouter sont prêtes
if os.environ.get("OPENAI_API_KEY") and os.environ.get("OPENAI_API_BASE") == "https://openrouter.ai/api/v1":
    
    # Choisissez un modèle disponible sur OpenRouter. Exemples:
    # 'mistralai/mistral-7b-instruct' (populaire)
    # 'google/gemini-pro'
    # 'anthropic/claude-3-haiku'
    # 'openai/gpt-3.5-turbo'
    # Certains modèles gratuits comme 'undi95/toppy-m-7b:free' peuvent nécessiter des en-têtes
    # personnalisés (HTTP-Referer, X-Title) via un client OpenAI personnalisé.
    
    nom_modele_openrouter = "mistralai/mistral-7b-instruct" # Changez selon vos besoins
    
    print(f"\nDemande de traduction pour OpenRouter (modèle: '{nom_modele_openrouter}')")
    print(f"API Base URL: {os.environ.get('OPENAI_API_BASE')}")
    print(f"API Key (début): {os.environ.get('OPENAI_API_KEY', '')[:10]}...")


    # ---- Configuration standard de PydanticAI ----
    # PydanticAI utilisera les variables d'environnement OPENAI_API_KEY et OPENAI_API_BASE
    llm_openrouter = PydanticAI(llm_engine_name=nom_modele_openrouter)
    
    # ---- OU Configuration avec client OpenAI personnalisé (pour en-têtes) ----
    # YOUR_SITE_URL = os.environ.get("YOUR_SITE_URL", "http://localhost")
    # YOUR_APP_NAME = os.environ.get("YOUR_APP_NAME", "PydanticTest")
    # openrouter_http_client = OpenAI(
    #     api_key=os.environ.get("OPENAI_API_KEY"),
    #     base_url=os.environ.get("OPENAI_API_BASE"),
    #     default_headers={ # Peut être nécessaire pour certains modèles
    #         "HTTP-Referer": YOUR_SITE_URL,
    #         "X-Title": YOUR_APP_NAME
    #     }
    # )
    # llm_openrouter = PydanticAI(llm_engine=openrouter_http_client, llm_engine_name=nom_modele_openrouter)
    # print("Utilisation d'un client OpenAI personnalisé pour OpenRouter avec en-têtes.")
    # ----------------------------------------------------

    texte_a_traduire = "Bonjour le monde, comment allez-vous aujourd'hui ?"

    try:
        resultat_traduction = llm_openrouter(
            input_text=texte_a_traduire,
            pydantic_model=TraductionInfo,
            instruction=(
                "Détecte la langue du texte fourni, traduis-le en anglais, "
                f"et indique que le modèle '{nom_modele_openrouter}' a été utilisé."
            )
        )
        print("\nRésultat de la traduction:")
        print(f"  Texte original: {resultat_traduction.texte_original}")
        print(f"  Langue détectée: {resultat_traduction.langue_detectee}")
        print(f"  Traduction (anglais): {resultat_traduction.texte_traduit}")
        print(f"  Modèle (rapporté par LLM): {resultat_traduction.modele_utilise}")
    except Exception as e:
        print(f"\nErreur avec OpenRouter (modèle '{nom_modele_openrouter}'): {e}")
        print("Vérifications possibles:")
        print("  - OPENROUTER_API_KEY et OPENAI_API_BASE sont-ils corrects dans .env ?")
        print(f"  - Le modèle '{nom_modele_openrouter}' est-il valide et avez-vous des crédits sur OpenRouter ?")
        print("  - Si le modèle requiert des en-têtes (HTTP-Referer), avez-vous configuré un client personnalisé ?")
else:
    print("Configuration OpenRouter incomplète. Vérifiez OPENROUTER_API_KEY et OPENAI_API_BASE dans votre .env.")
    if not os.environ.get("OPENAI_API_KEY"):
        print("  - OPENAI_API_KEY (dérivée de OPENROUTER_API_KEY) est manquante.")
    if os.environ.get("OPENAI_API_BASE") != "https://openrouter.ai/api/v1":
        print(f"  - OPENAI_API_BASE est '{os.environ.get('OPENAI_API_BASE')}' au lieu de 'https://openrouter.ai/api/v1'.")

```

-----

## 7\. Bonnes Pratiques et Dépannage

### Gestion des erreurs

  * **`PydanticOutputValidationException`**: La sortie du LLM ne correspond pas à votre modèle Pydantic, même après tentatives de correction.
      * **Solutions**: Améliorez le prompt, simplifiez/précisez le modèle Pydantic, ou utilisez un LLM plus performant.
  * **Erreurs d'API (authentification, quotas, nom de modèle incorrect, etc.)**:
      * **Solutions**:
        1.  **Vérifiez attentivement votre fichier `.env`**: Les clés sont-elles exactes ? Sans fautes de frappe ? Pour le bon service ?
        2.  Les variables `OPENAI_API_BASE` (pour OpenRouter) sont-elles correctes ?
        3.  Vos comptes fournisseurs (Google, Mistral, OpenRouter) sont-ils actifs et avec des crédits/quotas suffisants ?
        4.  Le nom du modèle (`llm_engine_name`) est-il exact et supporté ?
  * **`KeyError` / `AttributeError`**: Le LLM n'a pas retourné les champs attendus.

### Optimisation des prompts

  * **Clarté**: Soyez explicite sur la tâche et la structure de sortie attendue.
  * **Exemples (Few-shot)**: Fournir des exemples dans le prompt peut améliorer la performance.
  * **Itération**: Testez et affinez. Un prompt pour Gemini peut nécessiter un ajustement pour Mistral.

### Débogage

  * **Vérifiez le chargement de `.env`**: Ajoutez `print(os.environ.get("MA_CLE_API"))` au début de votre script pour confirmer que les clés sont bien chargées.
  * **Simplicité**: Commencez avec des modèles Pydantic simples et des prompts basiques.
  * **Isolation**: Le problème vient-il de PydanticAI, de la communication API, du prompt, ou du modèle Pydantic ?
  * **Mises à jour**: `pip install --upgrade pydantic-ai openai google-generativeai mistralai python-dotenv`
  * **Communauté**: Consultez les "Issues" sur le GitHub de Pydantic AI.

Si "ça foire à chaque fois" malgré l'utilisation du `.env` :

1.  **Confirmation du chargement du `.env`**: Assurez-vous que `load_dotenv()` est appelé *avant* toute initialisation de `PydanticAI` ou de client LLM, et qu'il trouve bien votre fichier `.env`.
2.  **Exactitude des noms de variables d'environnement**: `GOOGLE_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_BASE` doivent correspondre exactement à ce que PydanticAI et les bibliothèques sous-jacentes attendent.
3.  **Dépendances**: Avez-vous toutes les bibliothèques spécifiques au LLM installé (`google-generativeai`, `mistralai`, `openai`) ?
4.  **Conflits**: Utilisez un environnement virtuel Python (`venv`, `conda`) pour éviter les conflits de versions entre bibliothèques.

Ce document détaillé devrait vous fournir une base solide pour utiliser Pydantic AI avec différents modèles tout en gérant vos clés API de manière sécurisée avec un fichier `.env`. La clé du succès réside souvent dans la configuration correcte des clés et des noms de modèles.