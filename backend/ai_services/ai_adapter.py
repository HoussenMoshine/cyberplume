from abc import ABC, abstractmethod
from typing import List, Optional # Importer List et Optional
# NOUVEAU: Importer CharacterContext pour la signature de generate
from ..models import CharacterContext

class AIAdapter(ABC):
    """Classe de base abstraite pour tous les adaptateurs d'IA."""

    @abstractmethod
    async def generate( # Rendre la méthode async pour correspondre à l'appel dans main.py
        self,
        prompt: str,
        action: Optional[str] = None,
        style: Optional[str] = None,
        # Paramètres optionnels pour enrichir la génération de scène
        characters: Optional[List[str]] = None,
        scene_goal: Optional[str] = None,
        key_elements: Optional[str] = None,
        # Paramètre pour le style personnalisé analysé
        custom_style_description: Optional[str] = None,
        # NOUVEAU: Paramètre pour le contexte des personnages
        character_context: Optional[List[CharacterContext]] = None,
        # Ajouter d'autres paramètres communs si nécessaire (ex: max_tokens, temperature)
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Génère du texte à partir d'un prompt, en tenant compte d'une action,
        d'un style d'écriture spécifiques (standard ou personnalisé), et potentiellement
        d'informations contextuelles supplémentaires comme le contexte des personnages.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[dict]:
        """Retourne la liste des modèles disponibles avec metadata."""
        pass

    # La méthode statique get_provider_models a été supprimée car elle contenait
    # une liste statique obsolète et était utilisée incorrectement comme fallback.
    # La récupération des modèles doit se faire dynamiquement via get_available_models()
    # implémentée dans chaque adaptateur spécifique.

    @staticmethod
    def get_providers() -> list[str]:
        """Retourne la liste des providers disponibles."""
        return ["mistral", "gemini", "openrouter"]