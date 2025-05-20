import logging
from typing import Dict, Any # Ajout de Any

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request # Ajout de Request

from backend.ai_services.factory import create_adapter # Correction: Importer create_adapter
from backend.ai_services.ai_adapter import AIAdapter
from backend.utils.text_extractor import extract_text_from_file
from backend.config import Settings, get_settings # Pour accéder aux clés API etc.

router = APIRouter(
    prefix="/api/style",
    tags=["Style Analysis"],
)

logger = logging.getLogger(__name__)

# Dépendance pour obtenir le service IA configuré
# Note: Ceci suppose que la configuration (provider, api_key) est globale pour l'instant.
# Si la sélection du provider est dynamique par requête, il faudra ajuster.
async def get_configured_ai_service(settings: Settings = Depends(get_settings)) -> AIAdapter:
    """Dependency to get the configured AI service based on settings."""
    # Pour l'instant, on prend le premier provider configuré ou un provider par défaut.
    # Idéalement, la configuration indiquerait quel provider utiliser pour cette tâche
    # ou le client pourrait le spécifier. Simplifions pour le moment.
    default_provider = "gemini" # Ou lire depuis settings si défini

    # Récupérer la clé API correspondante depuis les settings
    api_key = None
    if default_provider == "gemini" and settings.gemini_api_key:
        api_key = settings.gemini_api_key
    elif default_provider == "mistral" and settings.mistral_api_key:
        api_key = settings.mistral_api_key
    elif default_provider == "openrouter" and settings.openrouter_api_key:
        api_key = settings.openrouter_api_key
    # Ajouter d'autres providers si nécessaire

    if not api_key:
        logger.error(f"API key for default provider '{default_provider}' not found in settings.")
        raise HTTPException(status_code=500, detail=f"API key for default AI provider '{default_provider}' is not configured.")

    try:
        # Utiliser la fonction create_adapter importée
        # On ne spécifie pas de modèle ici, l'adaptateur utilisera son défaut si nécessaire
        ai_service = create_adapter(provider=default_provider, api_key=api_key, model=None)
        if not ai_service:
            # create_adapter lève une ValueError si le provider n'est pas supporté
            # Ce cas ne devrait pas arriver si la clé API existe
             raise HTTPException(status_code=500, detail=f"Failed to create AI service adapter for '{default_provider}'.")
        return ai_service
    except ValueError as e:
        logger.error(f"Configuration error for AI service {default_provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration error for AI service: {e}")
    except Exception as e:
        logger.error(f"Failed to initialize AI service {default_provider}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to initialize AI service.")


@router.post("/analyze-upload", response_model=Dict[str, str])
async def analyze_style_from_upload(
    request: Request, # Ajout du paramètre Request
    file: UploadFile = File(None), # Changé pour File(None) pour le moment pour voir si le problème vient de la validation du fichier
    ai_service: AIAdapter = Depends(get_configured_ai_service)
):
    """
    Analyzes the writing style of an uploaded document (PDF, DOCX, ODT, TXT).
    """
    logger.info(f"--- ANALYZE STYLE UPLOAD START ---")
    logger.info(f"Request Headers: {dict(request.headers)}") # Log des en-têtes

    form_data: Any = None # Pour stocker les données du formulaire
    try:
        form_data = await request.form()
        logger.info(f"Form data keys: {list(form_data.keys())}")
        if "file" in form_data:
            logger.info(f"Form data 'file' field details: {form_data['file']}")
            # Si 'file' est un UploadFile, on peut logger son filename et content_type
            if isinstance(form_data['file'], UploadFile):
                 logger.info(f"Uploaded file details from form: filename='{form_data['file'].filename}', content_type='{form_data['file'].content_type}'")
            else:
                logger.info(f"Form data 'file' field is not an UploadFile instance, type: {type(form_data['file'])}")
        else:
            logger.warning("Form data does not contain 'file' key.")

    except Exception as e:
        logger.error(f"Error reading form data: {e}", exc_info=True)
        # Ne pas lever d'exception ici pour permettre de voir si le paramètre 'file' est quand même populé

    logger.info(f"FastAPI 'file' parameter: {file}")
    if file:
        logger.info(f"FastAPI 'file' parameter details: filename='{file.filename}', content_type='{file.content_type}'")
    else:
        logger.warning("FastAPI 'file' parameter is None or empty.")
        # Si 'file' est None ici, et que les logs précédents montrent que 'file' était dans form_data,
        # cela pourrait indiquer un problème avec la manière dont FastAPI mappe le champ du formulaire au paramètre.
        # Si 'file' n'était pas dans form_data, le problème est côté client.
        # Si 'file' est None et que request.form() a échoué, le problème est plus bas niveau.
        raise HTTPException(status_code=422, detail="File not provided or form data parsing issue.")


    logger.info(f"Received file upload for style analysis: {file.filename if file else 'No file object'} ({file.content_type if file else 'N/A'})")

    # 1. Read file content
    try:
        file_content = await file.read()
        if not file_content:
            logger.warning(f"Uploaded file is empty: {file.filename}")
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    except Exception as e:
        logger.error(f"Error reading uploaded file {file.filename}: {e}")
        raise HTTPException(status_code=400, detail="Could not read uploaded file.")
    finally:
        if file: # S'assurer que file existe avant d'appeler close
            await file.close()

    # 2. Extract text
    try:
        extracted_text = extract_text_from_file(file_content, file.filename)
        if not extracted_text or extracted_text.isspace():
            logger.warning(f"No text could be extracted from {file.filename}")
            raise HTTPException(status_code=400, detail="No text could be extracted from the uploaded file.")
        # Limit text size to avoid excessive API costs/long processing
        # TODO: Make this limit configurable
        max_chars = 15000
        if len(extracted_text) > max_chars:
            logger.warning(f"Extracted text from {file.filename} truncated to {max_chars} characters.")
            extracted_text = extracted_text[:max_chars]

    except ValueError as e:
        logger.error(f"Text extraction failed for {file.filename}: {e}")
        # Distinguish between unsupported format and other errors
        if "Unsupported file format" in str(e):
            raise HTTPException(status_code=415, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=f"Failed to process file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during text extraction for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during text extraction.")

    # 3. Prepare AI prompt for style analysis
    # TODO: Refine this prompt based on testing
    analysis_prompt = (
        "Analyse le style d'écriture du texte suivant. "
        "Décris ce style de manière concise et objective en utilisant 3 à 5 adjectifs clés "
        "ou une courte phrase descriptive. Cette description doit être directement utilisable "
        "comme instruction pour une autre IA afin qu'elle adopte ce style spécifique. "
        "Ne donne que la description du style, sans phrases d'introduction ou de conclusion.\n\n"
        "TEXTE À ANALYSER:\n"
        "--------------------\n"
        f"{extracted_text}\n"
        "--------------------\n"
        "DESCRIPTION CONCISE DU STYLE:"
    )

    # 4. Call AI service
    try:
        logger.info(f"Sending text from {file.filename} to AI for style analysis using {ai_service.__class__.__name__}...")
        # We might need a specific method in the adapter or use generate with specific parameters
        # For now, let's assume generate can handle this task.
        # We might need to adjust temperature or other parameters for analysis vs generation.
        analyzed_style = await ai_service.generate(
            prompt=analysis_prompt,
            max_tokens=100, # Limit response size for style description
            temperature=0.5 # Lower temperature for more objective analysis
        )
        logger.info(f"Received style analysis result for {file.filename}: {analyzed_style}")

        if not analyzed_style or analyzed_style.isspace():
             logger.warning(f"AI returned empty style analysis for {file.filename}")
             raise HTTPException(status_code=500, detail="AI analysis returned an empty result.")

        # Simple cleaning (optional)
        analyzed_style = analyzed_style.strip()

        return {"analyzed_style": analyzed_style}

    except HTTPException:
         # Re-raise HTTPExceptions from get_configured_ai_service
         raise
    except Exception as e:
        logger.error(f"AI service call failed during style analysis for {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI service failed to analyze style: {e}")