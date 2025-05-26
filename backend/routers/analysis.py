import spacy
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
import re
import json
from pydantic import BaseModel, Field, ValidationError
from bs4 import BeautifulSoup

# Importer les modèles SQLAlchemy et la session DB (Imports relatifs)
from .. import models
from ..database import get_db
# Importer les nouveaux modèles Pydantic pour l'analyse de chapitre (Import relatif)
from ..models import ChapterAnalysisResponse, ChapterAnalysisStats, Suggestion
# Importer la factory et l'adapter IA (Imports relatifs)
from ..ai_services.factory import create_adapter
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
        # On pourrait lever une exception ici ou laisser l'application démarrer
        # mais les routes d'analyse échoueront. Pour l'instant, on logue l'erreur.
        nlp = None # Indiquer que spaCy n'est pas fonctionnel

router = APIRouter(
    
    tags=["analysis"],
    responses={500: {"description": "Internal Server Error"}},
)

# --- Schémas Pydantic pour l'analyse de cohérence (déjà présents) ---

class ConsistencyAnalysisRequest(models.ConsistencyAnalysisRequest):
    pass

class EntityInfo(models.EntityInfo):
    pass

class ConsistencyAnalysisResponse(models.ConsistencyAnalysisResponse):
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

    # 1. Récupérer le projet et ses chapitres
    project = db.query(models.Project).filter(models.Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Récupérer le contenu de tous les chapitres du projet
    chapters = db.query(models.Chapter).filter(models.Chapter.project_id == request.project_id).all()
    if not chapters:
        return ConsistencyAnalysisResponse(
            project_id=request.project_id,
            total_chapters=0,
            total_words=0,
            warnings=["Aucun chapitre trouvé pour ce projet."]
        )

    # 2. Concaténer le texte des chapitres (utiliser le contenu HTML tel quel pour l'analyse spaCy)
    full_text = ""
    for chapter in chapters:
        if chapter.content:
            # Ajouter un séparateur clair (peut aider le modèle NLP)
            full_text += f"\n\n--- CHAPITRE: {chapter.title} ---\n\n" + chapter.content

    if not full_text.strip():
        return ConsistencyAnalysisResponse(
            project_id=request.project_id,
            total_chapters=len(chapters),
            total_words=0,
            warnings=["Les chapitres de ce projet sont vides."]
        )

    # 3. Analyser le texte avec spaCy
    logging.info(f"Processing text with spaCy (length: {len(full_text)} chars)...")
    doc = nlp(full_text)
    logging.info("spaCy processing complete.")

    # 4. Extraire les entités et compter les occurrences
    entity_counts: Dict[tuple, int] = {} # Utiliser (text.lower(), label) comme clé
    total_words = 0
    for token in doc:
        if not token.is_punct and not token.is_space:
            total_words += 1

    for ent in doc.ents:
        # Filtrer les entités pertinentes (ex: Personnes, Lieux, Organisations)
        if ent.label_ in ["PER", "LOC", "ORG"]:
            key = (ent.text.lower(), ent.label_)
            entity_counts[key] = entity_counts.get(key, 0) + 1
            
    # Formater les entités pour la réponse
    entities_response: List[EntityInfo] = []
    for (text, label), count in sorted(entity_counts.items(), key=lambda item: item[1], reverse=True):
         entities_response.append(EntityInfo(text=text, label=label, count=count))

    # 5. Ajouter des avertissements simples (Exemple: variations orthographiques - très basique)
    warnings = []
    # TODO: Implémenter une logique plus avancée pour détecter les variations (ex: distance de Levenshtein)

    logging.info(f"Analysis complete for project {request.project_id}. Found {len(entities_response)} unique entities.")

    return ConsistencyAnalysisResponse(
        project_id=request.project_id,
        total_chapters=len(chapters),
        total_words=total_words,
        entities=entities_response,
        warnings=warnings
    )

# --- NOUVEAU: Endpoint pour l'analyse de contenu de chapitre ---

# Schéma pour la requête
class ChapterAnalysisRequest(BaseModel):
    provider: str = Field(..., description="Fournisseur IA à utiliser (ex: 'gemini', 'mistral')")
    model: Optional[str] = Field(None, description="Modèle spécifique à utiliser (si non fourni, utilise le défaut du fournisseur)")
    # Ajouter d'autres options si nécessaire (ex: types d'analyse à effectuer)


@router.post("/chapters/{chapter_id}/analyze-content", response_model=ChapterAnalysisResponse)
async def analyze_chapter_content(
    chapter_id: int,
    request: ChapterAnalysisRequest, # Accepter les options de la requête
    db: Session = Depends(get_db)
):
    """
    Analyse le contenu d'un chapitre spécifique pour obtenir des statistiques
    et des suggestions d'amélioration via IA, incluant les indices de position.
    """
    logging.info(f"Starting content analysis for chapter_id: {chapter_id}")

    # 1. Récupérer le chapitre
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    content_html = chapter.content if chapter.content else ""
    if not content_html.strip():
        logging.warning(f"Chapter {chapter_id} content is empty. Returning basic stats.")
        # Retourner des stats vides mais valides
        stats = ChapterAnalysisStats(word_count=0)
        return ChapterAnalysisResponse(chapter_id=chapter_id, stats=stats, suggestions=[])

    # Extraire le texte brut du contenu HTML
    soup = BeautifulSoup(content_html, 'html.parser')
    content_plain_text = soup.get_text()

    # NOUVEAU LOG: Afficher le texte brut envoyé à l'IA
    logging.info(f"Plain text sent to AI (length: {len(content_plain_text)}): {content_plain_text[:500]}...") # Log les 500 premiers caractères

    # 2. Calculer les statistiques de base sur le texte brut
    word_count = len(content_plain_text.split())
    stats = ChapterAnalysisStats(word_count=word_count)

    # 3. Préparer et exécuter l'appel IA pour les suggestions
    suggestions: List[Suggestion] = []
    try:
        provider_lower = request.provider.lower()

        # Vérification explicite si le fournisseur est supporté
        if provider_lower not in crud_api_keys.SUPPORTED_PROVIDERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fournisseur non supporté : {request.provider}"
            )

        # Essayer de récupérer la clé API (DB puis fallback .env)
        api_key_to_use = crud_api_keys.get_decrypted_api_key(db, provider_lower, settings_fallback=settings)

        if not api_key_to_use:
            logging.warning(f"Aucune clé API trouvée (DB ou .env) pour le provider: {provider_lower} lors de l'analyse de chapitre.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Clé API non configurée pour le fournisseur : {request.provider}. Veuillez la configurer via l'interface ou le fichier .env."
            )

        ai_service: AIAdapter = create_adapter(provider_lower, api_key=api_key_to_use, model=request.model)

        # MODIFICATION: Ajustement du prompt pour demander les indices sur le TEXTE BRUT
        prompt = f"""
        Analyse le texte suivant d'un chapitre de roman et fournis des suggestions d'amélioration.
        **Priorité absolue : Corriger toutes les erreurs factuelles.**
        Ensuite, propose des améliorations légères si nécessaire.

        Points d'attention principaux :
        1.  **Correction Factuelle (Priorité Haute) :**
            -   Orthographe
            -   Grammaire (accords, conjugaison, syntaxe)
            -   Ponctuation
        2.  **Améliorations Légères (Priorité Moyenne) :**
            -   Clarté : Reformuler les phrases ambiguës ou difficiles à comprendre.
            -   Fluidité : Suggérer des transitions plus douces ou corriger les phrases hachées.
            -   Répétitions : Identifier et proposer des alternatives pour les mots ou expressions répétés de manière excessive et proche.
        3.  **Style (Priorité Basse) :**
            -   Éviter les suggestions de refonte stylistique majeure ou de changement de ton. Se concentrer sur les points ci-dessus.
            -   Ne pas proposer de synonymes juste pour varier si le mot original est correct et clair.

        TEXTE À ANALYSER :
        ---
        {content_plain_text}
        ---

        FORMAT DE SORTIE ATTENDU :
        Fournis ta réponse **uniquement** sous forme d'un objet JSON valide contenant une clé "suggestions".
        La valeur de "suggestions" doit être une liste d'objets JSON, où chaque objet représente une suggestion et a les clés suivantes :
        - "original_text": (string) Le segment de texte exact concerné par la suggestion.
        - "suggested_text": (string) Le texte de remplacement proposé.
        - "suggestion_type": (string) Le type de suggestion (utiliser principalement : 'orthographe', 'grammaire', 'ponctuation', 'clarté', 'fluidité', 'répétition').
        - "explanation": (string, optionnel) Une brève explication de la suggestion.
        - "start_index": (integer) L'index de début (basé sur 0) du premier caractère de 'original_text' dans le TEXTE À ANALYSER complet.
        - "end_index": (integer) L'index de fin (exclusif, basé sur 0) du dernier caractère de 'original_text' dans le TEXTE À ANALYSER complet. Assure-toi que `TEXTE_A_ANALYSER[start_index:end_index]` correspond exactement à `original_text`.

        Exemple de format JSON attendu :
        {{
          "suggestions": [
            {{
              "original_text": "Il etait trés fatigué.",
              "suggested_text": "Il était très fatigué.",
              "suggestion_type": "orthographe",
              "explanation": "Correction orthographique et accentuation.",
              "start_index": 15, // Exemple d'index
              "end_index": 36   // Exemple d'index
            }},
            {{
              "original_text": "Le chat noir a traversé la route noire.",
              "suggested_text": "Le chat noir a traversé la route.",
              "suggestion_type": "répétition",
              "explanation": "Suppression de la répétition du mot 'noir'.",
              "start_index": 50, // Exemple d'index
              "end_index": 88  // Exemple d'index
            }}
          ]
        }}

        Ne fournis **aucun texte** avant ou après l'objet JSON.
        """

        logging.info(f"Sending analysis request to AI provider: {request.provider}, model: {request.model or 'default'}")
        ai_response_text = await ai_service.generate(
            prompt=prompt
        )
        logging.info("Received response from AI.")
        logging.info(f"Raw AI response before parsing: {ai_response_text}")


        # 4. Parser la réponse JSON de l'IA
        try:
            json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                ai_response_data = json.loads(json_str)
                if "suggestions" in ai_response_data and isinstance(ai_response_data["suggestions"], list):
                    # NOUVEAU: Log la liste brute des suggestions reçues de l'IA
                    logging.info(f"Raw suggestions from AI: {ai_response_data['suggestions']}")

                    for sugg_data in ai_response_data["suggestions"]:
                        try:
                            # Tenter de trouver l'original_text dans le texte brut
                            original_text = sugg_data.get("original_text")
                            if original_text:
                                found_index = content_plain_text.find(original_text)

                                if found_index != -1:
                                    # Si trouvé, utiliser les indices trouvés par Python
                                    start = found_index
                                    end = found_index + len(original_text)

                                    # Créer un dictionnaire avec les données de suggestion, en remplaçant les indices
                                    validated_sugg_data = sugg_data.copy()
                                    validated_sugg_data["start_index"] = start
                                    validated_sugg_data["end_index"] = end

                                    # Valider avec le modèle Pydantic
                                    suggestion_obj = Suggestion(**validated_sugg_data)
                                    suggestions.append(suggestion_obj)
                                    logging.info(f"Suggestion validated and added: {suggestion_obj.original_text} -> {suggestion_obj.suggested_text}")
                                else:
                                    # Si original_text non trouvé dans le texte brut
                                    logging.warning(
                                        f"Skipping suggestion: original_text '{original_text}' not found in plain text. "
                                        f"Full suggestion data: {sugg_data}"
                                    )
                            else:
                                # Si original_text est manquant dans la suggestion de l'IA
                                logging.warning(f"Skipping suggestion: 'original_text' missing in suggestion data. Full suggestion data: {sugg_data}")

                        except ValidationError as pydantic_error:
                            logging.warning(f"Skipping invalid suggestion data due to Pydantic validation error: {sugg_data} - Error: {pydantic_error}")
                        except Exception as e:
                             logging.warning(f"Skipping suggestion due to unexpected error during validation: {sugg_data} - Error: {e}")
                else:
                     logging.warning("AI response JSON does not contain a valid 'suggestions' list.")
            else:
                logging.warning("Could not find valid JSON object in AI response.")

        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response from AI: {e}")
            logging.debug(f"Raw AI response: {ai_response_text}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while parsing AI response: {e}")
            logging.debug(f"Raw AI response: {ai_response_text}")

    except HTTPException as e:
         raise e
    except Exception as e:
        logging.error(f"Failed to get suggestions from AI for chapter {chapter_id}: {e}")

    # 5. Retourner la réponse complète
    logging.info(f"Analysis complete for chapter {chapter_id}. Found {len(suggestions)} suggestions.")
    return ChapterAnalysisResponse(
        chapter_id=chapter_id,
        stats=stats,
        suggestions=suggestions
    )