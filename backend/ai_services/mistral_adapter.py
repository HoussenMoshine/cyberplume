from mistralai import Mistral # MODIFIÉ: Importation de la nouvelle classe client
# from mistralai.models.models import ModelList # Ce type spécifique n'est plus nécessaire si on itère sur response.data
from .ai_adapter import AIAdapter
import logging
from typing import List, Optional
import asyncio
from ..models import CharacterContext

STYLE_INSTRUCTIONS = {
    "formel": "Adopte un style d'écriture formel et professionnel.",
    "creatif": "Adopte un style d'écriture créatif, imaginatif et expressif.",
    "technique": "Adopte un style d'écriture technique, précis et factuel.",
    "humoristique": "Adopte un style d'écriture humoristique et léger.",
    "poetique": "Adopte un style d'écriture poétique et lyrique.",
    "sarcastique": "Adopte un ton sarcastique, cynique et pince-sans-rire.",
    "adulte": "Adopte un style d'écriture mature, sans censure, autorisant le contenu explicite, érotique ou 'hardcore' si nécessaire pour l'histoire.",
    "langage_cru": "Adopte un style d'écriture très direct et sans filtre, utilisant librement des injures, des mots grossiers et un langage de rue si nécessaire pour le contexte (par exemple, dialogues de gangsters, scènes de conflit intense).",
}

class MistralAdapter(AIAdapter):
    def __init__(self, api_key: str, model: str = None):
        self.client = Mistral(api_key=api_key) # MODIFIÉ: Utilisation de la nouvelle classe Mistral
        self.model = model
        logging.info(f"MistralAdapter initialized with new client, model: {self.model or 'Default will be chosen in generate'}")

    def get_available_models(self) -> list[dict]:
        """Récupère dynamiquement les modèles disponibles depuis l'API Mistral."""
        try:
            logging.info("Fetching models from Mistral API (using client.models.list())...")
            response = self.client.models.list() # MODIFIÉ: Appel via client.models.list()
            models = []
            if hasattr(response, 'data') and isinstance(response.data, list):
                for model_data in response.data:
                    model_id = getattr(model_data, 'id', None)
                    if model_id:
                        models.append({
                            "id": model_id,
                            "name": model_id, 
                            "description": f"Propriétaire: {getattr(model_data, 'owned_by', 'N/A')}, Créé: {getattr(model_data, 'created', 'N/A')}",
                        })
                    else:
                        logging.warning(f"Skipping model data without id: {model_data}")
            else:
                 logging.warning(f"Unexpected response structure from Mistral API client.models.list(): {response}")

            logging.info(f"Successfully fetched {len(models)} models from Mistral.")
            return models
        except Exception as e:
            logging.error(f"Error fetching Mistral models: {e}", exc_info=True)
            return []

    async def generate(
        self,
        prompt: str,
        action: Optional[str] = None,
        style: Optional[str] = None,
        characters: Optional[List[str]] = None,
        scene_goal: Optional[str] = None,
        key_elements: Optional[str] = None,
        custom_style_description: Optional[str] = None,
        character_context: Optional[List[CharacterContext]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        current_model = self.model
        if not current_model:
            current_model = "mistral-small-latest" 
            logging.warning(f"No model specified for Mistral, defaulting to: {current_model}")

        character_context_str = ""
        if character_context and action in ["continuer", "generer_dialogue", None, "suggest", "reformuler", "raccourcir", "développer", "generer_scene"]:
            context_lines = ["Contexte des personnages pertinents :"]
            for char in character_context:
                context_lines.append(f"- Nom: {char.name}")
                if char.description:
                    context_lines.append(f"  Description: {char.description}")
                if char.backstory:
                    context_lines.append(f"  Backstory: {char.backstory}")
            character_context_str = "\n".join(context_lines) + "\n\n---\n\n"
            logging.info(f"Injecting character context for action '{action}'.")

        action_prompt = prompt
        # ... (logique de construction de action_prompt reste la même) ...
        if action == "reformuler":
            action_prompt = f'Reformule le texte suivant :\n\n---\n{prompt}\n---\n\nReformulation :'
        elif action == "raccourcir":
            action_prompt = f'Raccourcis le texte suivant en conservant l\'essentiel :\n\n---\n{prompt}\n---\n\nVersion raccourcie :'
        elif action == "développer":
            action_prompt = f'Développe l\'idée ou le texte suivant de manière détaillée et cohérente :\n\n---\n{prompt}\n---\n\nDéveloppement :'
        elif action == "continuer":
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
        elif action == "generer_dialogue":
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
        elif action == "generer_personnage":
            action_prompt = prompt
        elif action == "generer_scene":
            base_instruction = "Écris une ébauche de scène de roman détaillée."
            context_parts = [base_instruction]
            if prompt and prompt.strip():
                 context_parts.append(f"\nDescription générale :\n{prompt.strip()}")
            context_parts.append("\n\nÉbauche de la scène :")
            action_prompt = "\n".join(context_parts)
        else: 
            action_prompt = f'Voici un extrait de texte :\n\n---\n{prompt}\n---\n\nPropose une ou plusieurs reformulations créatives ou des développements possibles pour ce passage. Ne fais pas d\'analyse, écris directement les propositions.'

        base_prompt_with_context = character_context_str + action_prompt
        final_prompt_for_system = base_prompt_with_context 
        system_message_content = "" 

        if custom_style_description:
            system_message_content = f"Adopte le style d'écriture suivant : {custom_style_description}"
            logging.info(f"Applying custom style description as system message.")
        elif style and style != 'normal':
            instruction = STYLE_INSTRUCTIONS.get(style)
            if instruction:
                system_message_content = instruction
                logging.info(f"Applying standard style '{style}' as system message.")
            else:
                logging.warning(f"Standard style '{style}' unknown, no system style instruction applied.")
        
        messages = []
        if system_message_content:
            messages.append({"role": "system", "content": system_message_content})
        messages.append({"role": "user", "content": final_prompt_for_system})

        # Préparer les arguments pour l'appel API, en s'assurant de ne passer que les non-None
        api_params = {
            "model": current_model,
            "messages": messages
        }
        if max_tokens is not None:
            api_params["max_tokens"] = max_tokens
        if temperature is not None:
            api_params["temperature"] = temperature
        
        # safe_mode (anciennement safe_prompt) est géré par défaut par le client.
        # Si une désactivation explicite est nécessaire pour certains styles,
        # il faudrait vérifier comment le client v1.x le gère (souvent un paramètre booléen).
        # Par exemple: api_params["safe_mode"] = False (si le paramètre existe)
        if style in ["adulte", "langage_cru"] or custom_style_description:
            # Pour la v1.x, le paramètre est `safe_prompt` (bool)
            api_params["safe_prompt"] = False # Tentative de désactivation du mode sécurisé
            logging.info("Attempting to set safe_prompt=False for explicit style.")
        else:
            api_params["safe_prompt"] = True # S'assurer qu'il est activé par défaut autrement

        logging.debug(f"Calling Mistral API with: {api_params}")

        try:
            # Utiliser client.chat.complete_async car notre méthode generate est async
            chat_response = await self.client.chat.complete_async(**api_params) # MODIFIÉ: Appel API corrigé

            if chat_response.choices and len(chat_response.choices) > 0:
                response_content = chat_response.choices[0].message.content
                logging.info(f"Mistral response received. Length: {len(response_content)}")
                return response_content.strip()
            else:
                logging.error("Mistral API response did not contain expected choices.")
                return "Erreur: Réponse inattendue de l'API Mistral."
        except Exception as e:
            logging.error(f"Error during Mistral API call: {e}", exc_info=True)
            return f"Erreur lors de l'appel à l'API Mistral: {str(e)}"
