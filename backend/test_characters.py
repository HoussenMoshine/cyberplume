import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importer l'application FastAPI et la Base SQLAlchemy
from backend.main import app
from backend.database import Base, get_db 
from backend import models # Pour utiliser les modèles dans les tests

# --- Configuration de la base de données de test ---

# Utiliser une base de données SQLite en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, # Recommandé pour SQLite en mémoire avec FastAPI/SQLAlchemy
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixtures Pytest ---

@pytest.fixture(scope="function") # Recréer la DB pour chaque test
def db_session():
    """Fixture pour créer et nettoyer la base de données de test."""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db # Fournit la session au test
    finally:
        db.close()
        # Supprimer les tables après le test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Fixture pour créer un TestClient FastAPI avec la DB de test."""
    
    # Définir une fonction pour surcharger la dépendance get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            # La fermeture est gérée par la fixture db_session
            pass 

    # Appliquer la surcharge de dépendance à l'application
    app.dependency_overrides[get_db] = override_get_db
    
    # Créer et retourner le client de test
    yield TestClient(app)
    
    # Nettoyer la surcharge après le test
    app.dependency_overrides.clear()


# --- Tests pour l'API Personnages ---

def test_create_character(client):
    """Teste la création d'un personnage via POST /api/characters."""
    response = client.post(
        "/api/characters/",
        json={"name": "Gandalf", "description": "Un magicien puissant", "backstory": "Istari"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Gandalf"
    assert data["description"] == "Un magicien puissant"
    assert data["backstory"] == "Istari"
    assert "id" in data

def test_read_characters_empty(client):
    """Teste la lecture des personnages quand la base est vide."""
    response = client.get("/api/characters/")
    assert response.status_code == 200, response.text
    assert response.json() == []

def test_read_character(client):
    """Teste la lecture d'un personnage spécifique après création."""
    # Créer un personnage d'abord
    create_response = client.post(
        "/api/characters/",
        json={"name": "Frodo", "description": "Porteur de l'Anneau"},
    )
    assert create_response.status_code == 201
    character_id = create_response.json()["id"]

    # Lire le personnage créé
    read_response = client.get(f"/api/characters/{character_id}")
    assert read_response.status_code == 200, read_response.text
    data = read_response.json()
    assert data["name"] == "Frodo"
    assert data["description"] == "Porteur de l'Anneau"
    assert data["id"] == character_id

def test_read_character_not_found(client):
    """Teste la lecture d'un personnage qui n'existe pas (404)."""
    response = client.get("/api/characters/999") # ID improbable
    assert response.status_code == 404, response.text

def test_read_multiple_characters(client):
    """Teste la lecture de plusieurs personnages."""
    # Créer plusieurs personnages
    client.post("/api/characters/", json={"name": "Aragorn"})
    client.post("/api/characters/", json={"name": "Legolas"})

    # Lire la liste
    response = client.get("/api/characters/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 2
    # Note: L'ordre n'est pas garanti par défaut par SQLite, mais pour ce test simple, on suppose un ordre d'insertion.
    # Pour des tests plus robustes, on vérifierait la présence des noms sans supposer l'ordre.
    assert data[0]["name"] == "Aragorn"
    assert data[1]["name"] == "Legolas"

def test_update_character(client):
    """Teste la mise à jour d'un personnage via PUT /api/characters/{id}."""
    # Créer un personnage
    create_response = client.post(
        "/api/characters/",
        json={"name": "Samwise", "description": "Jardinier fidèle"},
    )
    assert create_response.status_code == 201
    character_id = create_response.json()["id"]

    # Mettre à jour le personnage
    update_response = client.put(
        f"/api/characters/{character_id}",
        json={"name": "Samwise Gamgee", "backstory": "Héros de la Comté"},
    )
    assert update_response.status_code == 200, update_response.text
    data = update_response.json()
    assert data["name"] == "Samwise Gamgee"
    assert data["description"] == "Jardinier fidèle" # Description non modifiée
    assert data["backstory"] == "Héros de la Comté" # Backstory ajoutée/mise à jour
    assert data["id"] == character_id

    # Vérifier que la mise à jour est persistante
    read_response = client.get(f"/api/characters/{character_id}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "Samwise Gamgee"
    assert read_response.json()["backstory"] == "Héros de la Comté"

def test_update_character_not_found(client):
    """Teste la mise à jour d'un personnage qui n'existe pas (404)."""
    response = client.put(
        "/api/characters/999",
        json={"name": "Fantôme"}
    )
    assert response.status_code == 404, response.text

def test_delete_character(client):
    """Teste la suppression d'un personnage via DELETE /api/characters/{id}."""
    # Créer un personnage
    create_response = client.post(
        "/api/characters/",
        json={"name": "Boromir", "description": "Fils de Denethor"},
    )
    assert create_response.status_code == 201
    character_id = create_response.json()["id"]

    # Supprimer le personnage
    delete_response = client.delete(f"/api/characters/{character_id}")
    assert delete_response.status_code == 204, delete_response.text # Statut 204 No Content

    # Vérifier que le personnage n'existe plus
    read_response = client.get(f"/api/characters/{character_id}")
    assert read_response.status_code == 404, read_response.text

def test_delete_character_not_found(client):
    """Teste la suppression d'un personnage qui n'existe pas (404)."""
    response = client.delete("/api/characters/999")
    assert response.status_code == 404, response.text

# On pourrait ajouter des tests pour les relations (ex: personnage lié à un chapitre POV)
# et pour la validation des données (ex: nom manquant à la création).