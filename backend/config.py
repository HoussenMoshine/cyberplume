import os
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional
from cryptography.fernet import Fernet

# Déterminer le répertoire du fichier config.py
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
# Construire le chemin vers le fichier .env dans le même répertoire
ENV_FILE_PATH = os.path.join(CONFIG_DIR, '.env')

class Settings(BaseSettings):
    api_key: str = Field(..., validation_alias="API_KEY")
    debug: bool = True
    mistral_api_key: Optional[str] = Field(None, validation_alias="MISTRAL_API_KEY")
    gemini_api_key: Optional[str] = Field(None, validation_alias="GEMINI_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, validation_alias="OPENROUTER_API_KEY")
    
    cyberplume_fernet_key: Optional[str] = Field(None, validation_alias="CYBERPLUME_FERNET_KEY")

    @field_validator('cyberplume_fernet_key', mode='before')
    @classmethod
    def check_fernet_key(cls, v: Optional[str], info) -> str: # info est requis par Pydantic v2 pour les validateurs de champ
        if v is None:
            key_bytes = Fernet.generate_key()
            key_str = key_bytes.decode('utf-8')
            print("+" + "-"*78 + "+")
            print("| IMPORTANT: CYBERPLUME_FERNET_KEY non définie dans votre fichier .env      |")
            print("| Une nouvelle clé de chiffrement a été générée.                          |")
            print("| Veuillez l'ajouter à votre fichier .env (`backend/.env`)                |")
            print("| pour assurer la persistance des données chiffrées :                     |")
            print(f"| CYBERPLUME_FERNET_KEY={key_str}                                      |")
            print("+" + "-"*78 + "+")
            return key_str
        # S'assurer que la clé fournie est une chaîne valide pour Fernet (encodée base64 URL-safe)
        try:
            Fernet(v.encode('utf-8'))
        except Exception as e:
            # Si la clé n'est pas valide, on pourrait soit lever une erreur, soit en générer une nouvelle.
            # Pour l'instant, on va lever une erreur pour forcer l'utilisateur à fournir une clé correcte.
            raise ValueError(f"CYBERPLUME_FERNET_KEY fournie n'est pas une clé Fernet valide: {e}")
        return v

    class Config:
        env_file = ENV_FILE_PATH # Utiliser le chemin construit
        extra = 'ignore' # Ignorer les variables d'environnement supplémentaires


settings = Settings()

def get_settings():
    return settings