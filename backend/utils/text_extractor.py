import io
import logging
from typing import Optional

import chardet
import docx
from odf import opendocument, text as odf_text
from pypdf import PdfReader
from pypdf.errors import PdfReadError

logger = logging.getLogger(__name__)

def _extract_text_from_pdf(file_content: bytes) -> str:
    """Extracts text from PDF content."""
    try:
        reader = PdfReader(io.BytesIO(file_content))
        text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
        return "\n".join(text_parts)
    except PdfReadError as e:
        logger.error(f"Error reading PDF file: {e}")
        raise ValueError("Could not read PDF file. It might be corrupted or password-protected.") from e
    except Exception as e:
        logger.error(f"Unexpected error extracting text from PDF: {e}")
        raise ValueError("An unexpected error occurred while processing the PDF file.") from e

def _extract_text_from_docx(file_content: bytes) -> str:
    """Extracts text from DOCX content."""
    try:
        document = docx.Document(io.BytesIO(file_content))
        text_parts = [p.text for p in document.paragraphs]
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        raise ValueError("Could not process DOCX file.") from e

def _extract_text_from_odt(file_content: bytes) -> str:
    """Extracts text from ODT content."""
    try:
        doc = opendocument.load(io.BytesIO(file_content))
        all_paras = doc.getElementsByType(odf_text.P)
        text_parts = [odf_text.extractText(para) for para in all_paras]
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"Error extracting text from ODT: {e}")
        raise ValueError("Could not process ODT file.") from e

def _extract_text_from_txt(file_content: bytes) -> str:
    """Extracts text from TXT content, detecting encoding."""
    try:
        detected_encoding = chardet.detect(file_content)['encoding']
        if detected_encoding:
            logger.info(f"Detected encoding: {detected_encoding}")
            return file_content.decode(detected_encoding, errors='replace')
        else:
            # Fallback to common encodings if detection fails
            logger.warning("Could not detect encoding. Trying UTF-8 and Latin-1.")
            try:
                return file_content.decode('utf-8')
            except UnicodeDecodeError:
                return file_content.decode('latin-1', errors='replace')
    except Exception as e:
        logger.error(f"Error decoding TXT file: {e}")
        raise ValueError("Could not decode TXT file.") from e


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extracts text from the content of an uploaded file based on its extension.

    Args:
        file_content: The binary content of the file.
        filename: The original name of the file, used to determine the type.

    Returns:
        The extracted text as a string.

    Raises:
        ValueError: If the file format is unsupported or an error occurs during extraction.
    """
    filename_lower = filename.lower()
    text = ""

    logger.info(f"Attempting to extract text from file: {filename}")

    if filename_lower.endswith(".pdf"):
        text = _extract_text_from_pdf(file_content)
    elif filename_lower.endswith(".docx"):
        text = _extract_text_from_docx(file_content)
    elif filename_lower.endswith(".odt"):
        text = _extract_text_from_odt(file_content)
    elif filename_lower.endswith(".txt"):
        text = _extract_text_from_txt(file_content)
    else:
        logger.warning(f"Unsupported file format for file: {filename}")
        raise ValueError("Unsupported file format. Please upload PDF, DOCX, ODT, or TXT.")

    if not text or text.isspace():
        logger.warning(f"No text could be extracted from file: {filename}")
        # Return empty string instead of raising error if extraction technically succeeded but found no text
        # raise ValueError("No text could be extracted from the file.")
        return ""

    logger.info(f"Successfully extracted text from {filename} (length: {len(text)} chars)")
    return text