import google.generativeai as genai

# Configuration de l'API
genai.configure(api_key="AIzaSyBAHyupnFpV1iyZo4IiniJGyklnEU1-Z_E")

# Récupérer tous les modèles
models = genai.list_models()

# Filtrer les modèles Gemini (leurs noms commencent par "gemini")
gemini_models = [
    model for model in models
    if "gemini" in model.name.lower()  # Filtrage par nom
]

# Afficher les détails
for model in gemini_models:
    print(f"Nom: {model.name}")
    print(f"Description: {model.description}")
    print(f"Version: {model.version}")
    print("---" * 10)