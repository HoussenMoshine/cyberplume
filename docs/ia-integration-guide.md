# Guide d'Intégration Modulaire des Services d'IA

## Table des Matières
- [Guide d'Intégration Modulaire des Services d'IA](#guide-dintégration-modulaire-des-services-dia)
  - [Introduction](#introduction)
    - [Objectif du document](#objectif-du-document)
    - [Philosophie](#philosophie)
  - [Principes d'Architecture](#principes-darchitecture)
    - [Patrons de Conception Clés](#patrons-de-conception-clés)
  - [Partie 1 : Implémentation Backend (Python/FastAPI)](#partie-1--implémentation-backend-pythonfastapi)
    - [1.1 Le Cœur du Système : L'Interface et la Factory](#11-le-cœur-du-système--linterface-et-la-factory)
    - [1.2 L'Adaptateur : Exemples Concrets](#12-ladaptateur--exemples-concrets)
    - [1.3 L'API : Exposer les Fonctionnalités au Frontend](#13-lapi--exposer-les-fonctionnalités-au-frontend)
  - [Partie 2 : Implémentation Frontend (Vue.js)](#partie-2--implémentation-frontend-vuejs)
    - [2.1 Récupérer et Afficher les Modèles](#21-récupérer-et-afficher-les-modèles)
    - [2.2 Gérer les Clés API](#22-gérer-les-clés-api)
    - [2.3 Appeler l'IA](#23-appeler-lia)
  - [Partie 3 : Guide d'Adaptation](#partie-3--guide-dadaptation)
    - [Comment ajouter un nouveau fournisseur d'IA (ex: "Anthro-AI")](#comment-ajouter-un-nouveau-fournisseur-dia-ex-anthro-ai)
    - [Checklist de Configuration pour un Nouveau Projet](#checklist-de-configuration-pour-un-nouveau-projet)
  - [Conclusion](#conclusion)

---
## Introduction

### Objectif du document
Ce document a pour but de fournir un guide technique complet pour l'intégration modulaire et robuste de divers fournisseurs de modèles de langage (LLM) au sein d'une application. Il s'adresse aux développeurs, architectes logiciels et aux intelligences artificielles d'assistance au codage.

### Philosophie
L'approche décrite ici repose sur une philosophie simple : créer un système où l'ajout, le remplacement ou la mise à jour d'un fournisseur d'IA nécessite un effort minimal et prévisible, sans impacter le reste de l'application. La clé est le découplage et la définition d'une interface commune.

## Principes d'Architecture

L'architecture proposée repose sur une séparation claire des responsabilités entre le backend, qui gère toute la logique d'interaction avec les IA, et le frontend, qui se contente de consommer les services exposés par le backend.

```mermaid
graph TD
    subgraph "Navigateur Client"
        direction LR
        Frontend[Application Frontend (Vue, React, etc.)]
    end

    subgraph "Serveur Backend"
        direction LR
        API[API RESTful (FastAPI, Nest.js, etc.)]
        Factory[Adapter Factory]
        Adapters[Adaptateurs Spécifiques]
    end

    subgraph "Services Tiers"
        direction LR
        ServiceA[API Fournisseur A (ex: Gemini)]
        ServiceB[API Fournisseur B (ex: Mistral)]
        ServiceC[API Fournisseur C (ex: OpenRouter)]
    end

    Frontend -- "Appels HTTP (ex: /generate)" --> API;
    API -- "Demande un adaptateur pour 'Fournisseur A'" --> Factory;
    Factory -- "Instancie et retourne GeminiAdapter" --> API;
    API -- "Utilise l'adaptateur" --> Adapters;
    Adapters -- "Appel API normalisé" --> ServiceA;
    Adapters -- "Appel API normalisé" --> ServiceB;
    Adapters -- "Appel API normalisé" --> ServiceC;
```

### Patrons de Conception Clés

-   **Adapter Pattern** : C'est le pilier de cette architecture. Nous définissons une interface `AIAdapter` unique et cohérente dans notre application. Chaque fournisseur d'IA est ensuite encapsulé dans sa propre classe d'adaptateur qui implémente cette interface, traduisant les appels de notre application en requêtes spécifiques que l'API du fournisseur comprend.
-   **Factory Pattern** : Une simple factory est utilisée pour instancier l'adaptateur requis à la volée. Le reste de l'application n'a pas besoin de connaître les classes d'adaptateurs concrètes ; il lui suffit de demander à la factory un adaptateur pour un `provider` donné (par exemple, "gemini").
-   **API RESTful** : Le backend expose des points de terminaison (endpoints) clairs pour que le frontend puisse demander des listes de modèles, effectuer des générations de texte, et gérer la configuration, sans jamais interagir directement avec les services d'IA.

---
### Partie 1 : Implémentation Backend (Python/FastAPI)

Cette section détaille la mise en place de la logique côté serveur. Les exemples sont en Python avec le framework FastAPI, mais les principes sont transposables à d'autres langages et frameworks comme Nest.js.

#### 1.1 Le Cœur du Système : L'Interface et la Factory

Avant d'interagir avec une quelconque API externe, nous devons définir notre propre contrat interne.

**L'Interface `AIAdapter`**

C'est une classe de base abstraite qui garantit que chaque adaptateur que nous créerons aura la même forme et les mêmes méthodes.

*   `generate()`: La méthode principale pour toute génération de texte. Elle prend un ensemble de paramètres normalisés (prompt, style, etc.) que notre application utilise.
*   `get_available_models()`: Une méthode pour récupérer dynamiquement la liste des modèles qu'un fournisseur propose.

**Exemple : `backend/ai_services/ai_adapter.py`**
```python
from abc import ABC, abstractmethod
from typing import List, Optional

# Un modèle Pydantic ou un simple dict peut être utilisé pour le contexte
class CharacterContext:
    name: str
    description: Optional[str]
    backstory: Optional[str]

class AIAdapter(ABC):
    """Classe de base abstraite pour tous les adaptateurs d'IA."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        # ... autres paramètres normalisés ...
        character_context: Optional[List[CharacterContext]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Génère du texte à partir d'un prompt.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[dict]:
        """
        Retourne la liste des modèles disponibles avec leurs métadonnées.
        Chaque modèle doit être un dictionnaire avec au moins 'id' et 'name'.
        """
        pass
```

**La `AdapterFactory`**

C'est une simple fonction qui agit comme un point d'entrée centralisé pour créer des instances d'adaptateurs. Elle mappe une chaîne de caractères (le nom du fournisseur) à la classe d'adaptateur correspondante.

**Exemple : `backend/ai_services/factory.py`**
```python
from .mistral_adapter import MistralAdapter
from .gemini_adapter import GeminiAdapter
from .openrouter_adapter import OpenRouterAdapter

def create_adapter(provider: str, api_key: str, model: str = None):
    """
    Crée et retourne l'adaptateur approprié selon le provider.
    """
    adapters = {
        "mistral": lambda: MistralAdapter(api_key, model),
        "gemini": lambda: GeminiAdapter(api_key, model),
        "openrouter": lambda: OpenRouterAdapter(api_key, model)
    }
    
    if provider not in adapters:
        raise ValueError(f"Provider {provider} non supporté")
        
    return adapters[provider]()
```
---
#### 1.2 L'Adaptateur : Exemples Concrets

C'est ici que la logique de "traduction" opère. Chaque adaptateur implémente l'interface `AIAdapter` mais contient du code spécifique au fournisseur qu'il représente.

**Exemple 1 : Adaptateur avec SDK Client (Gemini)**

Cette approche est courante lorsque le fournisseur propose une bibliothèque cliente officielle.

**`backend/ai_services/gemini_adapter.py`**
```python
import google.generativeai as genai
from .ai_adapter import AIAdapter
import logging

class GeminiAdapter(AIAdapter):
    def __init__(self, api_key: str, model: str = None):
        genai.configure(api_key=api_key)
        self.model = model or "gemini-1.5-flash-latest"

    def get_available_models(self) -> list[dict]:
        try:
            models = genai.list_models()
            # Filtrer et formater la liste des modèles...
            formatted_models = [
                {
                    "id": m.name,
                    "name": m.display_name,
                    "description": m.description
                }
                for m in models if 'generateContent' in m.supported_generation_methods
            ]
            return formatted_models
        except Exception as e:
            logging.error(f"Erreur API Gemini (models): {e}")
            return []

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            model_instance = genai.GenerativeModel(self.model)
            # Construire le prompt final avec les kwargs (style, contexte, etc.)
            final_prompt = f"Instruction de style: {kwargs.get('style', 'normal')}\n\n{prompt}"
            
            response = await model_instance.generate_content_async(final_prompt)
            return response.text
        except Exception as e:
            logging.error(f"Erreur API Gemini (generate): {e}")
            return f"Erreur: {e}"

```

**Exemple 2 : Adaptateur avec API REST Directe (OpenRouter)**

Cette approche est utilisée lorsqu'il n'y a pas de SDK officiel ou que l'on souhaite un contrôle total sur l'appel HTTP.

**`backend/ai_services/openrouter_adapter.py`**
```python
import httpx # Bibliothèque HTTP asynchrone recommandée avec FastAPI
from .ai_adapter import AIAdapter
import logging

class OpenRouterAdapter(AIAdapter):
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = model or "openai/gpt-3.5-turbo"

    def get_available_models(self) -> list[dict]:
        # Utilise 'requests' ou 'httpx' en mode synchrone
        # ... (logique d'appel à GET {self.base_url}/models) ...
        return [] # Placeholder

    async def generate(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # Format de corps de requête compatible OpenAI
        json_data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"Style: {kwargs.get('style', 'normal')}"},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=json_data
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logging.error(f"Erreur API OpenRouter: {e.response.text}")
            return f"Erreur: {e.response.text}"
```

**Exemple 3 : Concept pour Nest.js (TypeScript)**

La même logique peut être appliquée en TypeScript avec des classes et des interfaces.

**`src/ai/gemini.adapter.ts`**
```typescript
import { AIAdapter } from './ai.adapter.interface';
import { GoogleGenerativeAI } from '@google/generative-ai';

export class GeminiAdapter implements AIAdapter {
  private readonly genAI: GoogleGenerativeAI;
  private model: string;

  constructor(apiKey: string, model?: string) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = model || 'gemini-1.5-flash-latest';
  }

  async getAvailableModels(): Promise<any[]> {
    // En TypeScript, la méthode list_models n'existe pas de la même manière.
    // Il faudrait se référer à la documentation de la librairie JS.
    // Pour l'exemple, on retourne une liste statique.
    return [{ id: 'gemini-1.5-flash-latest', name: 'Gemini 1.5 Flash' }];
  }

  async generate(prompt: string, options: any): Promise<string> {
    const modelInstance = this.genAI.getGenerativeModel({ model: this.model });
    const result = await modelInstance.generateContent(prompt);
    const response = await result.response;
    return response.text();
  }
}
```
---
#### 1.3 L'API : Exposer les Fonctionnalités au Frontend

Une fois les adaptateurs prêts, il faut créer les points de terminaison (endpoints) pour que le frontend puisse les utiliser.

**Endpoint pour lister les Modèles**

Cet endpoint prend un nom de fournisseur, utilise la factory pour obtenir le bon adaptateur, et appelle `get_available_models()`.

**Exemple : `backend/routers/analysis.py` (adapté)**
```python
from fastapi import APIRouter, Depends, HTTPException
from ..ai_services.factory import create_adapter
from ..dependencies import get_api_key_for_provider # Fonction qui récupère la clé API

router = APIRouter()

@router.get("/models/{provider}")
def get_models(provider: str, api_key: str = Depends(get_api_key_for_provider)):
    try:
        adapter = create_adapter(provider, api_key)
        models = adapter.get_available_models()
        return {"provider": provider, "models": models}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne: {e}")
```

**Endpoint pour la Génération de Texte**

C'est l'endpoint principal. Il reçoit tous les paramètres de l'utilisateur, récupère l'adaptateur, et appelle sa méthode `generate`.

**Exemple : `backend/routers/analysis.py` (adapté)**
```python
from pydantic import BaseModel

class GenerationRequest(BaseModel):
    provider: str
    model: str
    prompt: str
    style: str = "normal"
    # ... autres options ...

@router.post("/generate")
async def generate_text(request: GenerationRequest, api_key: str = Depends(get_api_key_for_provider)):
    try:
        adapter = create_adapter(request.provider, api_key, request.model)
        generated_text = await adapter.generate(
            prompt=request.prompt,
            style=request.style
            # ... passer les autres options ...
        )
        return {"text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {e}")

```

**Exemples pour Nest.js / Next.js**

**Contrôleur Nest.js : `src/ai/ai.controller.ts`**
```typescript
import { Controller, Get, Post, Param, Body } from '@nestjs/common';
import { AiService } from './ai.service';

@Controller('ai')
export class AiController {
  constructor(private readonly aiService: AiService) {}

  @Get('models/:provider')
  async getModels(@Param('provider') provider: string) {
    return this.aiService.getModels(provider);
  }

  @Post('generate')
  async generateText(@Body() generationDto: any) {
    return this.aiService.generate(generationDto);
  }
}
```

**Route d'API Next.js : `pages/api/generate.js`**
```javascript
import { createAdapter } from '../../lib/ai/factory';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { provider, model, prompt, style } = req.body;
    const apiKey = process.env[`${provider.toUpperCase()}_API_KEY`];

    try {
      const adapter = createAdapter(provider, apiKey, model);
      const text = await adapter.generate(prompt, { style });
      res.status(200).json({ text });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```
---
### Partie 2 : Implémentation Frontend (Vue.js)

Le frontend est responsable de présenter les options à l'utilisateur et d'envoyer les requêtes au backend. Il n'a aucune connaissance directe des API des fournisseurs d'IA.

#### 2.1 Récupérer et Afficher les Modèles

Pour permettre à l'utilisateur de choisir un modèle, le frontend doit d'abord demander la liste des modèles disponibles au backend.

**Le Composable `useAIModels` (Logique Réutilisable)**

En Vue.js, un "composable" est une excellente façon d'encapsuler et de réutiliser de la logique avec état. Ce composable gère l'appel à l'API `/models/{provider}` et stocke les résultats.

**Exemple : `frontend/src/composables/useAIModels.js`**
```javascript
import { ref, reactive } from 'vue';
import axios from 'axios';

export function useAIModels() {
  const availableModels = reactive({}); // Ex: { gemini: [...], mistral: [...] }
  const loadingModels = ref(false);

  const fetchModels = async (provider) => {
    if (!provider || availableModels[provider]) return; // Ne pas recharger

    loadingModels.value = true;
    try {
      const response = await axios.get(`/api/models/${provider}`);
      availableModels[provider] = response.data.models;
    } catch (error) {
      console.error(`Erreur fetch models pour ${provider}:`, error);
      availableModels[provider] = []; // Vider en cas d'erreur
    } finally {
      loadingModels.value = false;
    }
  };

  return { availableModels, loadingModels, fetchModels };
}
```

**Le Composant de Sélection (UI)**

Un composant Vue peut alors utiliser ce composable pour afficher les listes déroulantes.

```html
<template>
  <div>
    <v-select
      label="Fournisseur"
      :items="providers"
      v-model="selectedProvider"
      @update:modelValue="fetchModelsForProvider"
    ></v-select>

    <v-select
      v-if="!loadingModels"
      label="Modèle"
      :items="availableModels[selectedProvider]"
      item-title="name"
      item-value="id"
      v-model="selectedModel"
    ></v-select>
    <p v-else>Chargement des modèles...</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAIModels } from '@/composables/useAIModels';

const { availableModels, loadingModels, fetchModels } = useAIModels();

const selectedProvider = ref('gemini');
const selectedModel = ref(null);

const fetchModelsForProvider = (provider) => {
  selectedModel.value = null; // Réinitialiser le modèle
  fetchModels(provider);
};

// Charger les modèles pour le fournisseur initial
fetchModels(selectedProvider.value);
</script>
```

**Exemple pour React (Hook Personnalisé)**

La même logique en React serait implémentée dans un hook personnalisé.

**`hooks/useAIModels.js`**
```javascript
import { useState, useCallback } from 'react';
import axios from 'axios';

export const useAIModels = () => {
  const [models, setModels] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const fetchModels = useCallback(async (provider) => {
    if (!provider || models[provider]) return;
    setIsLoading(true);
    try {
      const response = await axios.get(`/api/models/${provider}`);
      setModels(prev => ({ ...prev, [provider]: response.data.models }));
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  }, [models]);

  return { models, isLoading, fetchModels };
};
```

#### 2.2 Gérer les Clés API

Un composant dédié permet à l'utilisateur de saisir ses clés API, qui sont ensuite envoyées au backend pour être stockées de manière sécurisée.

**Exemple : `frontend/src/components/ApiKeysManager.vue`**
Ce composant va :
1.  À son montage, appeler `GET /api/api-keys-config/status` pour afficher quelles clés sont déjà configurées.
2.  Lors du clic sur "Sauvegarder", appeler `POST /api/api-keys-config/{provider}` avec la clé en corps de requête.
3.  Lors du clic sur "Supprimer", appeler `DELETE /api/api-keys-config/{provider}`.

#### 2.3 Appeler l'IA

Enfin, pour utiliser l'IA, le frontend appelle l'endpoint `/generate` avec tous les paramètres requis.

**Exemple de fonction d'appel**
```javascript
import axios from 'axios';

async function getAIGeneration(prompt, provider, model, style) {
  try {
    const response = await axios.post('/api/generate', {
      provider,
      model,
      prompt,
      style
    });
    return response.data.text;
  } catch (error) {
    console.error("Erreur de génération IA:", error);
    throw error; // Propager l'erreur pour que le composant appelant puisse la gérer
  }
}
```
---
### Partie 3 : Guide d'Adaptation

Cette section fournit une checklist pratique pour appliquer cette architecture à un nouveau projet ou pour y ajouter un nouveau fournisseur d'IA.

#### Comment ajouter un nouveau fournisseur d'IA (ex: "Anthro-AI")

1.  **Créer l'Adaptateur Backend**
    *   Créez un nouveau fichier : `backend/ai_services/anthro_adapter.py`.
    *   Dans ce fichier, créez une classe `AnthroAdapter(AIAdapter)`.
    *   Implémentez les méthodes `__init__`, `get_available_models`, et `generate` en utilisant le SDK ou l'API REST de "Anthro-AI".

2.  **Mettre à jour la Factory**
    *   Ouvrez `backend/ai_services/factory.py`.
    *   Importez votre nouvelle classe : `from .anthro_adapter import AnthroAdapter`.
    *   Ajoutez une nouvelle entrée dans le dictionnaire `adapters` :
        ```python
        "anthro": lambda: AnthroAdapter(api_key, model)
        ```

3.  **Mettre à jour le Frontend**
    *   Ouvrez le fichier où vos fournisseurs sont listés (ex: `frontend/src/composables/useAIModels.js`).
    *   Ajoutez "anthro" à la liste des fournisseurs, avec un titre et une description.
    *   Mettez à jour le composant de gestion des clés API pour inclure un champ pour "Anthro-AI".

C'est tout. Le reste de l'application fonctionnera avec ce nouveau fournisseur sans aucune autre modification.

#### Checklist de Configuration pour un Nouveau Projet

1.  **Backend :**
    *   [ ] Copier le dossier `backend/ai_services`.
    *   [ ] Créer les routes API (`/models/{provider}`, `/generate`, etc.) qui utilisent la `create_adapter`.
    *   [ ] Mettre en place la gestion des clés API (lecture depuis des variables d'environnement ou une base de données).

2.  **Frontend :**
    *   [ ] Créer un composable ou un hook (`useAIModels`) pour appeler l'endpoint `/models`.
    *   [ ] Créer un composant de sélection pour que l'utilisateur choisisse le fournisseur et le modèle.
    *   [ ] Créer un composant de gestion des clés API.
    *   [ ] Implémenter la fonction d'appel à l'endpoint `/generate`.

---

## Conclusion

Cette architecture basée sur les patrons **Adapter** et **Factory** offre une solution extrêmement flexible et maintenable pour intégrer des services d'IA. En décentralisant la logique spécifique à chaque fournisseur dans des adaptateurs interchangeables, on s'assure que le cœur de l'application reste agnostique et facile à faire évoluer.

**Pistes d'Amélioration :**
*   **Gestion de Cache :** Mettre en cache la liste des modèles pour éviter des appels API répétés.
*   **Fallback Automatique :** Si un appel à un fournisseur échoue, la factory pourrait automatiquement essayer un autre fournisseur de secours.
*   **Stratégies de "Retry" :** Implémenter une logique pour réessayer automatiquement les appels API qui échouent à cause d'erreurs réseau temporaires.