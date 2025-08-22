"""
PDF processor for BNS legal documents.
Handles extraction, chunking, and metadata preservation for legal content.
"""

import os
import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

@dataclass
class LegalChunk:
    """Data class for legal document chunks with metadata."""
    text: str
    metadata: Dict[str, str]
    confidence: float = 1.0
    
class BNSPDFProcessor:
    """
    Advanced PDF processor for BNS legal documents.
    Preserves legal structure and creates intelligent chunks.
    """
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True
        )
        
        # Legal section patterns
        self.section_patterns = [
            r'Section\s+(\d+)',
            r'Chapter\s+(\d+)',
            r'Part\s+([IVX]+)',
            r'Article\s+(\d+)',
            r'Sub-section\s+\((\d+)\)',
            r'Clause\s+\(([a-z]+)\)'
        ]
        
        # Cross-reference patterns
        self.xref_patterns = [
            r'under\s+section\s+(\d+)',
            r'in\s+section\s+(\d+)',
            r'as\s+defined\s+in\s+section\s+(\d+)',
            r'referred\s+to\s+in\s+section\s+(\d+)'
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF while preserving formatting.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if error
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page_text
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        continue
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            return None
    
    def identify_legal_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Identify legal sections, chapters, and structural elements.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of identified sections with metadata
        """
        sections = []
        
        for pattern in self.section_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                section_info = {
                    'type': pattern.split('\\s+')[0].lower(),
                    'number': match.group(1),
                    'position': match.start(),
                    'full_match': match.group(0)
                }
                sections.append(section_info)
        
        # Sort by position in text
        sections.sort(key=lambda x: x['position'])
        return sections
    
    def extract_cross_references(self, text: str) -> List[str]:
        """
        Extract cross-references to other legal sections.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of cross-referenced sections
        """
        cross_refs = []
        
        for pattern in self.xref_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            cross_refs.extend([f"section_{ref}" for ref in matches])
        
        return list(set(cross_refs))  # Remove duplicates
    
    def classify_content_type(self, text: str) -> str:
        """
        Classify the type of legal content.
        
        Args:
            text: Text to classify
            
        Returns:
            Content type classification
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['punishment', 'penalty', 'fine', 'imprisonment']):
            return 'penalty'
        elif any(word in text_lower for word in ['definition', 'means', 'includes']):
            return 'definition'
        elif any(word in text_lower for word in ['procedure', 'process', 'shall follow']):
            return 'procedure'
        elif any(word in text_lower for word in ['offence', 'crime', 'violation']):
            return 'offence'
        else:
            return 'general'
    
    def create_legal_chunks(self, text: str, source_file: str) -> List[LegalChunk]:
        """
        Create intelligent chunks that respect legal boundaries.
        
        Args:
            text: Input text to chunk
            source_file: Source filename for metadata
            
        Returns:
            List of LegalChunk objects
        """
        # First, identify legal sections
        sections = self.identify_legal_sections(text)
        
        # Create base chunks using text splitter
        base_chunks = self.text_splitter.split_text(text)
        
        legal_chunks = []
        
        for i, chunk in enumerate(base_chunks):
            # Find relevant section for this chunk
            chunk_position = text.find(chunk)
            relevant_section = None
            
            for section in sections:
                if section['position'] <= chunk_position:
                    relevant_section = section
                else:
                    break
            
            # Extract cross-references
            cross_refs = self.extract_cross_references(chunk)
            
            # Classify content
            content_type = self.classify_content_type(chunk)
            
            # Create metadata
            metadata = {
                'source': source_file,
                'chunk_id': str(i),
                'content_type': content_type,
                'cross_references': ','.join(cross_refs) if cross_refs else '',
                'section_type': relevant_section['type'] if relevant_section else 'unknown',
                'section_number': relevant_section['number'] if relevant_section else '',
                'word_count': str(len(chunk.split())),
                'char_count': str(len(chunk))
            }
            
            # Calculate confidence based on chunk quality
            confidence = self._calculate_chunk_confidence(chunk, metadata)
            
            legal_chunk = LegalChunk(
                text=chunk.strip(),
                metadata=metadata,
                confidence=confidence
            )
            
            legal_chunks.append(legal_chunk)
        
        logger.info(f"Created {len(legal_chunks)} legal chunks from {source_file}")
        return legal_chunks
    
    def _calculate_chunk_confidence(self, chunk: str, metadata: Dict[str, str]) -> float:
        """
        Calculate confidence score for chunk quality.
        
        Args:
            chunk: Text chunk
            metadata: Chunk metadata
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 1.0
        
        # Reduce confidence for very short chunks
        if len(chunk) < 100:
            confidence -= 0.2
        
        # Increase confidence for chunks with clear section markers
        if metadata.get('section_number'):
            confidence += 0.1
        
        # Reduce confidence for chunks with incomplete sentences
        if not chunk.strip().endswith(('.', '!', '?', ':')):
            confidence -= 0.1
        
        # Increase confidence for legal content types
        if metadata.get('content_type') in ['definition', 'penalty', 'procedure']:
            confidence += 0.1
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def process_bns_documents(self, pdf_directory: str = None) -> List[LegalChunk]:
        """
        Process all BNS PDF documents in the specified directory.
        
        Args:
            pdf_directory: Directory containing BNS PDF files
            
        Returns:
            List of all legal chunks from processed documents
        """
        if pdf_directory is None:
            pdf_directory = Config.PDF_DATA_PATH
        
        if not os.path.exists(pdf_directory):
            logger.error(f"PDF directory does not exist: {pdf_directory}")
            return []
        
        all_chunks = []
        pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_directory}")
            return []
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            logger.info(f"Processing PDF: {pdf_file}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                logger.error(f"Failed to extract text from {pdf_file}")
                continue
            
            # Create chunks
            chunks = self.create_legal_chunks(text, pdf_file)
            all_chunks.extend(chunks)
        
        logger.info(f"Processed {len(pdf_files)} PDFs, created {len(all_chunks)} total chunks")
        return all_chunks
    
    def get_processing_stats(self, chunks: List[LegalChunk]) -> Dict[str, any]:
        """
        Get statistics about processed chunks.
        
        Args:
            chunks: List of legal chunks
            
        Returns:
            Dictionary with processing statistics
        """
        if not chunks:
            return {'total_chunks': 0}
        
        content_types = {}
        total_words = 0
        confidence_scores = []
        
        for chunk in chunks:
            # Count content types
            content_type = chunk.metadata.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Count words
            word_count = int(chunk.metadata.get('word_count', '0'))
            total_words += word_count
            
            # Collect confidence scores
            confidence_scores.append(chunk.confidence)
        
        return {
            'total_chunks': len(chunks),
            'content_types': content_types,
            'total_words': total_words,
            'average_words_per_chunk': total_words / len(chunks),
            'average_confidence': sum(confidence_scores) / len(confidence_scores),
            'sources': list(set(chunk.metadata.get('source', '') for chunk in chunks))
        }