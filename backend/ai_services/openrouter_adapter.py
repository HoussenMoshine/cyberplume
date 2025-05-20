import requests
import asyncio # Importer asyncio
from .ai_adapter import AIAdapter
import logging # Ajouter logging
from typing import List, Optional # NOUVEAU: Importer List et Optional
# NOUVEAU: Importer CharacterContext pour la signature et l'utilisation
from ..models import CharacterContext

# MODIFIÉ: Ajout des instructions pour les nouveaux styles
STYLE_INSTRUCTIONS = {
    "formel": "Adopte un style d'écriture formel et professionnel.",
    "creatif": "Adopte un style d'écriture créatif, imaginatif et expressif.",
    "technique": "Adopte un style d'écriture technique, précis et factuel.",
    "humoristique": "Adopte un style d'écriture humoristique et léger.",
    "poetique": "Adopte un style d'écriture poétique et lyrique.",
    "sarcastique": "Adopte un ton sarcastique, cynique et pince-sans-rire.", # NOUVEAU
    "adulte": "Adopte un style d'écriture mature, sans censure, autorisant le contenu explicite, érotique ou 'hardcore' si nécessaire pour l'histoire.",
    "langage_cru": "Adopte un style d'écriture très direct et sans filtre, utilisant librement des injures, des mots grossiers et un langage de rue si nécessaire pour le contexte (par exemple, dialogues de gangsters, scènes de conflit intense).", # NOUVEAU
    # 'normal' n'a pas besoin d'instruction spécifique
}

# Optionnel: Configurer les headers recommandés par OpenRouter
OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://github.com/HoussenLandolsi/cyberplume", # Mettre votre URL de projet
    "X-Title": "CyberPlume", # Mettre le nom de votre application
}

class OpenRouterAdapter(AIAdapter):
    def __init__(self, api_key: str, model: str = None): # Accepter model=None initialement
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = model # Stocker le modèle demandé, validation dans generate
        logging.info(f"OpenRouterAdapter initialized with model: {self.model or 'Default will be chosen in generate'}")

    def get_available_models(self) -> list[dict]:
        """Récupère dynamiquement les modèles disponibles depuis l'API OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            **OPENROUTER_HEADERS # Ajouter les headers optionnels
        }
        try:
            logging.info("Fetching models from OpenRouter API...")
            # Utiliser un appel synchrone ici car la méthode n'est pas async
            response = requests.get(f"{self.base_url}/models", headers=headers)
            response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
            data = response.json()
            models = []
            if isinstance(data.get("data"), list):
                for model_data in data["data"]:
                    model_id = model_data.get("id")
                    if model_id:
                        # Essayer d'extraire plus d'infos pour la description
                        context = model_data.get('context_length', 'N/A')
                        pricing_prompt = model_data.get('pricing', {}).get('prompt', 'N/A')
                        pricing_completion = model_data.get('pricing', {}).get('completion', 'N/A')
                        # Construire une description plus informative
                        description_parts = []
                        if context != 'N/A':
                            description_parts.append(f"Context: {context}")
                        if pricing_prompt != 'N/A' or pricing_completion != 'N/A':
                             description_parts.append(f"Price(prompt/completion): ${pricing_prompt}/${pricing_completion} per MTok") # OpenRouter utilise souvent MTok

                        description = ", ".join(description_parts) if description_parts else "No details available"

                        models.append({
                            "id": model_id,
                            "name": model_data.get("name", model_id), # Utiliser le nom fourni, sinon l'ID
                            "description": description
                        })
            else:
                logging.warning(f"Unexpected response structure from OpenRouter API models: {data}")

            logging.info(f"Successfully fetched {len(models)} models from OpenRouter.")
            return models
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching OpenRouter models: {e}", exc_info=True)
            return [] # Retourner liste vide en cas d'erreur
        except Exception as e:
            logging.error(f"Unexpected error fetching OpenRouter models: {e}", exc_info=True)
            return []

    # MODIFIÉ: Signature mise à jour pour inclure character_context
    async def generate(
        self,
        prompt: str,
        action: Optional[str] = None,
        style: Optional[str] = None,
        characters: Optional[List[str]] = None, # Pour generate_scene
        scene_goal: Optional[str] = None, # Pour generate_scene
        key_elements: Optional[str] = None, # Pour generate_scene
        custom_style_description: Optional[str] = None,
        character_context: Optional[List[CharacterContext]] = None, # NOUVEAU
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Génère du texte en utilisant l'API OpenRouter avec le modèle sélectionné,
        en adaptant le prompt en fonction de l'action, du style (standard ou personnalisé)
        et du contexte des personnages pertinents.
        """
        current_model = self.model
        if not current_model:
            # Définir un modèle par défaut si aucun n'est fourni
            current_model = "openai/gpt-3.5-turbo" # Un défaut courant et souvent disponible
            logging.warning(f"No model specified for OpenRouter, defaulting to: {current_model}")
            self.model = current_model # Mettre à jour pour les appels suivants

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
             **OPENROUTER_HEADERS
        }

        # --- Construction du contexte personnage (si fourni et action pertinente) ---
        character_context_str = ""
        if character_context and action in ["continuer", "generer_dialogue", None, "suggest", "reformuler", "raccourcir", "développer", "generer_scene"]: # Inclure None et autres actions générales
            context_lines = ["Contexte des personnages pertinents :"]
            for char in character_context:
                context_lines.append(f"- Nom: {char.name}")
                if char.description:
                    context_lines.append(f"  Description: {char.description}")
                if char.backstory:
                    context_lines.append(f"  Backstory: {char.backstory}")
            character_context_str = "\n".join(context_lines) + "\n\n---\n\n" # Séparateur
            logging.info(f"Injecting character context for action '{action}'.")
        # -----------------------------------------------------------------------

        # --- Construction du prompt basé sur l'action ---
        action_prompt = prompt # Initialisation avec le prompt brut

        if action == "reformuler":
            action_prompt = f'Reformule le texte suivant :\n\n---\n{prompt}\n---\n\nReformulation :'
            logging.info(f"Action: {action}. Using specific prompt.")
        elif action == "raccourcir":
            action_prompt = f'Raccourcis le texte suivant en conservant l\'essentiel :\n\n---\n{prompt}\n---\n\nVersion raccourcie :'
            logging.info(f"Action: {action}. Using specific prompt.")
        elif action == "développer":
            action_prompt = f'Développe l\'idée ou le texte suivant de manière détaillée et cohérente :\n\n---\n{prompt}\n---\n\nDéveloppement :'
            logging.info(f"Action: {action}. Using specific prompt.")
        elif action == "continuer":
            # NOUVEAU: Prompt amélioré pour la continuation (similaire à Gemini)
            action_prompt = f"""Voici un extrait de texte. Écris UNIQUEMENT la suite directe et cohérente, en respectant ces consignes :
1. Ne répète pas le texte fourni
2. Maintiens le style, le ton et la cohérence narrative
3. Tiens compte du contexte des personnages si disponible
4. Fais une continuation fluide et naturelle

Texte à continuer :
---
{prompt}
---

Suite directe :"""
            logging.info(f"Action: {action}. Using improved prompt.")
        elif action == "generer_dialogue":
            # NOUVEAU: Prompt amélioré pour la génération de dialogue (similaire à Gemini)
            action_prompt = f"""À partir de la situation ou du texte suivant, écris un dialogue pertinent et naturel entre les personnages impliqués. Respecte ces consignes :
1. Le dialogue doit être réaliste et correspondre aux personnalités des personnages (si le contexte personnage est fourni).
2. Inclus des didascalies si nécessaire pour les actions ou émotions.
3. Maintiens la cohérence avec le texte fourni.
4. Si aucun personnage n'est explicitement mentionné, suggère un dialogue entre des personnages potentiels pertinents pour la situation.

Situation/Texte :
---
{prompt}
---

Dialogue :"""
            logging.info(f"Action: {action}. Using improved dialogue prompt.")
        elif action == "generer_personnage":
            action_prompt = prompt # Utilise le prompt reçu qui contient déjà les instructions
            logging.info(f"Action: {action}. Using prompt provided by router.")
        # NOUVEAU: Action pour générer une scène (prompt simple pour l'instant pour OpenRouter)
        elif action == "generer_scene":
             # Le contexte personnage n'est PAS injecté ici, car cette action a sa propre logique
             # TODO: Construire un prompt enrichi pour OpenRouter similaire à Gemini
            base_instruction = "Écris une ébauche de scène de roman détaillée."
            context_parts = [base_instruction]
            if prompt and prompt.strip():
                 context_parts.append(f"\nDescription générale :\n{prompt.strip()}")
            # Ajouter les autres infos si on veut les utiliser ici
            # if scene_goal: context_parts.append(f"\nObjectif: {scene_goal}")
            # if characters: context_parts.append(f"\nPersonnages: {', '.join(characters)}")
            # if key_elements: context_parts.append(f"\nÉléments clés: {key_elements}")
            context_parts.append("\n\nÉbauche de la scène :")
            action_prompt = "\n".join(context_parts)
            logging.info(f"Action: {action}. Using basic scene prompt for OpenRouter.")
        # TODO: Ajouter d'autres actions (decrire_scene, changer_ton...)
        else:
            if action:
                 logging.warning(f"Action inconnue '{action}' reçue. Utilisation du prompt de suggestion par défaut.")
            else:
                 logging.info("No specific action provided. Using default suggestion prompt.")
            action_prompt = f'Voici un extrait de texte :\n\n---\n{prompt}\n---\n\nPropose une ou plusieurs reformulations créatives ou des développements possibles pour ce passage. Ne fais pas d\'analyse, écris directement les propositions.'
        # -----------------------------------------------------

        # --- Application du style au prompt (Priorité au style personnalisé) ---
        # MODIFIÉ: Injecter le contexte personnage AVANT le style
        base_prompt_with_context = character_context_str + action_prompt
        final_prompt = base_prompt_with_context # Initialisation
        style_instruction = ""
        applied_style_type = "normal" # Pour le log

        if custom_style_description:
            style_instruction = f"Adopte le style d'écriture suivant : {custom_style_description}"
            logging.info(f"Applying custom style description.")
            applied_style_type = "custom"
        elif style and style != 'normal':
            instruction = STYLE_INSTRUCTIONS.get(style)
            if instruction:
                style_instruction = instruction
                logging.info(f"Applying standard style '{style}'.")
                applied_style_type = style
            else:
                logging.warning(f"Standard style '{style}' unknown, no style instruction applied.")

        if style_instruction:
             # Préfixer l'instruction au prompt utilisateur
             # Appliquer le style après le contexte personnage et le prompt d'action
             final_prompt = f"{style_instruction}\n\n{base_prompt_with_context}"
        # ------------------------------------

        # Définir le payload data ici, APRÈS avoir construit final_prompt
        data = {
            "model": current_model,
            "messages": [{"role": "user", "content": final_prompt}]
            # Ajouter d'autres paramètres si nécessaire (temperature, max_tokens, etc.)
        }
        if temperature is not None:
            data["temperature"] = temperature
            logging.debug(f"Setting temperature: {temperature}")
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
            logging.debug(f"Setting max_tokens: {max_tokens}")
        # OpenRouter n'a pas de paramètre 'safe_prompt' ou 'safety_settings' global.

        try:
            logging.info(f"Generating text with OpenRouter model: {current_model} for action: {action or 'default'}, style: {applied_style_type}")
            logging.debug(f"Final prompt sent to OpenRouter:\n{final_prompt}") # Log le prompt final
            logging.debug(f"Request data: {data}") # Log les données envoyées

            # Utiliser asyncio.to_thread pour exécuter l'appel bloquant requests.post
            response = await asyncio.to_thread(
                requests.post,
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status() # Vérifie les erreurs HTTP
            result = response.json()

            # Vérifier la structure de la réponse
            if result.get("choices") and result["choices"][0].get("message"):
                return result["choices"][0]["message"]["content"]
            else:
                logging.error(f"Unexpected response structure from OpenRouter chat API: {result}")
                raise ValueError("Réponse inattendue de l'API OpenRouter.")

        except requests.exceptions.RequestException as e:
            # Essayer d'extraire plus d'infos de l'erreur si possible
            error_detail = str(e)
            if e.response is not None:
                try:
                    # OpenRouter peut renvoyer des erreurs structurées
                    error_data = e.response.json()
                    error_detail = error_data.get('error', {}).get('message', str(e))
                except Exception:
                    # Si le corps de la réponse n'est pas JSON ou si la structure est différente
                    error_detail = e.response.text if e.response.text else str(e)
            logging.error(f"OpenRouter API error during generation with model {current_model}: {error_detail}", exc_info=True)
            raise ValueError(f"Erreur lors de la génération avec OpenRouter ({current_model}): {error_detail}")
        except Exception as e:
             logging.error(f"Unexpected error during OpenRouter generation: {e}", exc_info=True)
             raise ValueError(f"Erreur inattendue lors de la génération avec OpenRouter ({current_model}): {str(e)}")