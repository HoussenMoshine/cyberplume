from setuptools import setup, find_packages

setup(
    name="cyberplume",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "mistralai",
        "pydantic",
        "sqlalchemy",
        "python-dotenv"
    ],
    python_requires=">=3.10",
)