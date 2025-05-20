import pytest
import pytest_asyncio # Importer pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
import os

# Ajouter le répertoire parent (racine du projet) à sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Assurez-vous que le chemin d'importation est correct
# Si vous exécutez pytest depuis la racine du projet, cela devrait fonctionner.
from backend.main import app
from backend.database import get_db, Base

# --- Configuration de la base de données de test ---
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_temp.db" # Utilise un fichier temporaire

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)

# --- Fixture pour créer et détruire les tables de test ---
# Utiliser 'session' scope pour ne créer/détruire qu'une fois par session de test
# Utiliser autouse=True pour qu'elle s'exécute automatiquement
# Utiliser @pytest_asyncio.fixture pour les fixtures async
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Assurer un état propre au début
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Optionnel: Nettoyage final si nécessaire, mais drop_all au début suffit généralement
    # async with test_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

# --- Fixture pour surcharger la dépendance get_db ---
# Utiliser 'function' scope pour avoir une session DB propre pour chaque test
# Utiliser @pytest_asyncio.fixture pour les fixtures async
@pytest_asyncio.fixture(scope="function")
async def override_get_db():
    async def _override_get_db():
        async with TestingSessionLocal() as session:
            yield session
            # Rollback après chaque test pour isoler les tests
            await session.rollback()

    original_get_db = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _override_get_db
    yield
    # Restaurer la dépendance originale
    if original_get_db:
        app.dependency_overrides[get_db] = original_get_db
    else:
        app.dependency_overrides.pop(get_db, None)

# --- Fixture pour le client HTTP asynchrone ---
# Utiliser 'function' scope pour que chaque test ait son propre client (si nécessaire)
# S'assurer que override_get_db est exécuté avant cette fixture
# Utiliser @pytest_asyncio.fixture pour les fixtures async
@pytest_asyncio.fixture(scope="function")
async def client(override_get_db): # Dépend de override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac # Retourne directement le client initialisé

# La fixture event_loop personnalisée a été supprimée car elle entre en conflit
# avec celle fournie par pytest-asyncio et génère un avertissement.