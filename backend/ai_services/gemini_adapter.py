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
            for model_obj in models: # Renommé model en model_obj pour éviter conflit avec self.model
                 # Filtrer pour les modèles utilisables pour la génération de texte
                 if 'generateContent' in model_obj.supported_generation_methods:
                     # Utiliser l'ID complet (ex: models/gemini-pro) comme ID unique
                     model_id = model_obj.name
                     gemini_models.append({
                         "id": model_id,
                         "name": model_obj.display_name, # Utiliser display_name si disponible
                         "description": model_obj.description,
                         "version": model_obj.version,
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


        current_model_name = self.model # Modèle demandé par le frontend (ou défaut)

        # --- Construction du contexte personnage (si fourni et action pertinente) ---
        character_context_str = ""
        # MODIFIÉ: Inclure 'generer_scene' et 'generer_idees_scene' dans les actions pertinentes pour le contexte personnage détaillé
        if character_context and action in ["continuer", "generer_dialogue", None, "suggest", "reformuler", "raccourcir", "développer", "generer_scene", "generer_idees_scene"]:
            context_lines = ["Contexte des personnages pertinents :"]
            for char_ctx in character_context: # Renommé char en char_ctx
                context_lines.append(f"- Nom: {char_ctx.name}")
                if char_ctx.description:
                    context_lines.append(f"  Description: {char_ctx.description}")
                if char_ctx.backstory:
                    context_lines.append(f"  Backstory: {char_ctx.backstory}")
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
        elif action == "generer_idees_scene": # Correction d'indentation ici
            action_prompt = prompt # Utilise le prompt reçu qui est déjà détaillé
            logging.info(f"Action: {action}. Using prompt provided by router directly.")
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
                logging.info(f"Applying standard style: {style}")
                applied_style_type = style
            else:
                logging.warning(f"Style standard '{style}' non reconnu. Utilisation du style normal.")
        
        if style_instruction:
            final_prompt = f"{style_instruction}\n\n---\n\n{final_prompt}"
            logging.info(f"Style instruction applied. Final style type: {applied_style_type}")

        # Configuration de la génération
        generation_config = GenerationConfig(
            candidate_count=1, # On ne veut qu'une seule proposition pour l'instant
            # stop_sequences=["fin_generation"], # Exemple, à adapter
            max_output_tokens=max_tokens or 1024, # Valeur par défaut si non fournie
            temperature=temperature if temperature is not None else 0.7 # Valeur par défaut si non fournie
            # top_p=0.9, # Exemple
            # top_k=40   # Exemple
        )
        logging.debug(f"Setting max_output_tokens: {generation_config.max_output_tokens}")
        logging.debug(f"Setting temperature: {generation_config.temperature}")


        # Définir les safety settings pour autoriser plus de contenu si le style le demande
        # BLOCK_NONE permet tout, BLOCK_ONLY_HIGH bloque peu, BLOCK_MEDIUM_AND_ABOVE est plus strict.
        # Par défaut, on est plus permissif, mais on pourrait ajuster en fonction du style.
        safety_threshold = HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
        if style in ["adulte", "langage_cru"]:
            safety_threshold = HarmBlockThreshold.BLOCK_NONE # Plus permissif pour ces styles
            logging.info(f"Using more permissive safety settings (BLOCK_NONE) for style '{style}'.")
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: safety_threshold,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: safety_threshold,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: safety_threshold,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: safety_threshold,
        }
        logging.debug(f"Using safety settings: {safety_settings}")
        logging.debug(f"Using generation config: {generation_config}")


        try:
            logging.info(f"Generating text with Gemini model: {current_model_name} for action: {action or 'default'}, style: {applied_style_type}")
            logging.debug(f"Final prompt sent to Gemini:\n{final_prompt}")
            
            model_instance = genai.GenerativeModel(
                model_name=current_model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            response = await model_instance.generate_content_async(final_prompt) # Utiliser generate_content_async

            # Gestion de la réponse
            if response.parts:
                # logging.debug(f"Gemini response parts: {response.parts}")
                # S'assurer que la réponse est bien du texte et la retourner
                # Concaténer toutes les parties de texte si elles existent
                text_parts = [part.text for part in response.parts if hasattr(part, 'text')]
                generated_text = "".join(text_parts)
                
                # Vérifier si le contenu a été bloqué par les filtres de sécurité
                if not generated_text and response.prompt_feedback and response.prompt_feedback.block_reason:
                    block_reason_message = response.prompt_feedback.block_reason_message or "Contenu bloqué par les filtres de sécurité."
                    logging.warning(f"Gemini content generation blocked. Reason: {response.prompt_feedback.block_reason}. Message: {block_reason_message}")
                    # Lever une exception spécifique ou retourner un message d'erreur clair
                    raise GoogleAPIError(f"Génération de contenu bloquée par les filtres de sécurité: {block_reason_message}")

                logging.info("Text generated successfully by Gemini.")
                # logging.debug(f"Generated text (first 100 chars): {generated_text[:100]}")
                return generated_text
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                # Gérer le cas où le prompt lui-même est bloqué
                block_reason_message = response.prompt_feedback.block_reason_message or "Prompt bloqué par les filtres de sécurité."
                logging.warning(f"Gemini prompt blocked. Reason: {response.prompt_feedback.block_reason}. Message: {block_reason_message}")
                raise GoogleAPIError(f"Prompt bloqué par les filtres de sécurité: {block_reason_message}")
            else:
                # Cas où il n'y a pas de parts et pas de blocage de prompt explicite (inattendu)
                logging.warning("Gemini response has no parts and no explicit prompt block reason.")
                # logging.debug(f"Full Gemini response object: {response}")
                return "Réponse vide ou inattendue de l'IA."


        except GoogleAPIError as e:
            logging.error(f"Une erreur API Google est survenue: {e}", exc_info=True)
            raise  # Re-lever l'exception pour qu'elle soit gérée par le routeur
        except Exception as e:
            logging.error(f"Erreur inattendue lors de la génération de texte avec Gemini: {e}", exc_info=True)
            raise # Re-lever pour gestion par le routeur