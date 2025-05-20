import requests

# Configuration de l'API
api_key = "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"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "votre-site.com",  # Optionnel mais recommandé
    "X-Title": "Nom de votre application"  # Optionnel
}

# Récupérer les modèles
response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
data = response.json()

# Afficher la structure des données (pour déboguer)
print("Structure de la réponse :", data)  # À commenter après vérification

# Parcourir les modèles
for model in data.get("data", []):
    # Adapter les clés selon la structure réelle
    model_id = model.get("id", "N/A")
    provider = model.get("vendor", model.get("provider", "Inconnu"))  # Nouvelle clé possible
    
    print(f"Nom: {model_id}, Fournisseur: {provider}")