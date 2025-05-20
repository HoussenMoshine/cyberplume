import requests

# Configuration de l'API
api_key = "CXaga1oCfRdswb9jJ8ya7efuqVv4h4Lq"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Récupérer les modèles
response = requests.get("https://api.mistral.ai/v1/models", headers=headers)
models = response.json()

# Afficher les noms des modèles
for model in models["data"]:
    print(f"Nom: {model['id']}, Description: {model['description']}")