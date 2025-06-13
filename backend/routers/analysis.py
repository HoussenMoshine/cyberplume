import spacy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
import re
import json
from pydantic import BaseModel, Field, ValidationError # BaseModel est déjà importé
from bs4 import BeautifulSoup

# Importer les modèles SQLAlchemy et la session DB (Imports relatifs)
from .. import models
from ..database import get_db
# Importer les nouveaux modèles Pydantic pour l'analyse de chapitre (Import relatif)
from ..models import ChapterAnalysisResponse, ChapterAnalysisStats, Suggestion
# Importer la factory et l'adapter IA (Imports relatifs)
from ..ai_services.factory import create_adapter # Correction: utiliser create_adapter
from ..ai_services.ai_adapter import AIAdapter
# Importer les settings pour les clés API
from .. import crud_api_keys
from ..config import settings

# Charger le modèle spaCy français (s'assurer qu'il est téléchargé)
try:
    # Tenter de charger le modèle moyen pour un meilleur compromis
    nlp = spacy.load("fr_core_news_md")
    logging.info("Modèle spaCy 'fr_core_news_md' chargé.")
except OSError:
    logging.warning("Modèle 'fr_core_news_md' non trouvé. Tentative avec 'fr_core_news_sm'.")
    try:
        nlp = spacy.load("fr_core_news_sm")
        logging.info("Modèle spaCy 'fr_core_news_sm' chargé.")
    except OSError:
        logging.error("Aucun modèle spaCy français (md ou sm) trouvé. Veuillez télécharger un modèle : python -m spacy download fr_core_news_md (ou sm)")
        nlp = None 
        
router = APIRouter(
    
    tags=["analysis"],
    responses={500: {"description": "Internal Server Error"}},
)

# --- Schémas Pydantic pour l'analyse de cohérence ---

# MODIFIÉ: Définition locale car non trouvé dans models.py
class ConsistencyAnalysisRequest(BaseModel): 
    project_id: int = Field(..., description="ID du projet à analyser")
    # Ajoutez d'autres champs si nécessaire pour la requête

class EntityInfo(models.EntityInfo): # models.EntityInfo existe
    pass

class ConsistencyAnalysisResponse(models.ConsistencyAnalysisResponse): # models.ConsistencyAnalysisResponse existe
    pass

# --- Endpoint pour l'analyse de cohérence (déjà présent) ---

@router.post("/analyze/consistency", response_model=ConsistencyAnalysisResponse)
async def analyze_project_consistency(request: ConsistencyAnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyse la cohérence d'un projet (entités nommées, etc.).
    """
    if nlp is None:
        raise HTTPException(status_code=501, detail="Service d'analyse NLP non disponible (modèle spaCy manquant).")

    logging.info(f"Starting consistency analysis for project_id: {request.project_id}")

    project = db.query(models.Project).filter(models.Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    chapters = db.query(models.Chapter).filter(models.Chapter.project_id == request.project_id).all()
    if not chapters:
        return ConsistencyAnalysisResponse(
            project_id=request.project_id,
            total_chapters=0,
            total_words=0,
            warnings=["Aucun chapitre trouvé pour ce projet."]
        )

    full_text = ""
    for chapter in chapters:
        if chapter.content:
            # Utiliser BeautifulSoup pour extraire le texte brut de l'HTML
            soup = BeautifulSoup(chapter.content, 'html.parser')
            plain_chapter_text = soup.get_text(separator=" ", strip=True)
            full_text += f"\n\n--- CHAPITRE: {chapter.title} ---\n\n" + plain_chapter_text

    if not full_text.strip():
        return ConsistencyAnalysisResponse(
            project_id=request.project_id,
            total_chapters=len(chapters),
            total_words=0,
            warnings=["Les chapitres de ce projet sont vides."]
        )

    logging.info(f"Processing text with spaCy (length: {len(full_text)} chars)...")
    doc = nlp(full_text)
    logging.info("spaCy processing complete.")

    entity_counts: Dict[tuple, int] = {} 
    total_words = 0
    for token in doc:
        if not token.is_punct and not token.is_space:
            total_words += 1

    for ent in doc.ents:
        if ent.label_ in ["PER", "LOC", "ORG"]: # Personnes, Lieux, Organisations
            key = (ent.text.lower(), ent.label_) # Normaliser en minuscules pour le comptage
            entity_counts[key] = entity_counts.get(key, 0) + 1
            
    entities_response: List[EntityInfo] = []
    for (text, label), count in sorted(entity_counts.items(), key=lambda item: item[1], reverse=True):
         entities_response.append(EntityInfo(text=text, label=label, count=count))

    warnings = []
    # Exemple d'avertissement potentiel (à affiner)
    # if len(entities_response) > 50:
    #     warnings.append("Nombre élevé d'entités uniques détectées. Vérifiez la pertinence.")
    
    logging.info(f"Analysis complete for project {request.project_id}. Found {len(entities_response)} unique entities.")

    return ConsistencyAnalysisResponse(
        project_id=request.project_id,
        total_chapters=len(chapters),
        total_words=total_words,
        entities=entities_response,
        warnings=warnings
    )

# --- NOUVEAU: Endpoint pour l'analyse de contenu de chapitre ---

class ChapterAnalysisRequest(BaseModel):
    provider: str = Field(..., description="Fournisseur IA à utiliser (ex: 'gemini', 'mistral')")
    model: Optional[str] = Field(None, description="Modèle spécifique à utiliser (si non fourni, utilise le défaut du fournisseur)")

@router.post("/chapters/{chapter_id}/analyze-content", response_model=ChapterAnalysisResponse)
async def analyze_chapter_content(
    chapter_id: int,
    request: ChapterAnalysisRequest, 
    db: Session = Depends(get_db)
):
    """
    Analyse le contenu d'un chapitre spécifique pour obtenir des statistiques
    et des suggestions d'amélioration via IA, incluant les indices de position.
    Prend en compte le résumé du chapitre précédent si disponible.
    """
    logging.info(f"Starting content analysis for chapter_id: {chapter_id}")

    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    content_html = chapter.content if chapter.content else ""
    if not content_html.strip():
        logging.warning(f"Chapter {chapter_id} content is empty. Returning basic stats.")
        stats = ChapterAnalysisStats(word_count=0)
        return ChapterAnalysisResponse(chapter_id=chapter_id, stats=stats, suggestions=[])

    soup = BeautifulSoup(content_html, 'html.parser')
    content_plain_text = soup.get_text(separator=" ", strip=True) # Utiliser separator et strip
    
    logging.info(f"Plain text for analysis (chapter {chapter_id}, length: {len(content_plain_text)}): {content_plain_text[:500]}...")

    # Récupérer le résumé du chapitre précédent
    previous_chapter_summary_context = ""
    if chapter.order is not None and chapter.order > 0:
        previous_chapter = db.query(models.Chapter).filter(
            models.Chapter.project_id == chapter.project_id,
            models.Chapter.order == chapter.order - 1
        ).first()
        if previous_chapter and previous_chapter.summary:
            previous_chapter_summary_context = f"""
CONTEXTE DU CHAPITRE PRÉCÉDENT ({previous_chapter.title}):
---
{previous_chapter.summary}
---

Vous analysez maintenant le CHAPITRE ACTUEL ({chapter.title}).
"""
            logging.info(f"Injecting summary of previous chapter (ID: {previous_chapter.id}, Title: {previous_chapter.title}) into AI prompt.")

    word_count = len(content_plain_text.split())
    stats = ChapterAnalysisStats(word_count=word_count)

    suggestions: List[Suggestion] = []
    try:
        provider_lower = request.provider.lower()

        # Correction: Utiliser la logique de récupération de clé API et d'instanciation de service
        # similaire à celle de summary_service.py
        api_key_to_use = None
        model_name_to_use = request.model # Le modèle peut être spécifié dans la requête

        if provider_lower == "gemini":
            api_key_to_use = settings.gemini_api_key
            if not model_name_to_use: # Si non spécifié dans la requête, prendre celui par défaut
                 model_name_to_use = getattr(settings, 'gemini_analysis_model_name', getattr(settings, 'gemini_model_name', None))
        elif provider_lower == "mistral":
            api_key_to_use = settings.mistral_api_key
            if not model_name_to_use:
                 model_name_to_use = getattr(settings, 'mistral_analysis_model_name', getattr(settings, 'mistral_model_name', None))
        elif provider_lower == "openrouter":
            api_key_to_use = settings.openrouter_api_key
            if not model_name_to_use:
                 model_name_to_use = getattr(settings, 'openrouter_analysis_model_name', getattr(settings, 'openrouter_default_model', None))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fournisseur non supporté : {request.provider}"
            )

        if not api_key_to_use:
            logging.warning(f"Aucune clé API trouvée (DB ou .env) pour le provider: {provider_lower} lors de l'analyse de chapitre.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Clé API non configurée pour le fournisseur : {request.provider}. Veuillez la configurer via l'interface ou le fichier .env."
            )
        
        ai_service: AIAdapter = create_adapter(provider_name=provider_lower, api_key=api_key_to_use, model=model_name_to_use)
        
        # Construire le prompt pour l'analyse de contenu
        # TODO: Améliorer ce prompt, le rendre configurable, ou utiliser des templates.
        # S'assurer que le prompt demande des suggestions avec des indices de position.
        prompt_template = f"""{previous_chapter_summary_context}
Analysez le texte suivant du chapitre "{chapter.title}" et fournissez des suggestions d'amélioration. 
Pour chaque suggestion, indiquez le texte original concerné, la suggestion de remplacement, et si possible, les indices de début et de fin du texte original dans le contenu brut.
Format attendu pour chaque suggestion (JSON parsable dans une liste):
{{
  "original_text": "le texte original à remplacer",
  "suggested_text": "le texte suggéré",
  "start_index": index_debut_original_text,
  "end_index": index_fin_original_text,
  "comment": "brève explication de la suggestion"
}}

Voici le texte à analyser :
---
{content_plain_text}
---

Suggestions (liste de JSON) :
"""
        # Placeholder pour la réponse de l'IA - à remplacer par un appel réel
        # La réponse de l'IA devrait être une chaîne JSON représentant une liste d'objets Suggestion.
        # Exemple de réponse attendue de l'IA (chaîne JSON):
        # '[{"original_text": "un exemple de texte", "suggested_text": "un meilleur exemple", "start_index": 10, "end_index": 30, "comment": "Reformulation pour clarté."}]'
        
        # generated_response_str = await ai_service.generate(prompt_template, max_tokens=1000) # Ajuster max_tokens
        # Pour l'instant, simulation
        generated_response_str = f"""
        [
            {{
                "original_text": "{content_plain_text[20:40]}",
                "suggested_text": "un segment de texte amélioré (simulé)",
                "start_index": 20,
                "end_index": 40,
                "comment": "Ceci est une suggestion simulée pour des raisons de test."
            }}
        ]
        """
        logging.info(f"Réponse simulée de l'IA pour l'analyse du chapitre {chapter_id}: {generated_response_str}")

        try:
            parsed_suggestions = json.loads(generated_response_str)
            for sugg_data in parsed_suggestions:
                # Valider avec le modèle Pydantic Suggestion
                try:
                    suggestion_obj = Suggestion(**sugg_data)
                    suggestions.append(suggestion_obj)
                except ValidationError as ve:
                    logging.error(f"Erreur de validation pour la suggestion: {sugg_data}, Erreurs: {ve.errors()}")
                    # Optionnel: ajouter un avertissement ou une suggestion partielle
        except json.JSONDecodeError as e:
            logging.error(f"Erreur de décodage JSON de la réponse IA pour le chapitre {chapter_id}: {e}")
            logging.error(f"Réponse IA brute: {generated_response_str}")
            # Optionnel: ajouter un avertissement à la réponse finale
            # suggestions.append(Suggestion(original_text="Erreur IA", suggested_text="Impossible d'interpréter la réponse de l'IA.", start_index=0, end_index=0, comment="Vérifiez les logs du serveur."))


    except HTTPException: # Laisser remonter les HTTPException (clés API, etc.)
        raise
    except Exception as e:
        logging.error(f"Erreur inattendue lors de l'analyse du chapitre {chapter_id}: {e}", exc_info=True)
        # Ne pas bloquer toute la réponse pour une erreur d'IA, retourner les stats au moins
        # suggestions.append(Suggestion(original_text="Erreur Serveur", suggested_text="Une erreur interne est survenue lors de l'analyse IA.", start_index=0, end_index=0, comment=str(e)))

    return ChapterAnalysisResponse(chapter_id=chapter_id, stats=stats, suggestions=suggestions)

# TODO: Ajouter un endpoint pour l'analyse de style (similaire à l'analyse de contenu mais avec un prompt différent)
# from ..models import StyleAnalysisRequest, StyleAnalysisResponse
# @router.post("/chapters/{chapter_id}/analyze-style", response_model=StyleAnalysisResponse)
# async def analyze_chapter_style ...