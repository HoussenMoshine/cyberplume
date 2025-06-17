import logging # Ajout du module logging
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.crud_api_keys import get_decrypted_api_key # Import ajouté
from backend.database import get_db
from backend.ai_services.factory import create_adapter
from backend.models import SceneIdeaRequest, SceneIdeaResponse # Ces modèles seront créés ensuite
from backend.config import Settings, get_settings

router = APIRouter()

@router.post("/scene/generate", response_model=SceneIdeaResponse)
async def generate_scene_ideas(
    request_data: SceneIdeaRequest = Body(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Generates scene ideas based on the provided prompt and parameters.
    """
    logging.info(f"Received scene idea generation request: {request_data}")
    try:
        logging.info(f"Attempting to create AI adapter for provider: {request_data.ai_provider}, model: {request_data.model}")
        
        # Nouvelle logique de récupération de clé API
        logging.info(f"Attempting to retrieve API key for provider '{request_data.ai_provider}' using get_decrypted_api_key.")
        api_key_value = get_decrypted_api_key(db=db, provider_name=request_data.ai_provider, settings_fallback=settings)
        
        if api_key_value:
            logging.info(f"API key for '{request_data.ai_provider}' found.")
        else:
            # Ce log est utile pour confirmer que get_decrypted_api_key a retourné None.
            # La vérification ci-dessous lèvera l'exception si la clé n'est toujours pas trouvée.
            logging.warning(f"API key for '{request_data.ai_provider}' not found by get_decrypted_api_key. This will likely result in an error.")

        # Vérification existante (et toujours nécessaire) si la clé n'a pas été trouvée
        if not api_key_value:
            # Note: get_decrypted_api_key retourne None si le provider n'est pas supporté ou si la clé n'est ni en DB ni en settings.
            # On pourrait vouloir une erreur plus spécifique si le provider n'est pas dans SUPPORTED_PROVIDERS (de crud_api_keys)
            # mais pour l'instant, cette erreur générique pour clé manquante est conservée.
            raise HTTPException(status_code=500, detail=f"Clé API pour '{request_data.ai_provider}' non configurée ou fournisseur non supporté.")

        # CORRECTION: Retrait de l'argument 'settings' qui n'est pas attendu par create_adapter
        ai_service = create_adapter(
            provider=request_data.ai_provider,
            api_key=api_key_value,
            model=request_data.model
        )

        # Construire un prompt détaillé pour le service IA
        prompt_parts = [
            f"Génère des idées de scènes pour une histoire. Chaque idée doit être une description riche et détaillée d'au moins 50 mots, fournissant une base solide pour l'écriture.",
            f"Genre: {request_data.genre}",
            f"Thème principal: {request_data.main_theme}",
            f"Éléments clés à inclure: {', '.join(request_data.key_elements) if request_data.key_elements else 'Non spécifié'}",
            f"Style d'écriture souhaité: {request_data.writing_style}",
            f"Ton: {request_data.tone}",
            f"Nombre d'idées souhaitées: {request_data.number_of_ideas}",
            f"Contexte général de l'histoire (si fourni): {request_data.story_context or 'Non fourni'}"
        ]
        full_prompt = "\n".join(prompt_parts)

        logging.debug(f"Full prompt for scene ideas: {full_prompt}")
        logging.info(f"Calling AI service. Provider: {request_data.ai_provider}, Model: {request_data.model}, Max Tokens: {settings.default_max_tokens_scene_ideas}, Temperature: {request_data.temperature}")
        generated_ideas_raw = await ai_service.generate(
            prompt=full_prompt,
            max_tokens=settings.default_max_tokens_scene_ideas,
            temperature=request_data.temperature,
            action="generer_idees_scene" # Action spécifique pour utiliser le prompt tel quel
            # RAPPEL: Le paramètre 'action' manque ici et pourrait être nécessaire.
            # À investiguer après avoir résolu le problème de clé/init.
        )
        logging.info(f"Raw response from AI for scene ideas: {generated_ideas_raw}")

        # Simuler la séparation des idées si le LLM retourne un bloc de texte
        if isinstance(generated_ideas_raw, str):
            ideas = [idea.strip() for idea in generated_ideas_raw.split("\n\n") if idea.strip()]
            ideas = ideas[:request_data.number_of_ideas]
        elif isinstance(generated_ideas_raw, list):
            ideas = generated_ideas_raw[:request_data.number_of_ideas]
        else:
            ideas = ["Erreur lors de la récupération des idées ou format inattendu."]


        return SceneIdeaResponse(ideas=ideas)

    except ValueError as ve:
        logging.error(f"ValueError in generate_scene_ideas: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.exception(f"Unexpected error in generate_scene_ideas: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate scene ideas due to an unexpected server error.")