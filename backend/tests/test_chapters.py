import pytest
from httpx import AsyncClient

# Réutiliser les fixtures et la configuration de test_projects.py
# Idéalement, ces fixtures devraient être dans un fichier conftest.py
# Pour l'instant, on les importe implicitement via pytest ou on pourrait les copier/importer explicitement.
# On suppose ici que pytest les trouve.

# Clé API de test (doit être la même que celle utilisée par les fixtures)
TEST_API_KEY = "test-secret-key"
headers = {"x-api-key": TEST_API_KEY}

# --- Helper pour créer un projet ---
async def create_test_project(client: AsyncClient, title="Projet Parent Test"):
    response = await client.post("/api/projects/", json={"title": title}, headers=headers)
    assert response.status_code == 200
    return response.json()["id"]

# --- Tests pour les Chapitres ---

@pytest.mark.asyncio
async def test_create_chapter(client: AsyncClient):
    """Teste la création d'un nouveau chapitre pour un projet existant."""
    project_id = await create_test_project(client)
    chapter_data = {"title": "Chapitre 1: L'Aube", "content": "Il était une fois...", "order": 1}
    # L'endpoint pourrait être /api/projects/{project_id}/chapters/ ou /api/chapters/?project_id={project_id}
    # On suppose ici /api/projects/{project_id}/chapters/ basé sur les conventions REST
    response = await client.post(f"/api/projects/{project_id}/chapters/", json=chapter_data, headers=headers)
    assert response.status_code == 200 # Ou 201
    data = response.json()
    assert data["title"] == chapter_data["title"]
    assert data["content"] == chapter_data["content"]
    assert data["order"] == chapter_data["order"]
    assert data["project_id"] == project_id
    assert "id" in data

@pytest.mark.asyncio
async def test_create_chapter_for_non_existent_project(client: AsyncClient):
    """Teste la création d'un chapitre pour un projet inexistant."""
    chapter_data = {"title": "Chapitre Fantôme", "content": "...", "order": 1}
    response = await client.post("/api/projects/99999/chapters/", json=chapter_data, headers=headers)
    assert response.status_code == 404 # Le projet parent doit exister

@pytest.mark.asyncio
async def test_read_chapters_for_project(client: AsyncClient):
    """Teste la lecture des chapitres d'un projet spécifique."""
    project_id = await create_test_project(client)
    # Créer plusieurs chapitres
    await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre A", "order": 2}, headers=headers)
    await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre B", "order": 1}, headers=headers)

    response = await client.get(f"/api/projects/{project_id}/chapters/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    # Vérifier l'ordre si l'API est censée trier par 'order'
    assert data[0]["title"] == "Chapitre B" # order 1
    assert data[1]["title"] == "Chapitre A" # order 2

@pytest.mark.asyncio
async def test_read_chapter(client: AsyncClient):
    """Teste la lecture d'un chapitre spécifique par son ID."""
    project_id = await create_test_project(client)
    create_response = await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre à Lire", "order": 1}, headers=headers)
    chapter_id = create_response.json()["id"]

    # L'endpoint pourrait être /api/chapters/{chapter_id}/
    response = await client.get(f"/api/chapters/{chapter_id}/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == chapter_id
    assert data["title"] == "Chapitre à Lire"
    assert data["project_id"] == project_id

@pytest.mark.asyncio
async def test_update_chapter(client: AsyncClient):
    """Teste la mise à jour d'un chapitre existant."""
    project_id = await create_test_project(client)
    create_response = await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre Original", "content": "Contenu initial", "order": 1}, headers=headers)
    chapter_id = create_response.json()["id"]

    update_data = {"title": "Chapitre Modifié", "content": "Contenu mis à jour", "order": 2}
    response = await client.put(f"/api/chapters/{chapter_id}/", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == chapter_id
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert data["order"] == update_data["order"]

    # Vérifier la persistance
    read_response = await client.get(f"/api/chapters/{chapter_id}/", headers=headers)
    read_data = read_response.json()
    assert read_data["title"] == update_data["title"]
    assert read_data["content"] == update_data["content"]
    assert read_data["order"] == update_data["order"]

@pytest.mark.asyncio
async def test_delete_chapter(client: AsyncClient):
    """Teste la suppression d'un chapitre."""
    project_id = await create_test_project(client)
    create_response = await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre à Supprimer", "order": 1}, headers=headers)
    chapter_id = create_response.json()["id"]

    # Supprimer le chapitre
    delete_response = await client.delete(f"/api/chapters/{chapter_id}/", headers=headers)
    assert delete_response.status_code == 200 # Ou 204

    # Vérifier la suppression
    read_response = await client.get(f"/api/chapters/{chapter_id}/", headers=headers)
    assert read_response.status_code == 404

    # Vérifier qu'il n'est plus dans la liste du projet
    list_response = await client.get(f"/api/projects/{project_id}/chapters/", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 0

@pytest.mark.asyncio
async def test_batch_delete_chapters(client: AsyncClient):
    """Teste la suppression de plusieurs chapitres en une seule requête."""
    project_id = await create_test_project(client)
    # Créer plusieurs chapitres
    ch1_resp = await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre Batch 1", "order": 1}, headers=headers)
    ch2_resp = await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre Batch 2", "order": 2}, headers=headers)
    ch3_resp = await client.post(f"/api/projects/{project_id}/chapters/", json={"title": "Chapitre Batch 3", "order": 3}, headers=headers)
    ch1_id = ch1_resp.json()["id"]
    ch2_id = ch2_resp.json()["id"]
    ch3_id = ch3_resp.json()["id"] # Celui-ci ne sera pas supprimé

    ids_to_delete = [ch1_id, ch2_id]

    # Utiliser l'endpoint POST /api/chapters/batch-delete comme mentionné dans progres-cyberplume.md
    # Le corps de la requête est supposé être une liste d'IDs, par exemple {"ids": [id1, id2]}
    batch_delete_response = await client.post("/api/chapters/batch-delete", json={"ids": ids_to_delete}, headers=headers)
    assert batch_delete_response.status_code == 200 # Ou 204
    # Vérifier le nombre de chapitres supprimés si l'API le retourne
    # delete_result = batch_delete_response.json()
    # assert delete_result.get("deleted_count") == 2

    # Vérifier que les chapitres spécifiés sont supprimés
    read_ch1_resp = await client.get(f"/api/chapters/{ch1_id}/", headers=headers)
    assert read_ch1_resp.status_code == 404
    read_ch2_resp = await client.get(f"/api/chapters/{ch2_id}/", headers=headers)
    assert read_ch2_resp.status_code == 404

    # Vérifier que le chapitre non spécifié existe toujours
    read_ch3_resp = await client.get(f"/api/chapters/{ch3_id}/", headers=headers)
    assert read_ch3_resp.status_code == 200
    assert read_ch3_resp.json()["title"] == "Chapitre Batch 3"

    # Vérifier la liste des chapitres restants pour le projet
    list_response = await client.get(f"/api/projects/{project_id}/chapters/", headers=headers)
    assert list_response.status_code == 200
    remaining_chapters = list_response.json()
    assert len(remaining_chapters) == 1
    assert remaining_chapters[0]["id"] == ch3_id

@pytest.mark.asyncio
async def test_read_non_existent_chapter(client: AsyncClient):
    """Teste la lecture d'un chapitre qui n'existe pas."""
    response = await client.get("/api/chapters/99999/", headers=headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_non_existent_chapter(client: AsyncClient):
    """Teste la mise à jour d'un chapitre qui n'existe pas."""
    update_data = {"title": "Titre Fantôme"}
    response = await client.put("/api/chapters/99999/", json=update_data, headers=headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_non_existent_chapter(client: AsyncClient):
    """Teste la suppression d'un chapitre qui n'existe pas."""
    response = await client.delete("/api/chapters/99999/", headers=headers)
    assert response.status_code == 404

# TODO: Ajouter des tests pour les cas d'erreur (données invalides, clé API, etc.)
# TODO: Tester la suppression en cascade (supprimer projet -> chapitres supprimés) - peut être dans test_projects.py