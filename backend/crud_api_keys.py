from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from typing import List, Optional

from . import models
# Les schémas Pydantic sont aussi dans models.py dans ce projet
# from . import schemas # Si les schémas étaient dans un fichier séparé
from .config import Settings # MODIFIÉ: Importer Settings pour le fallback

# Initialiser Fernet avec la clé de configuration
# La clé doit être encodée en bytes pour Fernet
try:
    fernet_key_bytes = Settings().cyberplume_fernet_key.encode('utf-8') # MODIFIÉ: Accéder via instance de Settings
    cipher_suite = Fernet(fernet_key_bytes)
except Exception as e:
    print(f"ERREUR CRITIQUE: Impossible d'initialiser Fernet avec CYBERPLUME_FERNET_KEY. {e}")
    print("Veuillez vérifier que CYBERPLUME_FERNET_KEY est une clé Fernet valide dans votre .env.")
    # Dans un cas réel, on pourrait vouloir empêcher l'application de démarrer ici.
    # Pour l'instant, on laisse continuer mais les opérations de chiffrement échoueront.
    cipher_suite = None

SUPPORTED_PROVIDERS = ["gemini", "mistral", "openrouter"]

def encrypt_key(api_key: str) -> str:
    if cipher_suite is None:
        raise RuntimeError("Fernet cipher suite n'est pas initialisée. Vérifiez CYBERPLUME_FERNET_KEY.")
    encrypted_key_bytes = cipher_suite.encrypt(api_key.encode('utf-8'))
    return encrypted_key_bytes.decode('utf-8')

def decrypt_key(encrypted_key: str) -> str:
    if cipher_suite is None:
        raise RuntimeError("Fernet cipher suite n'est pas initialisée. Vérifiez CYBERPLUME_FERNET_KEY.")
    decrypted_key_bytes = cipher_suite.decrypt(encrypted_key.encode('utf-8'))
    return decrypted_key_bytes.decode('utf-8')

def get_api_key_entry(db: Session, provider_name: str) -> Optional[models.ApiKey]:
    provider_name_lower = provider_name.lower()
    if provider_name_lower not in SUPPORTED_PROVIDERS:
        return None # Ou lever une exception
    return db.query(models.ApiKey).filter(models.ApiKey.provider_name == provider_name_lower).first()

def get_decrypted_api_key(db: Session, provider_name: str, settings_fallback: Optional[Settings] = None) -> Optional[str]: # MODIFIÉ: Ajout de settings_fallback
    # Essayer d'abord de récupérer depuis la base de données
    db_api_key_entry = get_api_key_entry(db, provider_name)
    if db_api_key_entry and db_api_key_entry.encrypted_api_key:
        try:
            return decrypt_key(db_api_key_entry.encrypted_api_key)
        except Exception as e:
            print(f"Erreur lors du déchiffrement de la clé pour {provider_name} depuis la DB: {e}")
            # Ne pas retourner ici, essayer le fallback

    # Si non trouvé dans la DB ou erreur de déchiffrement, essayer le fallback sur settings (variables d'env)
    if settings_fallback:
        provider_name_lower = provider_name.lower()
        if provider_name_lower == "gemini":
            return settings_fallback.gemini_api_key
        elif provider_name_lower == "mistral":
            return settings_fallback.mistral_api_key
        elif provider_name_lower == "openrouter":
            return settings_fallback.openrouter_api_key
        # Ajoutez d'autres providers ici si nécessaire

    return None # Retourner None si la clé n'est trouvée nulle part

def create_or_update_api_key(db: Session, provider_name: str, api_key: str) -> models.ApiKey:
    provider_name_lower = provider_name.lower()
    if provider_name_lower not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Fournisseur non supporté: {provider_name}")

    encrypted_key_str = encrypt_key(api_key)

    db_api_key = get_api_key_entry(db, provider_name_lower)
    if db_api_key:
        db_api_key.encrypted_api_key = encrypted_key_str
    else:
        db_api_key = models.ApiKey(
            provider_name=provider_name_lower,
            encrypted_api_key=encrypted_key_str
        )
        db.add(db_api_key)

    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def delete_api_key_entry(db: Session, provider_name: str) -> bool:
    provider_name_lower = provider_name.lower()
    if provider_name_lower not in SUPPORTED_PROVIDERS:
        return False # Ou lever une exception

    db_api_key = get_api_key_entry(db, provider_name_lower)
    if db_api_key:
        db.delete(db_api_key)
        db.commit()
        return True
    return False

def list_api_keys_status(db: Session) -> List[models.ApiKeyRead]:
    statuses = []
    for provider in SUPPORTED_PROVIDERS:
        db_key = get_api_key_entry(db, provider)
        statuses.append(
            models.ApiKeyRead(
                id=db_key.id if db_key else 0, # Mettre un ID factice si pas de clé, ou gérer autrement
                provider_name=provider,
                has_key_set=bool(db_key and db_key.encrypted_api_key)
            )
        )
    return statuses