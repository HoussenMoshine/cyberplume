import os
from pydantic_settings import BaseSettings
from pydantic import Field

# Déterminer le répertoire du fichier config.py
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
# Construire le chemin vers le fichier .env dans le même répertoire
ENV_FILE_PATH = os.path.join(CONFIG_DIR, '.env')

class Settings(BaseSettings):
    api_key: str = Field(..., validation_alias="API_KEY")
    debug: bool = True
    mistral_api_key: str = Field(..., validation_alias="MISTRAL_API_KEY") # Utiliser validation_alias pour la compatibilité
    gemini_api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    openrouter_api_key: str = Field(..., validation_alias="OPENROUTER_API_KEY")


    class Config:
        env_file = ENV_FILE_PATH # Utiliser le chemin construit
        extra = 'ignore' # Ignorer les variables d'environnement supplémentaires


settings = Settings()

def get_settings():
    return settings