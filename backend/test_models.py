import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cyberplume.backend.models import Base, Project, Chapter, Character
from cyberplume.backend.config import settings

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"

# Create a test engine and session
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency injection to get a test database session
@pytest.fixture()
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test cases
def test_create_project(test_db):
    project = Project(title="Test Project", description="This is a test project.")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    assert project.id == 1
    assert project.title == "Test Project"
    assert project.description == "This is a test project."

def test_create_chapter(test_db):
    project = Project(title="Test Project", description="This is a test project.")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    chapter = Chapter(title="Test Chapter", content="This is a test chapter.", project_id=project.id)
    test_db.add(chapter)
    test_db.commit()
    test_db.refresh(chapter)
    assert chapter.id == 1
    assert chapter.title == "Test Chapter"
    assert chapter.content == "This is a test chapter."
    assert chapter.project_id == project.id

def test_project_chapter_relationship(test_db):
    project = Project(title="Test Project", description="This is a test project.")
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)

    chapter1 = Chapter(title="Test Chapter 1", content="This is test chapter 1.", project_id=project.id)
    chapter2 = Chapter(title="Test Chapter 2", content="This is test chapter 2.", project_id=project.id)
    test_db.add_all([chapter1, chapter2])
    test_db.commit()
    test_db.refresh(project)

    assert len(project.chapters) == 2 # This should be 2, but the relationship is not working