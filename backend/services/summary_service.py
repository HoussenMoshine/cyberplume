from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models
from ..ai_services.factory import create_adapter # MODIFIÉ
from ..utils.text_extractor import extract_text_from_html
from ..config import settings # Pour accéder aux clés API si nécessaire directement ou via le service IA

async def generate_and_save_summary(db_chapter: models.Chapter, db: Session) -> str:
    """
    Génère un résumé pour le contenu d'un chapitre et le sauvegarde dans la base de données.
    Retourne le résumé généré.
    """
    if not db_chapter.content:
        # Ne pas générer de résumé si le contenu est vide, ou retourner une chaîne vide.
        # Ou lever une exception si un contenu est attendu.
        db_chapter.summary = "" # Ou None, selon la logique souhaitée
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
    # Cela pourrait venir de la configuration utilisateur plus tard.
    # Exemple: provider_name = settings.default_summary_provider or "gemini"
    #          model_name = settings.default_summary_model or "gemini-pro" 
    # Pour l'instant, on va supposer qu'on utilise Gemini par défaut pour la summarisation.
    
    provider_name = "gemini" # À rendre configurable plus tard
    ai_service = None
    
    try:
        # DÉBUT BLOC MODIFIÉ
        api_key = None
        model_name = None # Optionnel, dépendra de l'adapter

        if provider_name == "gemini":
            api_key = settings.gemini_api_key
            # Tentative de récupérer un nom de modèle spécifique pour les résumés, sinon le modèle par défaut
            model_name = getattr(settings, 'gemini_summary_model_name', getattr(settings, 'gemini_model_name', None))
        elif provider_name == "mistral":
            api_key = settings.mistral_api_key
            model_name = getattr(settings, 'mistral_summary_model_name', getattr(settings, 'mistral_model_name', None))
        elif provider_name == "openrouter":
            api_key = settings.openrouter_api_key
            model_name = getattr(settings, 'openrouter_summary_model_name', getattr(settings, 'openrouter_default_model', None))
        # Ajouter d'autres providers si nécessaire

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"API key for provider '{provider_name}' not configured."
            )

        ai_service = create_adapter(provider_name, api_key=api_key, model=model_name)
        # FIN BLOC MODIFIÉ
    except ValueError as e:
        # Lever une HTTPException si le fournisseur n'est pas supporté ou mal configuré
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI service provider '{provider_name}' not found or misconfigured: {str(e)}")

    if not ai_service:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not initialize AI service for {provider_name}")

    # Construire le prompt pour la summarisation
    # TODO: Améliorer ce prompt, le rendre configurable, ou utiliser des templates.
    prompt = f"Veuillez fournir un résumé concis du texte suivant, en mettant en évidence les événements clés, l'évolution des personnages et les nouveaux éléments d'intrigue introduits. Le résumé doit faire environ 100 à 150 mots.:\n\n---\n{plain_text_content}\n---\n\nRésumé:"

    try:
        # TODO: Le service IA doit avoir une méthode comme `generate_summary` ou une méthode `generate` plus générique.
        # Pour l'instant, supposons une méthode `generate_text` ou similaire.
        # La méthode exacte dépendra de l'interface de `AiAdapter`.
        # response = await ai_service.generate_text(prompt=prompt, max_tokens=200) # Exemple
        
        # Supposons que la méthode generate_text existe et est asynchrone
        # Si elle n'est pas asynchrone, enlevez await.
        # Si la méthode de l'adaptateur est `generate(prompt, model_name=None, temperature=0.7, max_tokens=150, etc.)`
        # response_data = await ai_service.generate(prompt=prompt, model_name=None, max_tokens=250) # Ajuster max_tokens
        # generated_summary = response_data.get("text", "") # ou une structure de réponse spécifique
        
        # Pour l'instant, utilisons un placeholder pour la réponse de l'IA
        # En attendant de définir la méthode exacte de l'adapter.
        # Exemple avec une méthode générique `generate` qui retourne un dictionnaire
        # ou un objet avec un attribut `text`.
        # Pour l'instant, on va simuler une réponse.
        
        # Simuler un appel à une méthode générique de l'adaptateur
        # Ceci est un placeholder et devra être remplacé par l'appel réel
        # à la méthode de l'adaptateur (ex: generate_text, generate_completion, etc.)
        # et la gestion de sa réponse.
        if hasattr(ai_service, 'generate'): # Si une méthode générique 'generate' existe
            # L'appel à generate peut varier selon l'implémentation de l'adapter
            # (ex: certains peuvent prendre un `model` spécifique, d'autres non si déjà configuré)
            # response_obj = await ai_service.generate(prompt, model_name=None) # ou settings.default_summary_model
            # generated_summary = response_obj.text # ou response_obj['text']
            # Pour l'instant, on va juste utiliser un texte de remplacement
            generated_summary = f"Résumé simulé pour le contenu : '{plain_text_content[:100]}...'"
            print(f"Utilisation de la méthode 'generate' simulée pour le résumé.")

        elif hasattr(ai_service, 'generate_text'): # Si une méthode 'generate_text' existe
            # generated_summary = await ai_service.generate_text(prompt, max_tokens=250)
            generated_summary = f"Résumé simulé (via generate_text) pour : '{plain_text_content[:100]}...'"
            print(f"Utilisation de la méthode 'generate_text' simulée pour le résumé.")
        else:
            raise NotImplementedError(f"Le service IA {provider_name} ne supporte pas une méthode de génération de texte reconnue (generate, generate_text).")

        if not generated_summary.strip():
            # Si le résumé est vide, on peut soit lever une erreur, soit stocker une chaîne vide.
            print(f"Avertissement : Le résumé généré pour le chapitre {db_chapter.id} est vide.")
            generated_summary = "Le résumé n'a pas pu être généré ou le contenu était insuffisant."


    except Exception as e:
        # Gérer les erreurs de l'API IA
        print(f"Erreur lors de la génération du résumé pour le chapitre {db_chapter.id} avec {provider_name}: {str(e)}")
        # Optionnel: ne pas mettre à jour le résumé en cas d'erreur ou mettre un message d'erreur.
        # Pour l'instant, on ne met pas à jour en cas d'erreur de l'IA.
        # On pourrait aussi lever une HTTPException ici pour informer le client.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Erreur du service IA lors de la génération du résumé: {str(e)}")

    db_chapter.summary = generated_summary.strip()
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)

    return db_chapter.summary