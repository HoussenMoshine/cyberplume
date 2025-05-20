import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold, GenerationConfig # Import pour les safety settings et GenerationConfig
from google.api_core.exceptions import GoogleAPIError
import logging
from typing import List, Optional # Importer List et Optional
from .ai_adapter import AIAdapter
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

class GeminiAdapter(AIAdapter):
    def __init__(self, api_key: str, model: str = None): # Accepter model=None initialement
        genai.configure(api_key=api_key)
        # Stocker le modèle demandé, utiliser un défaut dans generate si None
        # Utiliser un modèle plus récent par défaut si possible, ex: gemini-1.5-flash-latest
        self.model = model or "gemini-1.5-flash-latest"
        logging.info(f"GeminiAdapter initialized with model: {self.model}")

    def get_available_models(self) -> list[dict]:
        """Récupère dynamiquement les modèles Gemini disponibles avec leurs metadata."""
        try:
            logging.info("Fetching models from Gemini API...")
            models = genai.list_models()
            gemini_models = []
            for model in models:
                 # Filtrer pour les modèles utilisables pour la génération de texte
                 if 'generateContent' in model.supported_generation_methods:
                     # Utiliser l'ID complet (ex: models/gemini-pro) comme ID unique
                     model_id = model.name
                     gemini_models.append({
                         "id": model_id,
                         "name": model.display_name, # Utiliser display_name si disponible
                         "description": model.description,
                         "version": model.version,
                         # Ajouter d'autres métadonnées utiles si nécessaire
                     })
            logging.info(f"Successfully fetched {len(gemini_models)} usable models from Gemini.")
            return gemini_models
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des modèles Gemini: {str(e)}", exc_info=True) # Log stack trace
            # Retourner une liste vide en cas d'erreur, pas de fallback statique
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
        Génère du texte en utilisant l'API Gemini avec le modèle sélectionné,
        en adaptant le prompt en fonction de l'action, du style (standard ou personnalisé)
        et du contexte des personnages pertinents.
        """
        if not prompt or prompt.strip() == "":
            # Pour generer_scene, un prompt vide est acceptable si d'autres infos sont fournies
            if action != "generer_scene":
                 raise ValueError("Le prompt ne peut pas être vide pour cette action.")
            elif not scene_goal and not characters and not key_elements:
                 raise ValueError("Pour générer une scène sans description, fournissez au moins un objectif, des personnages ou des éléments clés.")


        current_model = self.model # Modèle demandé par le frontend (ou défaut)

        # --- Construction du contexte personnage (si fourni et action pertinente) ---
        character_context_str = ""
        # MODIFIÉ: Inclure 'generer_scene' dans les actions pertinentes pour le contexte personnage détaillé
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
            # NOUVEAU: Prompt amélioré pour la continuation
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
            # NOUVEAU: Prompt amélioré pour la génération de dialogue
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
        # MODIFIÉ: Construction du prompt enrichi pour generer_scene (v4 - character-centric avec contexte détaillé)
        elif action == "generer_scene":
            # Le contexte personnage détaillé est maintenant inclus via character_context_str
            context_parts = []

            if characters:
                # Instruction principale centrée sur le personnage
                context_parts.append(f"Écris une ébauche de scène de roman détaillée du point de vue de {characters[0]} (ou en le mettant en scène de manière centrale si plusieurs personnages sont listés : {', '.join(characters)}).")
                context_parts.append(f"Le personnage principal {'est' if len(characters) == 1 else 'sont'} : {', '.join(characters)}.")
                context_parts.append("Décris ses actions, ses pensées, ou ce qu'il perçoit directement.")
            else:
                # Fallback si aucun personnage n'est fourni
                context_parts.append("Écris une ébauche de scène de roman détaillée du point de vue d'un observateur neutre.")

            # Intégrer les autres éléments comme contexte pour le personnage (si possible)
            if prompt and prompt.strip():
                context_parts.append(f"\nLa scène se déroule dans le contexte suivant : {prompt.strip()}")
            if scene_goal:
                context_parts.append(f"\nL'objectif de la scène est : {scene_goal}")
            if key_elements:
                context_parts.append(f"\nÉléments importants à inclure dans la scène : {key_elements}")

            # Instructions générales finales (plus concises)
            context_parts.append("\nInstructions générales :")
            context_parts.append("- Utilise des descriptions sensorielles.")
            context_parts.append("- Inclus des dialogues si approprié.")
            context_parts.append("- Maintiens la cohérence.")

            context_parts.append("\n\nÉbauche de la scène :")
            # MODIFIÉ: action_prompt est maintenant juste les instructions spécifiques à la scène
            action_prompt = "\n".join(context_parts)
            logging.info(f"Action: {action}. Constructed detailed prompt (v4 - character-centric with detailed context).")
        # --- Fin Prompt v4 ---
        # TODO: Ajouter d'autres actions (decrire_scene, changer_ton...)
        else:
            # Comportement par défaut (si action=None ou inconnue) -> Suggestion/Reformulation générale
            if action:
                 logging.warning(f"Action inconnue '{action}' reçue. Utilisation du prompt de suggestion par défaut.")
            else:
                 logging.info("No specific action provided. Using default suggestion prompt.")
            action_prompt = f'Voici un extrait de texte :\n\n---\n{prompt}\n---\n\nPropose une ou plusieurs reformulations créatives ou des développements possibles pour ce passage. Ne fais pas d\'analyse, écris directement les propositions.'
        # -----------------------------------------------------

        # --- Application du style au prompt (Priorité au style personnalisé) ---
        # Le character_context_str est maintenant toujours inclus au début si pertinent
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
             # Appliquer le style après le contexte personnage et le prompt d'action
             final_prompt = f"{style_instruction}\n\n{base_prompt_with_context}"
        # ------------------------------------

        # --- Configuration des Safety Settings ---
        safety_settings = {
            # Par défaut, utiliser les seuils standards de Gemini
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        # MODIFIÉ: Inclure 'langage_cru' dans l'ajustement des safety settings
        # On ajuste si le style standard est 'adulte' ou 'langage_cru', OU si un style personnalisé est appliqué
        # (car on ne connaît pas la nature du style personnalisé, on relâche un peu la censure par défaut)
        if (style in ['adulte', 'langage_cru']) or custom_style_description:
            log_reason = f"style '{style}'" if style in ['adulte', 'langage_cru'] else "custom style"
            logging.warning(f"Adjusting safety settings (BLOCK_ONLY_HIGH) due to {log_reason}.")
            # Utilisons BLOCK_ONLY_HIGH comme compromis initial.
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        # ---------------------------------------

        # --- Configuration de la Génération (max_tokens, temperature) ---
        generation_config = GenerationConfig()
        if max_tokens is not None:
            generation_config.max_output_tokens = max_tokens
            logging.debug(f"Setting max_output_tokens: {max_tokens}")
        if temperature is not None:
            generation_config.temperature = temperature
            logging.debug(f"Setting temperature: {temperature}")
        # Ajouter d'autres paramètres si nécessaire (top_p, top_k...)
        # -------------------------------------------------------------

        try:
            logging.info(f"Generating text with Gemini model: {current_model} for action: {action or 'default'}, style: {applied_style_type}")
            logging.debug(f"Final prompt sent to Gemini:\n{final_prompt}") # Log le prompt final
            logging.debug(f"Using safety settings: {safety_settings}") # Log les safety settings
            logging.debug(f"Using generation config: {generation_config}") # Log la config

            model_instance = genai.GenerativeModel(current_model)

            # Passer les safety_settings et generation_config à l'appel generate_content
            response = await model_instance.generate_content_async( # Utiliser la version async
                final_prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )

            # Gestion améliorée de la réponse
            # Vérifier d'abord si le contenu a été bloqué
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 block_reason = response.prompt_feedback.block_reason.name # Obtenir le nom de la raison
                 logging.warning(f"Gemini content generation blocked. Reason: {block_reason}")
                 # Essayer de voir si des candidats existent malgré le blocage (parfois le cas)
                 if response.candidates and response.candidates[0].content:
                     logging.warning("Content found in candidates despite block reason. Returning candidate content.")
                     # Attention: ce contenu peut être celui qui a causé le blocage. À utiliser avec prudence.
                     # return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
                     # Préférable de renvoyer une erreur claire à l'utilisateur
                     raise ValueError(f"La génération a été bloquée par Gemini (Raison: {block_reason}).")
                 else:
                     raise ValueError(f"La génération a été bloquée par Gemini (Raison: {block_reason}). Aucun contenu alternatif disponible.")

            # Si non bloqué, extraire le texte
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'parts') and response.parts:
                # Concaténer le texte de toutes les parties
                return "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif response.candidates and response.candidates[0].content: # Vérifier les candidats comme fallback
                 logging.info("Extracting text from response candidates.")
                 return "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            else:
                 logging.error(f"Unexpected or empty response structure from Gemini API: {response}")
                 raise ValueError("Réponse inattendue ou vide de l'API Gemini.")

        except GoogleAPIError as e:
            logging.error(f"Gemini API error during generation with model {current_model}: {e}", exc_info=True)
            raise ValueError(f"Erreur lors de la génération avec Gemini ({current_model}): {str(e)}")
        except Exception as e:
             logging.error(f"Unexpected error during Gemini generation: {e}", exc_info=True)
             raise ValueError(f"Erreur inattendue lors de la génération avec Gemini ({current_model}): {str(e)}")