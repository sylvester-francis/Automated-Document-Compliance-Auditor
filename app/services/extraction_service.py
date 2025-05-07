# app/services/extraction_service.py
import os
import re
from typing import List, Tuple, Dict
import uuid

import PyPDF2
import docx
from flask import current_app

def extract_text_from_pdf(file_path: str) -> Tuple[str, List[Dict]]:
    """
    Extract text and paragraphs from a PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple of (full_text, paragraphs)
    """
    full_text = ""
    paragraphs = []
    
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            
            if page_text:
                full_text += page_text + "\n\n"
                
                # Split into paragraphs (by double newline)
                para_texts = [p for p in re.split(r'\n\s*\n', page_text) if p.strip()]
                
                # Add each paragraph
                for position, para_text in enumerate(para_texts):
                    clean_text = para_text.strip()
                    if clean_text:
                        paragraph_id = f"p_{page_num}_{position}_{str(uuid.uuid4())[:8]}"
                        paragraphs.append({
                            "id": paragraph_id,
                            "text": clean_text,
                            "page": page_num + 1,
                            "position": position
                        })
    
    return full_text, paragraphs

def extract_text_from_docx(file_path: str) -> Tuple[str, List[Dict]]:
    """
    Extract text and paragraphs from a DOCX file
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Tuple of (full_text, paragraphs)
    """
    full_text = ""
    paragraphs = []
    
    doc = docx.Document(file_path)
    
    for position, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text:
            full_text += text + "\n\n"
            paragraph_id = f"p_{position}_{str(uuid.uuid4())[:8]}"
            paragraphs.append({
                "id": paragraph_id,
                "text": text,
                "position": position
            })
    
    return full_text, paragraphs

def extract_text_from_txt(file_path: str) -> Tuple[str, List[Dict]]:
    """
    Extract text and paragraphs from a plain text file
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Tuple of (full_text, paragraphs)
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        full_text = file.read()
    
    paragraphs = []
    # Split by empty lines
    para_texts = [p for p in re.split(r'\n\s*\n', full_text) if p.strip()]
    
    for position, para_text in enumerate(para_texts):
        clean_text = para_text.strip()
        if clean_text:
            paragraph_id = f"p_{position}_{str(uuid.uuid4())[:8]}"
            paragraphs.append({
                "id": paragraph_id,
                "text": clean_text,
                "position": position
            })
    
    return full_text, paragraphs

def extract_document_text(file_path: str) -> Tuple[str, List[Dict]]:
    """
    Extract text from a document based on its file extension
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Tuple of (full_text, paragraphs)
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")