from .mistral_adapter import MistralAdapter
from .gemini_adapter import GeminiAdapter
from .openrouter_adapter import OpenRouterAdapter

def create_adapter(provider: str, api_key: str, model: str = None):
    """
    Crée et retourne l'adaptateur approprié selon le provider.
    """
    adapters = {
        "mistral": lambda: MistralAdapter(api_key, model),
        "gemini": lambda: GeminiAdapter(api_key, model),
        "openrouter": lambda: OpenRouterAdapter(api_key, model)
    }
    
    if provider not in adapters:
        raise ValueError(f"Provider {provider} non supporté")
        
    return adapters[provider]()