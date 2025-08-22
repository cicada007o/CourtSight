"""
Configuration management for BNS Legal Assistant.
Handles environment variables, API keys, and system settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the BNS Legal Assistant application."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_EMBEDDING_MODEL: str = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-ada-002')
    
    # Flask Configuration
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'bns-legal-assistant-secret-key-2023')
    
    # Vector Store Configuration
    VECTOR_DB_PATH: str = os.getenv('VECTOR_DB_PATH', './data/vector_db')
    COLLECTION_NAME: str = os.getenv('COLLECTION_NAME', 'bns_legal_documents')
    
    # PDF Processing Configuration
    PDF_DATA_PATH: str = os.getenv('PDF_DATA_PATH', './data')
    CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE', '800'))
    CHUNK_OVERLAP: int = int(os.getenv('CHUNK_OVERLAP', '100'))
    
    # RAG Configuration
    MAX_RETRIEVAL_DOCS: int = int(os.getenv('MAX_RETRIEVAL_DOCS', '5'))
    SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
    
    # System Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_QUERY_LENGTH: int = int(os.getenv('MAX_QUERY_LENGTH', '1000'))
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """
        Validate the configuration settings.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set. Please set it in .env file.")
        
        if not os.path.exists(cls.PDF_DATA_PATH):
            try:
                os.makedirs(cls.PDF_DATA_PATH, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create PDF_DATA_PATH directory: {e}")
        
        if cls.CHUNK_SIZE < 100:
            errors.append("CHUNK_SIZE should be at least 100 characters.")
        
        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            errors.append("CHUNK_OVERLAP should be less than CHUNK_SIZE.")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_summary(cls) -> dict:
        """Get a summary of current configuration settings."""
        return {
            'openai_model': cls.OPENAI_MODEL,
            'embedding_model': cls.OPENAI_EMBEDDING_MODEL,
            'vector_db_path': cls.VECTOR_DB_PATH,
            'chunk_size': cls.CHUNK_SIZE,
            'chunk_overlap': cls.CHUNK_OVERLAP,
            'max_retrieval_docs': cls.MAX_RETRIEVAL_DOCS,
            'similarity_threshold': cls.SIMILARITY_THRESHOLD,
            'api_key_configured': bool(cls.OPENAI_API_KEY),
            'flask_env': cls.FLASK_ENV,
            'log_level': cls.LOG_LEVEL
        }