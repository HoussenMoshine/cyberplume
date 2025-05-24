from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud_api_keys, models # models contient aussi les schemas Pydantic
from ..database import get_db

router = APIRouter(
    prefix="/api-keys-config", # Changé pour éviter conflit potentiel avec /api/keys si existant
    tags=["API Keys Configuration"],
)

# Schéma pour le corps de la requête POST/PUT pour définir une clé
class ApiKeySetRequest(models.BaseModel):
    api_key: str


@router.get("/status", response_model=List[models.ApiKeyRead])
def get_api_keys_status(db: Session = Depends(get_db)):
    """
    Récupère le statut de configuration des clés API pour tous les fournisseurs supportés.
    Indique pour chaque fournisseur si une clé API a été définie.
    """
    return crud_api_keys.list_api_keys_status(db)

@router.post("/{provider_name}", response_model=models.ApiKeyRead)
def set_api_key(
    provider_name: str, 
    api_key_request: ApiKeySetRequest, 
    db: Session = Depends(get_db)
):
    """
    Définit ou met à jour la clé API pour un fournisseur spécifié.
    La clé API est fournie dans le corps de la requête.
    """
    provider_name_lower = provider_name.lower()
    if provider_name_lower not in crud_api_keys.SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fournisseur non supporté: {provider_name}. Supportés: {', '.join(crud_api_keys.SUPPORTED_PROVIDERS)}"
        )
    try:
        crud_api_keys.create_or_update_api_key(
            db=db, 
            provider_name=provider_name_lower, 
            api_key=api_key_request.api_key
        )
        # Après la création/mise à jour, récupérer le statut pour la réponse
        # Cela garantit que la réponse reflète l'état actuel, y compris l'ID si c'est une nouvelle entrée.
        updated_key_info = crud_api_keys.get_api_key_entry(db, provider_name_lower)
        if not updated_key_info:
             # Cela ne devrait pas arriver si create_or_update_api_key a réussi
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de la récupération de la clé après mise à jour.")

        return models.ApiKeyRead(
            id=updated_key_info.id,
            provider_name=updated_key_info.provider_name,
            has_key_set=bool(updated_key_info.encrypted_api_key) # Devrait toujours être true ici
        )

    except ValueError as e: # Capturer les ValueErrors de create_or_update_api_key
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Log l'erreur e pour le débogage côté serveur
        print(f"Erreur interne du serveur lors de la définition de la clé API pour {provider_name}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erreur interne du serveur: {e}")


@router.delete("/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(provider_name: str, db: Session = Depends(get_db)):
    """
    Supprime la clé API pour un fournisseur spécifié.
    """
    provider_name_lower = provider_name.lower()
    if provider_name_lower not in crud_api_keys.SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fournisseur non supporté: {provider_name}. Supportés: {', '.join(crud_api_keys.SUPPORTED_PROVIDERS)}"
        )
    
    success = crud_api_keys.delete_api_key_entry(db, provider_name_lower)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune clé API trouvée pour le fournisseur: {provider_name}"
        )
    return # Réponse 204 No Content en cas de succès