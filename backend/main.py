from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware

# Utilisation exclusive d'imports relatifs pour les modules locaux
from .ai_services import AIAdapter, create_adapter
from .config import settings
# MODIFIÉ: GenerationRequest inclut maintenant aussi character_context
from .models import GenerationRequest
# MODIFIÉ: Ajout de l'import pour les routeurs export, scenes, analysis, style et agents
from .routers import projects, characters, export, scenes, analysis, style, api_keys_config # agents supprimé, api_keys_config ajouté
from .routers import projects, characters, export, scenes, analysis, style, api_keys_config, ideas # Ajout de ideas
from .database import create_tables # Importer la fonction pour créer les tables
import time
import logging
from typing import Optional # Ajouté pour Optional[str]

# Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s') # Géré par log_config.yaml

app = FastAPI(
    title="CyberPlume",
    description="API principale pour l'application CyberPlume",
    version="0.1.0",
    debug=settings.debug
)

# Événement de démarrage pour créer les tables de la base de données
@app.on_event("startup")
async def startup_event():
    logging.info("Application startup: Creating database tables...")
    create_tables()
    logging.info("Database tables checked/created.")
# Cette parenthèse était en trop

# Configuration du port
import uvicorn
if __name__ == "__main__":
    # Note: Ce bloc n'est généralement pas exécuté par uvicorn backend.main:app
    # Il est utile si on lance directement `python backend/main.py` (ce qui causerait des erreurs d'import relatif)
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) # Modifié pour correspondre à la commande uvicorn

# Rate limiting
last_access = {}
RATE_LIMIT = 1  # 1 request per second

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Assurez-vous que c'est le bon port frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Inclure les routeurs
app.include_router(projects.router)
app.include_router(characters.router) # Inclusion du routeur pour les personnages
app.include_router(export.router) # MODIFIÉ: Inclusion du routeur pour l'export
app.include_router(scenes.router) # NOUVEAU: Inclusion du routeur pour les scènes (déjà présent, vérifié)
app.include_router(analysis.router) # NOUVEAU: Inclusion du routeur pour l'analyse
app.include_router(style.router) # NOUVEAU: Inclusion du routeur pour l'analyse de style
app.include_router(api_keys_config.router) # NOUVEAU: Inclusion du routeur pour la configuration des clés API
app.include_router(ideas.router, prefix="/ideas", tags=["ideas"]) # NOUVEAU: Inclusion du routeur pour la génération d'idées

@app.get("/")
async def root():
    return {"message": "Bienvenue sur CyberPlume API"}

from sqlalchemy.orm import Session # Ajout pour Depends(get_db)
from .database import get_db # Assurer l'import de get_db
from . import crud_api_keys # Importer le module crud_api_keys

@app.get("/status")
async def get_application_status(db: Session = Depends(get_db)): # Injection de la session DB # RENOMMÉ ICI
    """Endpoint de statut avec vérification des configurations des clés API depuis la DB."""
    
    # Récupérer le statut des clés API depuis la base de données
    api_keys_status_db = crud_api_keys.list_api_keys_status(db)
    
    # Convertir la liste en dictionnaire pour la réponse
    providers_configured_db = {
        item.provider_name: item.has_key_set for item in api_keys_status_db
    }

    # Vérifier également les clés du .env comme fallback ou information supplémentaire (optionnel)
    # Pour l'instant, on se fie principalement à ce qui est dans la DB pour "providers_configured"
    # providers_env = {
    #     "mistral": bool(settings.mistral_api_key),
    #     "gemini": bool(settings.gemini_api_key),
    #     "openrouter": bool(settings.openrouter_api_key)
    # }

    return {
        "status": "ok",
        "version": "0.1.0",
        "debug": settings.debug,
        "providers_configured": providers_configured_db, # Utilise le statut de la DB
        "api_key_set": bool(settings.api_key) # Clé API de l'application elle-même
    }

@app.get("/models/{provider}")
async def get_model_info(
    provider: str,
    x_api_key: str = Header(None, description="Clé API d'authentification"),
    db: Session = Depends(get_db) # Injection de la session DB
):
    """
    Retourne les informations sur les modèles disponibles pour un provider donné
    avec leurs metadata (description, capacités, etc.)
    Tente de récupérer la clé API depuis la DB, puis fallback sur .env.
    """
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    provider_lower = provider.lower()
    if provider_lower not in crud_api_keys.SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Provider non supporté: {provider}")

    api_key_to_use: Optional[str] = None
    key_source = "N/A"

    # 1. Essayer de récupérer la clé depuis la base de données
    api_key_from_db = crud_api_keys.get_decrypted_api_key(db, provider_lower)
    if api_key_from_db:
        api_key_to_use = api_key_from_db
        key_source = "database"
        logging.info(f"Using API key from database for provider: {provider_lower}")
    else:
        # 2. Fallback sur la clé du fichier .env (via settings)
        if provider_lower == "mistral":
            api_key_to_use = settings.mistral_api_key
        elif provider_lower == "gemini":
            api_key_to_use = settings.gemini_api_key
        elif provider_lower == "openrouter":
            api_key_to_use = settings.openrouter_api_key
        
        if api_key_to_use:
            key_source = "env_file"
            logging.info(f"Using API key from .env file for provider: {provider_lower}")
        else:
            logging.warning(f"Aucune clé API trouvée ni dans la DB ni dans .env pour le provider: {provider_lower}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clé API non configurée pour le provider: {provider}. Veuillez la configurer."
            )

    try:
        logging.info(f"Creating adapter for provider: {provider_lower} using key from {key_source}")
        adapter = create_adapter(provider_lower, api_key_to_use)
        models = adapter.get_available_models()
        logging.debug(f"Retrieved models for {provider_lower}: {models}")

        return {
            "provider": provider_lower,
            "status": "active", # Pourrait être amélioré pour indiquer la source de la clé
            "key_source": key_source,
            "models": models
        }
    except ValueError as e: # Erreurs de create_adapter ou get_available_models
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des modèles pour {provider_lower}: {str(e)}")
        logging.exception("Stack trace complet:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne du serveur lors de la récupération des modèles pour {provider_lower}.")

@app.post("/generate/text")
async def generate_text(
    request: GenerationRequest, 
    x_api_key: str = Header(None),
    db: Session = Depends(get_db) # Injection de la session DB
):
    """
    Génère du texte en utilisant le provider, le modèle, l'action et le style spécifiés.
    Tente de récupérer la clé API depuis la DB, puis fallback sur .env.
    """
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    provider_lower = request.provider.lower()
    if provider_lower not in crud_api_keys.SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Provider non supporté: {request.provider}")

    logging.info(
        f"generate_text: provider={provider_lower}, model={request.model}, "
        f"action={request.action}, style={request.style}, "
        f"custom_style={bool(request.custom_style_description)}, "
        f"character_context_present={bool(request.character_context)}"
    )
    if request.action == "generer_scene":
        logging.info(f"  Scene Goal: {request.scene_goal}")
        logging.info(f"  Characters: {request.characters}")
        logging.info(f"  Key Elements: {request.key_elements}")
    elif request.character_context:
         logging.info(f"  Character Context: {[c.name for c in request.character_context]}")

    api_key_to_use: Optional[str] = None
    key_source = "N/A"

    # 1. Essayer de récupérer la clé depuis la base de données
    api_key_from_db = crud_api_keys.get_decrypted_api_key(db, provider_lower)
    if api_key_from_db:
        api_key_to_use = api_key_from_db
        key_source = "database"
        logging.info(f"Using API key from database for provider: {provider_lower} in /generate/text")
    else:
        # 2. Fallback sur la clé du fichier .env (via settings)
        if provider_lower == "mistral":
            api_key_to_use = settings.mistral_api_key
        elif provider_lower == "gemini":
            api_key_to_use = settings.gemini_api_key
        elif provider_lower == "openrouter":
            api_key_to_use = settings.openrouter_api_key
        
        if api_key_to_use:
            key_source = "env_file"
            logging.info(f"Using API key from .env file for provider: {provider_lower} in /generate/text")
        else:
            logging.warning(f"Aucune clé API trouvée ni dans la DB ni dans .env pour le provider: {provider_lower} in /generate/text")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, # Ici status est bien l'objet importé
                detail=f"Clé API non configurée pour le provider: {provider_lower}. Veuillez la configurer."
            )
    
    try:
        logging.info(f"Creating adapter for provider: {provider_lower} using key from {key_source} for text generation")
        adapter = create_adapter(provider_lower, api_key_to_use, request.model)
        generated_text = await adapter.generate(
            prompt=request.prompt,
            action=request.action,
            style=request.style,
            characters=request.characters,
            scene_goal=request.scene_goal,
            key_elements=request.key_elements,
            custom_style_description=request.custom_style_description,
            character_context=request.character_context
        )
        return {"generated_text": generated_text, "raw_response": getattr(adapter, 'raw_response', None)}
    except ValueError as e: # Erreurs de create_adapter ou generate
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) # Ici status est bien l'objet importé
    except Exception as e:
        logging.error(f"Erreur lors de la génération de texte pour {provider_lower}: {str(e)}")
        logging.exception("Stack trace complet:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne du serveur lors de la génération de texte: {e}") # Ici status est bien l'objet importé

# TODO: Ajouter un endpoint pour récupérer la configuration des clés API (juste si elles sont set, pas les clés elles-mêmes)
# Le routeur api_keys_config.router gère déjà cela avec /status.
# L'endpoint /status global pourrait être mis à jour pour utiliser ce nouveau service.