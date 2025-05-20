import os
from dotenv import load_dotenv
from mistralai import Mistral

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer la clé API
api_key = os.environ.get("MISTRAL_API_KEY")

if api_key is None:
    print("Erreur: La variable d'environnement MISTRAL_API_KEY n'est pas définie.")
    exit()

model = "mistral-large-latest"

client = Mistral(api_key=api_key)

try:
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "What is the best French cheese?",
            },
        ]
    )
    print(chat_response.choices[0].message.content)

except Exception as e:
    print(f"Une erreur s'est produite : {e}")