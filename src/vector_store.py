"""
Vector store management using ChromaDB for BNS legal documents.
Handles embedding generation, storage, and similarity search.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
import openai
from openai import OpenAI
from src.config import Config
from src.pdf_processor import LegalChunk

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class BNSVectorStore:
    """
    Vector store for BNS legal documents using ChromaDB and OpenAI embeddings.
    """
    
    def __init__(self):
        # Initialize OpenAI client
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Initialize ChromaDB
        os.makedirs(Config.VECTOR_DB_PATH, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(
            path=Config.VECTOR_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(Config.COLLECTION_NAME)
            logger.info(f"Loaded existing collection: {Config.COLLECTION_NAME}")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"description": "BNS Legal Documents Vector Store"}
            )
            logger.info(f"Created new collection: {Config.COLLECTION_NAME}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI's embedding model.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=Config.OPENAI_EMBEDDING_MODEL,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def add_chunks(self, chunks: List[LegalChunk]) -> bool:
        """
        Add legal chunks to the vector store.
        
        Args:
            chunks: List of LegalChunk objects to add
            
        Returns:
            True if successful, False otherwise
        """
        if not chunks:
            logger.warning("No chunks to add")
            return True
        
        try:
            # Prepare data for ChromaDB
            texts = [chunk.text for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"{chunk.metadata.get('source', 'unknown')}_{chunk.metadata.get('chunk_id', i)}" 
                   for i, chunk in enumerate(chunks)]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {e}")
            return False
    
    def similarity_search(self, query: str, n_results: int = None, 
                         filters: Dict = None) -> List[Dict]:
        """
        Perform similarity search for legal queries.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of search results with relevance scores
        """
        if n_results is None:
            n_results = Config.MAX_RETRIEVAL_DOCS
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings([query])[0]
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filters,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'relevance': self._calculate_relevance(
                            query, doc, results['metadatas'][0][i] if results['metadatas'] else {}
                        )
                    }
                    formatted_results.append(result)
            
            # Filter by similarity threshold
            filtered_results = [
                r for r in formatted_results 
                if r['similarity_score'] >= Config.SIMILARITY_THRESHOLD
            ]
            
            logger.info(f"Found {len(filtered_results)} relevant results for query")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def _calculate_relevance(self, query: str, document: str, metadata: Dict) -> float:
        """
        Calculate enhanced relevance score considering legal factors.
        
        Args:
            query: Original query
            document: Retrieved document
            metadata: Document metadata
            
        Returns:
            Enhanced relevance score
        """
        base_score = 0.5
        
        # Boost for exact term matches
        query_terms = query.lower().split()
        document_lower = document.lower()
        term_matches = sum(1 for term in query_terms if term in document_lower)
        term_boost = (term_matches / len(query_terms)) * 0.2
        
        # Boost for legal content types
        content_type = metadata.get('content_type', '')
        if content_type in ['definition', 'penalty']:
            content_boost = 0.15
        elif content_type in ['procedure', 'offence']:
            content_boost = 0.1
        else:
            content_boost = 0.0
        
        # Boost for section information
        section_boost = 0.1 if metadata.get('section_number') else 0.0
        
        # Boost for cross-references
        xref_boost = 0.05 if metadata.get('cross_references') else 0.0
        
        total_score = base_score + term_boost + content_boost + section_boost + xref_boost
        return min(1.0, total_score)
    
    def hybrid_search(self, query: str, n_results: int = None) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword matching.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            Combined search results
        """
        if n_results is None:
            n_results = Config.MAX_RETRIEVAL_DOCS
        
        # Perform semantic search
        semantic_results = self.similarity_search(query, n_results * 2)
        
        # Perform keyword search by filtering collection
        keyword_results = self._keyword_search(query, n_results)
        
        # Combine and rank results
        combined_results = self._combine_search_results(
            semantic_results, keyword_results, n_results
        )
        
        return combined_results
    
    def _keyword_search(self, query: str, n_results: int) -> List[Dict]:
        """
        Perform keyword-based search using document text matching.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            Keyword search results
        """
        try:
            # Get all documents (this could be optimized with better indexing)
            all_results = self.collection.get(
                include=['documents', 'metadatas']
            )
            
            keyword_matches = []
            query_terms = query.lower().split()
            
            for i, doc in enumerate(all_results['documents']):
                doc_lower = doc.lower()
                
                # Count keyword matches
                matches = sum(1 for term in query_terms if term in doc_lower)
                if matches > 0:
                    score = matches / len(query_terms)
                    keyword_matches.append({
                        'text': doc,
                        'metadata': all_results['metadatas'][i],
                        'similarity_score': score,
                        'relevance': score
                    })
            
            # Sort by score and return top results
            keyword_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            return keyword_matches[:n_results]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def _combine_search_results(self, semantic_results: List[Dict], 
                               keyword_results: List[Dict], n_results: int) -> List[Dict]:
        """
        Combine semantic and keyword search results.
        
        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            n_results: Number of final results to return
            
        Returns:
            Combined and ranked results
        """
        # Create a dictionary to merge results by document text
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            text = result['text']
            combined[text] = result.copy()
            combined[text]['semantic_score'] = result['similarity_score']
        
        # Add keyword results and boost scores
        for result in keyword_results:
            text = result['text']
            if text in combined:
                # Boost existing result
                combined[text]['similarity_score'] = max(
                    combined[text]['similarity_score'],
                    result['similarity_score']
                ) * 1.1  # Small boost for appearing in both searches
                combined[text]['keyword_score'] = result['similarity_score']
            else:
                # Add new result
                combined[text] = result.copy()
                combined[text]['keyword_score'] = result['similarity_score']
                combined[text]['semantic_score'] = 0.0
        
        # Convert back to list and sort by combined score
        final_results = list(combined.values())
        final_results.sort(
            key=lambda x: (x['similarity_score'] + x.get('keyword_score', 0)) / 2,
            reverse=True
        )
        
        return final_results[:n_results]
    
    def get_collection_stats(self) -> Dict[str, any]:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            if count > 0:
                # Get sample of metadata to analyze
                sample = self.collection.get(
                    include=['metadatas'],
                    limit=min(100, count)
                )
                
                content_types = {}
                sources = set()
                
                for metadata in sample['metadatas']:
                    content_type = metadata.get('content_type', 'unknown')
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                    sources.add(metadata.get('source', 'unknown'))
                
                return {
                    'total_documents': count,
                    'content_types': content_types,
                    'sources': list(sources),
                    'collection_name': Config.COLLECTION_NAME,
                    'embedding_model': Config.OPENAI_EMBEDDING_MODEL
                }
            else:
                return {
                    'total_documents': 0,
                    'message': 'Collection is empty'
                }
                
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}
    
    def reset_collection(self) -> bool:
        """
        Reset the vector store collection (delete all data).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.chroma_client.delete_collection(Config.COLLECTION_NAME)
            self.collection = self.chroma_client.create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"description": "BNS Legal Documents Vector Store"}
            )
            logger.info(f"Reset collection: {Config.COLLECTION_NAME}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False
    
    def health_check(self) -> Dict[str, any]:
        """
        Perform health check on the vector store.
        
        Returns:
            Health status information
        """
        try:
            # Check collection accessibility
            count = self.collection.count()
            
            # Test embedding generation
            test_embedding = self.generate_embeddings(["test query"])
            
            # Test search functionality
            if count > 0:
                test_results = self.collection.query(
                    query_embeddings=[test_embedding[0]],
                    n_results=1
                )
                search_working = len(test_results['documents'][0]) > 0
            else:
                search_working = True  # No documents to search
            
            return {
                'status': 'healthy',
                'collection_accessible': True,
                'document_count': count,
                'embedding_generation': True,
                'search_functionality': search_working,
                'openai_api': True
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'collection_accessible': False,
                'embedding_generation': False,
                'search_functionality': False,
                'openai_api': False
            }