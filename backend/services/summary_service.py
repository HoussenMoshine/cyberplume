from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models
from ..ai_services.factory import create_adapter
from ..utils.text_extractor import extract_text_from_html
from ..config import settings # Pour accéder aux clés API via fallback
from ..crud_api_keys import get_decrypted_api_key # NOUVEL IMPORT

async def generate_and_save_summary(db_chapter: models.Chapter, db: Session) -> str:
    """
    Génère un résumé pour le contenu d'un chapitre et le sauvegarde dans la base de données.
    Retourne le résumé généré.
    """
    if not db_chapter.content:
        db_chapter.summary = "" 
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        return ""

    plain_text_content = extract_text_from_html(db_chapter.content)

    if not plain_text_content.strip():
        db_chapter.summary = ""
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        return ""

    # TODO: Déterminer dynamiquement le fournisseur et le modèle IA à utiliser.
    # Pour l'instant, utilisons des valeurs par défaut ou celles configurées globalement.
    provider_name = "gemini" # À rendre configurable plus tard
    ai_service = None
    model_name = None # Initialiser model_name
    
    try:
        # MODIFIÉ: Utiliser get_decrypted_api_key pour récupérer la clé API
        api_key = get_decrypted_api_key(db, provider_name, settings_fallback=settings)

        # La logique pour model_name peut rester pour déterminer un modèle spécifique au résumé
        # ou un modèle par défaut pour le fournisseur, lu depuis settings.
        if provider_name == "gemini":
            model_name = getattr(settings, 'gemini_summary_model_name', getattr(settings, 'gemini_model_name', None))
        elif provider_name == "mistral":
            model_name = getattr(settings, 'mistral_summary_model_name', getattr(settings, 'mistral_model_name', None))
        elif provider_name == "openrouter":
            model_name = getattr(settings, 'openrouter_summary_model_name', getattr(settings, 'openrouter_default_model', None))
        # Ajouter d'autres providers si nécessaire pour model_name

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # ou 401/403 si on considère que c'est une auth manquante
                detail=f"API key for provider '{provider_name}' not configured in DB or .env."
            )

        ai_service = create_adapter(provider_name, api_key=api_key, model=model_name)
    except ValueError as e: # Erreur de create_adapter si provider non supporté
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI service provider '{provider_name}' not found or misconfigured: {str(e)}")
    except HTTPException as e: # Propage les HTTPExceptions (comme celle de `if not api_key`)
        raise e
    except Exception as e: # Autres erreurs lors de la récupération de clé ou création d'adapter
        print(f"Erreur inattendue lors de l'initialisation du service IA pour {provider_name}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error initializing AI service for {provider_name}: {str(e)}")


    if not ai_service: # Double vérification, devrait être couvert par les exceptions ci-dessus
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not initialize AI service for {provider_name}")

    prompt = f"Veuillez fournir un résumé concis du texte suivant, en mettant en évidence les événements clés, l'évolution des personnages et les nouveaux éléments d'intrigue introduits. Le résumé doit faire environ 100 à 150 mots.:\n\n---\n{plain_text_content}\n---\n\nRésumé:"

    try:
        # Placeholder pour l'appel réel - À REMPLACER
        generated_summary = ""
        if hasattr(ai_service, 'generate'):
            # response_obj = await ai_service.generate(prompt, model_name=model_name) # model_name est déjà passé à create_adapter
            response_obj = await ai_service.generate(prompt) # Supposant que le modèle est déjà configuré dans l'adaptateur
            generated_summary = response_obj.text if hasattr(response_obj, 'text') else str(response_obj)
            print(f"Utilisation de la méthode 'generate' pour le résumé.")
        elif hasattr(ai_service, 'generate_text'):
            # generated_summary = await ai_service.generate_text(prompt, max_tokens=250)
            generated_summary = await ai_service.generate_text(prompt) # Supposant que le modèle est déjà configuré
            print(f"Utilisation de la méthode 'generate_text' pour le résumé.")
        else:
            # Si on arrive ici, c'est que l'adaptateur n'a pas les méthodes attendues,
            # même si create_adapter a réussi. Cela pourrait être un problème de l'adaptateur lui-même.
            # Ou, si on veut garder le placeholder pour l'instant :
            print(f"AVERTISSEMENT: Le service IA {provider_name} ne supporte pas une méthode de génération reconnue (generate, generate_text). Utilisation d'un résumé simulé.")
            generated_summary = f"Résumé simulé pour le contenu : '{plain_text_content[:100]}...'"
            # raise NotImplementedError(f"Le service IA {provider_name} ne supporte pas une méthode de génération de texte reconnue (generate, generate_text).")


        if not generated_summary.strip():
            print(f"Avertissement : Le résumé généré pour le chapitre {db_chapter.id} est vide.")
            generated_summary = "Le résumé n'a pas pu être généré ou le contenu était insuffisant."

    except Exception as e:
        print(f"Erreur lors de la génération du résumé pour le chapitre {db_chapter.id} avec {provider_name}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Erreur du service IA lors de la génération du résumé: {str(e)}")

    db_chapter.summary = generated_summary.strip()
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)

    return db_chapter.summary