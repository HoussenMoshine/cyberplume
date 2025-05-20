from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

# Utilisation exclusive d'imports relatifs pour les modules locaux
from .ai_services import AIAdapter, create_adapter
from .config import settings
# MODIFIÉ: GenerationRequest inclut maintenant aussi character_context
from .models import GenerationRequest
# MODIFIÉ: Ajout de l'import pour les routeurs export, scenes, analysis, style et agents
from .routers import projects, characters, export, scenes, analysis, style # agents supprimé
from .database import create_tables # Importer la fonction pour créer les tables
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

@app.get("/")
async def root():
    return {"message": "Bienvenue sur CyberPlume API"}

@app.get("/status")
async def status():
    """Endpoint de statut avec vérification des configurations"""
    providers = {
        "mistral": bool(settings.mistral_api_key),
        "gemini": bool(settings.gemini_api_key),
        "openrouter": bool(settings.openrouter_api_key)
    }

    return {
        "status": "ok",
        "version": "0.1.0",
        "debug": settings.debug,
        "providers_configured": providers,
        "api_key_set": bool(settings.api_key)
    }

@app.get("/models/{provider}")
async def get_model_info(
    provider: str,
    x_api_key: str = Header(None, description="Clé API d'authentification")
):
    """
    Retourne les informations sur les modèles disponibles pour un provider donné
    avec leurs metadata (description, capacités, etc.)
    """
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        api_key = {
            "mistral": settings.mistral_api_key,
            "gemini": settings.gemini_api_key,
            "openrouter": settings.openrouter_api_key
        }.get(provider)

        if not api_key:
            # Utiliser AIAdapter directement ici pourrait causer une dépendance circulaire si AIAdapter importe main
            # Il vaut mieux utiliser create_adapter qui est conçu pour ça
            # available_providers = AIAdapter.get_providers() # Potentiel problème
            # Plutôt, on peut lister les clés de notre dictionnaire api_key
            available_providers = ["mistral", "gemini", "openrouter"]
            # Récupérer les providers configurés pour le message d'erreur
            providers_status = {
                "mistral": bool(settings.mistral_api_key),
                "gemini": bool(settings.gemini_api_key),
                "openrouter": bool(settings.openrouter_api_key)
            }
            raise ValueError(
                f"Provider {provider} non supporté ou clé API manquante. "
                f"Providers configurés: {', '.join(p for p, configured in providers_status.items() if configured)}"
            )

        # Créer un adapteur temporaire pour récupérer les modèles dynamiquement
        logging.info(f"Creating adapter for provider: {provider}")
        adapter = create_adapter(provider, api_key)
        models = adapter.get_available_models()
        logging.debug(f"Retrieved models for {provider}: {models}")

        return {
            "provider": provider,
            "status": "active",
            "models": models
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des modèles pour {provider}: {str(e)}")
        logging.exception("Stack trace complet:")
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur lors de la récupération des modèles pour {provider}.")

@app.post("/generate/text")
async def generate_text(request: GenerationRequest, x_api_key: str = Header(None)):
    """
    Génère du texte en utilisant le provider, le modèle, l'action et le style spécifiés.
    Peut inclure des informations contextuelles supplémentaires pour certaines actions,
    y compris le contexte des personnages pertinents.
    Peut utiliser une description de style personnalisée.
    """
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Rate limiting (simple, en mémoire)
    # Attention: ne fonctionne pas avec plusieurs workers uvicorn
    # if x_api_key in last_access and time.time() - last_access[x_api_key] < RATE_LIMIT:
    #     raise HTTPException(status_code=429, detail="Too many requests")
    # last_access[x_api_key] = time.time()

    # MODIFIÉ: Log incluant action, style, custom_style et character_context
    logging.info(
        f"generate_text: provider={request.provider}, model={request.model}, "
        f"action={request.action}, style={request.style}, "
        f"custom_style={bool(request.custom_style_description)}, "
        f"character_context_present={bool(request.character_context)}"
    )
    # Log des détails spécifiques à l'action
    if request.action == "generer_scene":
        logging.info(f"  Scene Goal: {request.scene_goal}")
        logging.info(f"  Characters: {request.characters}")
        logging.info(f"  Key Elements: {request.key_elements}")
    elif request.character_context:
         logging.info(f"  Character Context: {[c.name for c in request.character_context]}")


    try:
        api_key = {
            "mistral": settings.mistral_api_key,
            "gemini": settings.gemini_api_key,
            "openrouter": settings.openrouter_api_key
        }.get(request.provider)

        if not api_key:
             providers_status = {
                 "mistral": bool(settings.mistral_api_key),
                 "gemini": bool(settings.gemini_api_key),
                 "openrouter": bool(settings.openrouter_api_key)
             }
             raise ValueError(
                 f"Provider {request.provider} non supporté ou clé API manquante. "
                 f"Providers configurés: {', '.join(p for p, configured in providers_status.items() if configured)}"
             )

        adapter = create_adapter(request.provider, api_key, request.model)
        # MODIFIÉ: Passer tous les champs pertinents, y compris character_context
        generated_text = await adapter.generate( # Utiliser await si generate est async
            prompt=request.prompt,
            action=request.action,
            style=request.style,
            characters=request.characters, # Pour generate_scene
            scene_goal=request.scene_goal, # Pour generate_scene
            key_elements=request.key_elements, # Pour generate_scene
            custom_style_description=request.custom_style_description,
            character_context=request.character_context # NOUVEAU: Pour continue, suggest, dialogue
            # Ajouter d'autres paramètres comme max_tokens, temperature si besoin depuis request
        )
        return {"generated_text": generated_text}
    except ValueError as e:
        # Log spécifique pour les ValueErrors (souvent liés à la config ou aux entrées)
        logging.warning(f"ValueError in generate_text: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log général pour les autres exceptions
        logging.error(f"Unexpected error in generate_text: {str(e)}")
        logging.exception("Full stack trace for generate_text error:") # Log la stack trace complète
        raise HTTPException(status_code=500, detail="Erreur interne du serveur lors de la génération de texte.")