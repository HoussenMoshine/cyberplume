import pytest
from httpx import AsyncClient

# Les fixtures (client, override_get_db, setup_database) sont maintenant dans conftest.py

# --- Tests pour les Projets ---

# Clé API de test (similaire à celle dans .env mais peut être différente)
TEST_API_KEY = "test-secret-key"
headers = {"x-api-key": TEST_API_KEY}

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Teste la création d'un nouveau projet."""
    project_data = {"title": "Mon Premier Projet de Test", "description": "Une description test"}
    response = await client.post("/api/projects/", json=project_data, headers=headers)
    assert response.status_code == 200 # Ou 201 si vous utilisez ce code pour la création
    data = response.json()
    assert data["title"] == project_data["title"]
    assert data["description"] == project_data["description"]
    assert "id" in data
    assert data["id"] is not None

@pytest.mark.asyncio
async def test_read_projects(client: AsyncClient):
    """Teste la lecture de la liste des projets."""
    # Créer d'abord un projet pour s'assurer qu'il y a quelque chose à lire
    # Note: Les tests s'exécutent dans un ordre non garanti et la DB est (potentiellement)
    # nettoyée entre les tests selon le scope des fixtures. Il est plus sûr de créer
    # les données nécessaires DANS chaque test.
    await client.post("/api/projects/", json={"title": "Projet Test 1"}, headers=headers)
    await client.post("/api/projects/", json={"title": "Projet Test 2"}, headers=headers)

    response = await client.get("/api/projects/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # La base de données est nettoyée avant chaque test (scope='function' pour override_get_db)
    # Donc on ne s'attend qu'aux 2 projets créés dans CE test.
    assert len(data) == 2
    # L'ordre n'est pas garanti sans clause ORDER BY explicite dans l'API
    titles = {item["title"] for item in data}
    assert titles == {"Projet Test 1", "Projet Test 2"}

@pytest.mark.asyncio
async def test_read_project(client: AsyncClient):
    """Teste la lecture d'un projet spécifique par son ID."""
    # Créer un projet
    create_response = await client.post("/api/projects/", json={"title": "Projet à Lire"}, headers=headers)
    project_id = create_response.json()["id"]

    # Lire le projet créé
    response = await client.get(f"/api/projects/{project_id}/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["title"] == "Projet à Lire"

@pytest.mark.asyncio
async def test_update_project(client: AsyncClient):
    """Teste la mise à jour (modification) d'un projet existant."""
    # Créer un projet
    create_response = await client.post("/api/projects/", json={"title": "Projet à Modifier"}, headers=headers)
    project_id = create_response.json()["id"]

    # Mettre à jour le projet
    update_data = {"title": "Projet Modifié", "description": "Nouvelle description"}
    response = await client.put(f"/api/projects/{project_id}/", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]

    # Vérifier que la modification est persistée en relisant le projet
    read_response = await client.get(f"/api/projects/{project_id}/", headers=headers)
    assert read_response.status_code == 200
    read_data = read_response.json()
    assert read_data["title"] == update_data["title"]
    assert read_data["description"] == update_data["description"]

@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    """Teste la suppression d'un projet."""
    # Créer un projet
    create_response = await client.post("/api/projects/", json={"title": "Projet à Supprimer"}, headers=headers)
    project_id = create_response.json()["id"]

    # Supprimer le projet
    delete_response = await client.delete(f"/api/projects/{project_id}/", headers=headers)
    assert delete_response.status_code == 200 # Ou 204 si l'API ne retourne pas de contenu
    # Vérifier que le projet a bien été supprimé (devrait retourner 404)
    read_response = await client.get(f"/api/projects/{project_id}/", headers=headers)
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_read_non_existent_project(client: AsyncClient):
    """Teste la lecture d'un projet qui n'existe pas."""
    response = await client.get("/api/projects/99999/", headers=headers) # ID improbable
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_non_existent_project(client: AsyncClient):
    """Teste la mise à jour d'un projet qui n'existe pas."""
    update_data = {"title": "Titre Fantôme"}
    response = await client.put("/api/projects/99999/", json=update_data, headers=headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_non_existent_project(client: AsyncClient):
    """Teste la suppression d'un projet qui n'existe pas."""
    response = await client.delete("/api/projects/99999/", headers=headers)
    assert response.status_code == 404

# TODO: Ajouter des tests pour les cas d'erreur (ex: données invalides, clé API manquante/incorrecte)
# TODO: Ajouter des tests pour la pagination si implémentée
# TODO: Ajouter des tests pour les relations (ex: suppression d'un projet supprime ses chapitres)