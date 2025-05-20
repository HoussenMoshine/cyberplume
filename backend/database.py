import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configuration du chemin de la base de données
# Utiliser un chemin absolu ou relatif robuste basé sur l'emplacement de ce fichier
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTANCE_FOLDER = os.path.join(BASE_DIR, 'instance')
DB_PATH = os.path.join(INSTANCE_FOLDER, 'cyberplume.db')

# Créer le dossier instance s'il n'existe pas
os.makedirs(INSTANCE_FOLDER, exist_ok=True)

# URL de la base de données SQLite
SQLALCHEMY_DATABASE_URL = f'sqlite:///{DB_PATH}'

# Créer l'engine SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Nécessaire pour SQLite
)

# Créer une classe SessionLocal pour les sessions de base de données
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer une Base pour les modèles déclaratifs
# Les modèles dans models.py hériteront de cette Base
Base = declarative_base()

# Fonction de dépendance pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour créer toutes les tables définies dans les modèles qui héritent de Base
def create_tables():
    # Importer les modèles ici pour s'assurer qu'ils sont enregistrés avec Base avant create_all
    # Bien que Base soit défini ici, les modèles eux-mêmes sont dans models.py
    from . import models # noqa: F401 - Import non utilisé directement mais nécessaire pour l'enregistrement des modèles
    Base.metadata.create_all(bind=engine)