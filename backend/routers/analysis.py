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
from ..crud_api_keys import get_decrypted_api_key # IMPORT CORRECT

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
        model_name_to_use = request.model

        # CORRECTION: Utiliser la logique de récupération de clé unifiée
        api_key_to_use = get_decrypted_api_key(db, provider_lower, settings_fallback=settings)

        if not api_key_to_use:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Clé API pour le fournisseur '{provider_lower}' non configurée dans la base de données ou le fichier .env."
            )

        # Définir le modèle par défaut si non fourni
        if not model_name_to_use:
            default_model_key = f'{provider_lower}_analysis_model_name'
            fallback_model_key = f'{provider_lower}_model_name'
            model_name_to_use = getattr(settings, default_model_key, getattr(settings, fallback_model_key, None))

        ai_service = create_adapter(provider_lower, api_key=api_key_to_use, model=model_name_to_use)
        
        if not ai_service:
            raise HTTPException(status_code=500, detail=f"Impossible d'initialiser le service IA pour {provider_lower}")

        prompt = f"""
        {previous_chapter_summary_context}
        <instruction>
        Tu es un assistant d'écriture expert. Analyse le texte du CHAPITRE ACTUEL ci-dessous.
        Identifie les fautes de grammaire, d'orthographe, les problèmes de style (répétitions, phrases maladroites), et les incohérences.
        Pour chaque problème identifié, fournis une suggestion d'amélioration.
        Ta réponse DOIT être un objet JSON valide, qui est une liste de suggestions.
        Chaque suggestion dans la liste doit être un objet JSON avec les clés suivantes :
        - "original_text": Le segment de texte exact à corriger.
        - "start_index": L'index de début du segment dans le texte original.
        - "end_index": L'index de fin du segment dans le texte original.
        - "suggested_text": La version corrigée ou améliorée du segment.
        - "explanation": Une brève explication de la raison de la suggestion.
        - "suggestion_type": Une catégorie pour la suggestion (par exemple, "Grammaire", "Style", "Orthographe", "Clarté", "Incohérence").

        Exemple de format de sortie JSON attendu :
        [
            {{
                "original_text": "Il sont aller au marché.",
                "start_index": 10,
                "end_index": 32,
                "suggested_text": "Ils sont allés au marché.",
                "explanation": "Accord du participe passé avec l'auxiliaire 'être' et correction du pronom sujet.",
                "suggestion_type": "Grammaire"
            }},
            {{
                "original_text": "Le grand homme grand.",
                "start_index": 45,
                "end_index": 64,
                "suggested_text": "L'homme de grande taille.",
                "explanation": "Répétition du mot 'grand'.",
                "suggestion_type": "Style"
            }}
        ]
        Ne fournis AUCUN texte en dehors de cet objet JSON. La réponse doit commencer par `[` et se terminer par `]`.
        </instruction>
        <texte_original_a_analyser>
        {content_plain_text}
        </texte_original_a_analyser>
        """

        logging.info(f"Sending prompt to {provider_lower} (model: {model_name_to_use})...")
        
        ai_response_text = ""
        if hasattr(ai_service, 'generate_text'):
            ai_response_text = await ai_service.generate_text(prompt)
        elif hasattr(ai_service, 'generate'):
            response_obj = await ai_service.generate(prompt)
            ai_response_text = response_obj.text if hasattr(response_obj, 'text') else str(response_obj)
        else:
            raise NotImplementedError(f"Le service IA {provider_lower} ne supporte pas de méthode de génération reconnue.")

        logging.info(f"Raw AI response: {ai_response_text[:500]}...")

        # Nettoyer et parser la réponse JSON de manière plus robuste
        json_str = None
        # Regex pour trouver un bloc de code JSON, puis fallback sur un JSON brut.
        # Gère ```json ... ```, ``` ... ```, et le JSON brut.
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```|([\s\S]*)", ai_response_text.strip(), re.DOTALL)
        
        if match:
            # Le premier groupe capture le contenu dans ```...```, le second capture tout le reste.
            content = match.group(1) if match.group(1) is not None else match.group(2)
            
            # Essayer de trouver le début d'un objet ou d'une liste JSON dans le contenu extrait
            json_start_match = re.search(r'\[|\{', content)
            if json_start_match:
                # Extraire à partir du premier crochet/accolade trouvé
                json_str = content[json_start_match.start():]
            else:
                json_str = content # Fallback si aucun délimiteur n'est trouvé
        
        if not json_str or not json_str.strip():
            logging.error(f"Aucun contenu JSON valide n'a été trouvé dans la réponse de l'IA.")
            logging.error(f"Réponse brute de l'IA: {ai_response_text}")
            raise HTTPException(status_code=500, detail="La réponse de l'IA ne contenait pas de JSON valide.")
        
        try:
            # Première tentative de parsing direct
            parsed_suggestions = json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.warning(f"Le parsing JSON direct a échoué: {e}. Tentative de réparation du JSON tronqué.")
            # Tentative de réparation si le JSON est tronqué (fréquent avec les LLMs)
            # On cherche la dernière accolade fermante '}' pour délimiter le dernier objet JSON complet
            last_brace_index = json_str.rfind('}')
            if last_brace_index != -1:
                # On prend la sous-chaîne jusqu'au dernier objet complet et on ferme la liste
                repaired_json_str = json_str[:last_brace_index + 1] + ']'
                logging.info(f"Tentative de parsing avec la chaîne JSON réparée: {repaired_json_str[:500]}...")
                try:
                    # Nouvelle tentative avec la chaîne réparée
                    parsed_suggestions = json.loads(repaired_json_str)
                except json.JSONDecodeError as e2:
                    logging.error(f"Impossible de décoder la réponse JSON même après réparation: {e2}")
                    logging.error(f"Chaîne JSON extraite problématique: {json_str}")
                    raise HTTPException(status_code=500, detail="La réponse de l'IA n'était pas un JSON valide, même après tentative de réparation.")
            else:
                # Si aucune accolade n'est trouvée, impossible de réparer
                logging.error(f"Impossible de trouver un objet JSON partiel à réparer.")
                logging.error(f"Chaîne JSON extraite problématique: {json_str}")
                raise HTTPException(status_code=500, detail="La réponse de l'IA ne contenait pas de JSON valide.")

        # La validation Pydantic se fait après avoir obtenu une liste `parsed_suggestions` valide
        try:
            for sugg_data in parsed_suggestions:
                try:
                    suggestions.append(Suggestion(**sugg_data))
                except ValidationError as e:
                    logging.warning(f"Suggestion invalide de l'IA ignorée : {sugg_data}. Erreur: {e}")
        except Exception as e:
            logging.error(f"Erreur lors de la validation Pydantic des suggestions: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la validation des données reçues de l'IA.")

    except HTTPException as e:
        raise e # Propage les erreurs HTTP (ex: clé API manquante)
    except Exception as e:
        logging.error(f"Erreur inattendue lors de l'analyse du chapitre {chapter_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur inattendue du serveur lors de l'analyse: {e}")

    return ChapterAnalysisResponse(chapter_id=chapter_id, stats=stats, suggestions=suggestions)