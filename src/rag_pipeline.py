"""
RAG (Retrieval-Augmented Generation) pipeline for BNS legal queries.
Combines document retrieval with OpenAI GPT for intelligent legal responses.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from src.config import Config
from src.vector_store import BNSVectorStore

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class BNSRAGPipeline:
    """
    Complete RAG pipeline for BNS legal question answering.
    """
    
    def __init__(self):
        # Initialize OpenAI client
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.vector_store = BNSVectorStore()
        
        # Legal query enhancement patterns
        self.legal_terms = {
            'crime': ['offence', 'criminal act', 'violation'],
            'punishment': ['penalty', 'sentence', 'imprisonment', 'fine'],
            'law': ['provision', 'section', 'clause', 'regulation'],
            'court': ['tribunal', 'judiciary', 'legal proceedings'],
            'rights': ['legal rights', 'constitutional rights', 'fundamental rights']
        }
        
        # System prompts for different types of legal queries
        self.system_prompts = {
            'general': """You are a legal expert specializing in the Bharatiya Nyaya Sanhita (BNS) 2023. 
                         Provide accurate, helpful legal information based only on the provided context. 
                         Always cite relevant sections when available. If information is not in the context, 
                         state this clearly. Provide practical guidance while emphasizing the need for 
                         professional legal consultation for specific cases.""",
            
            'definition': """You are a legal expert explaining definitions from the Bharatiya Nyaya Sanhita (BNS) 2023. 
                           Provide clear, precise definitions based on the provided context. Include the exact 
                           section number and explain the definition in simple terms. If there are related 
                           terms or cross-references, mention them.""",
            
            'penalty': """You are a legal expert explaining penalties and punishments under the Bharatiya Nyaya Sanhita (BNS) 2023. 
                         Clearly state the specific penalties, including imprisonment terms, fines, or other 
                         punishments. Always cite the exact section. Explain any conditions or variations 
                         in penalties. Emphasize that actual sentences may vary based on circumstances.""",
            
            'procedure': """You are a legal expert explaining legal procedures under the Bharatiya Nyaya Sanhita (BNS) 2023. 
                          Provide step-by-step explanations of legal processes based on the provided context. 
                          Include relevant section references and explain the practical implications. 
                          Mention any prerequisites or conditions that must be met."""
        }
    
    def enhance_query(self, query: str) -> str:
        """
        Enhance legal queries with expanded terms and context.
        
        Args:
            query: Original user query
            
        Returns:
            Enhanced query with legal terminology
        """
        enhanced_query = query.lower()
        
        # Expand common legal terms
        for base_term, synonyms in self.legal_terms.items():
            if base_term in enhanced_query:
                enhanced_query += f" {' '.join(synonyms)}"
        
        # Add BNS context if not present
        if 'bns' not in enhanced_query and 'bharatiya nyaya sanhita' not in enhanced_query:
            enhanced_query += " bharatiya nyaya sanhita bns 2023"
        
        return enhanced_query
    
    def classify_query_type(self, query: str) -> str:
        """
        Classify the type of legal query to use appropriate system prompt.
        
        Args:
            query: User query
            
        Returns:
            Query type classification
        """
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what is', 'define', 'definition', 'means']):
            return 'definition'
        elif any(word in query_lower for word in ['punishment', 'penalty', 'sentence', 'fine']):
            return 'penalty'
        elif any(word in query_lower for word in ['procedure', 'process', 'how to', 'steps']):
            return 'procedure'
        else:
            return 'general'
    
    def retrieve_relevant_documents(self, query: str) -> List[Dict]:
        """
        Retrieve relevant documents using hybrid search.
        
        Args:
            query: User query
            
        Returns:
            List of relevant documents with metadata
        """
        try:
            # Enhance query for better retrieval
            enhanced_query = self.enhance_query(query)
            
            # Perform hybrid search
            documents = self.vector_store.hybrid_search(
                enhanced_query, 
                n_results=Config.MAX_RETRIEVAL_DOCS
            )
            
            logger.info(f"Retrieved {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def build_context(self, documents: List[Dict]) -> str:
        """
        Build context from retrieved documents for GPT.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant legal documents found."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
            
            # Format document with metadata
            doc_context = f"Document {i}:\n"
            
            if metadata.get('section_number'):
                doc_context += f"Section {metadata['section_number']}: "
            
            if metadata.get('content_type'):
                doc_context += f"[{metadata['content_type'].title()}] "
            
            doc_context += f"{text}\n"
            
            if metadata.get('cross_references'):
                doc_context += f"Cross-references: {metadata['cross_references']}\n"
            
            context_parts.append(doc_context)
        
        return "\n---\n".join(context_parts)
    
    def generate_response(self, query: str, context: str, query_type: str) -> Dict[str, any]:
        """
        Generate response using OpenAI GPT with retrieved context.
        
        Args:
            query: Original user query
            context: Retrieved document context
            query_type: Type of query (general, definition, penalty, procedure)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            system_prompt = self.system_prompts.get(query_type, self.system_prompts['general'])
            
            user_prompt = f"""Context from Bharatiya Nyaya Sanhita (BNS) 2023:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context above. Include:
1. A clear, direct answer to the question
2. Relevant section numbers and citations
3. Practical implications when applicable
4. Any important warnings or disclaimers

If the context doesn't contain enough information to answer the question completely, please state this clearly."""
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for factual legal responses
                max_tokens=1500
            )
            
            answer = response.choices[0].message.content
            
            # Extract sections mentioned in the response
            sections = self._extract_sections(answer)
            
            return {
                'answer': answer,
                'sections_cited': sections,
                'model_used': Config.OPENAI_MODEL,
                'query_type': query_type,
                'response_length': len(answer),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'answer': "I apologize, but I'm unable to process your legal query at the moment. Please try again later or consult with a legal professional.",
                'sections_cited': [],
                'model_used': Config.OPENAI_MODEL,
                'query_type': query_type,
                'error': str(e),
                'success': False
            }
    
    def _extract_sections(self, text: str) -> List[str]:
        """
        Extract section references from generated response.
        
        Args:
            text: Generated response text
            
        Returns:
            List of section references
        """
        section_patterns = [
            r'[Ss]ection\s+(\d+)',
            r'[Ss]ec\.\s*(\d+)',
            r'§\s*(\d+)'
        ]
        
        sections = []
        for pattern in section_patterns:
            matches = re.findall(pattern, text)
            sections.extend([f"Section {match}" for match in matches])
        
        return list(set(sections))  # Remove duplicates
    
    def calculate_confidence(self, retrieved_docs: List[Dict], 
                           response_data: Dict[str, any]) -> float:
        """
        Calculate confidence score for the generated response.
        
        Args:
            retrieved_docs: Documents used for context
            response_data: Generated response data
            
        Returns:
            Confidence score between 0 and 1
        """
        if not response_data.get('success'):
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Boost for number of relevant documents
        if len(retrieved_docs) >= 3:
            confidence += 0.2
        elif len(retrieved_docs) >= 1:
            confidence += 0.1
        
        # Boost for document relevance scores
        if retrieved_docs:
            avg_relevance = sum(doc.get('relevance', 0) for doc in retrieved_docs) / len(retrieved_docs)
            confidence += avg_relevance * 0.2
        
        # Boost for section citations
        sections_cited = response_data.get('sections_cited', [])
        if len(sections_cited) >= 2:
            confidence += 0.15
        elif len(sections_cited) >= 1:
            confidence += 0.1
        
        # Boost for specific content types
        content_types = [doc.get('metadata', {}).get('content_type', '') for doc in retrieved_docs]
        if any(ct in ['definition', 'penalty'] for ct in content_types):
            confidence += 0.1
        
        # Penalty for very short responses (likely incomplete)
        response_length = response_data.get('response_length', 0)
        if response_length < 100:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def process_query(self, query: str) -> Dict[str, any]:
        """
        Process a complete legal query through the RAG pipeline.
        
        Args:
            query: User's legal question
            
        Returns:
            Complete response with metadata
        """
        try:
            # Validate query
            if not query or len(query.strip()) < 5:
                return {
                    'answer': "Please provide a more specific legal question.",
                    'confidence': 0.0,
                    'success': False,
                    'error': "Query too short or empty"
                }
            
            if len(query) > Config.MAX_QUERY_LENGTH:
                return {
                    'answer': f"Query is too long. Please limit to {Config.MAX_QUERY_LENGTH} characters.",
                    'confidence': 0.0,
                    'success': False,
                    'error': "Query too long"
                }
            
            # Classify query type
            query_type = self.classify_query_type(query)
            
            # Retrieve relevant documents
            retrieved_docs = self.retrieve_relevant_documents(query)
            
            if not retrieved_docs:
                return {
                    'answer': """I couldn't find relevant information in the BNS documents for your query. 
                             This could mean:
                             1. The topic might not be covered in the loaded BNS documents
                             2. The query might need to be rephrased
                             3. The system might need additional legal documents
                             
                             Please try rephrasing your question or consult with a legal professional.""",
                    'confidence': 0.1,
                    'success': True,
                    'retrieved_docs': 0,
                    'query_type': query_type,
                    'sections_cited': []
                }
            
            # Build context
            context = self.build_context(retrieved_docs)
            
            # Generate response
            response_data = self.generate_response(query, context, query_type)
            
            # Calculate confidence
            confidence = self.calculate_confidence(retrieved_docs, response_data)
            
            # Compile final response
            final_response = {
                'answer': response_data['answer'],
                'confidence': confidence,
                'success': response_data['success'],
                'retrieved_docs': len(retrieved_docs),
                'query_type': query_type,
                'sections_cited': response_data.get('sections_cited', []),
                'model_used': response_data['model_used'],
                'source_documents': [
                    {
                        'text': doc.get('text', '')[:200] + "..." if len(doc.get('text', '')) > 200 else doc.get('text', ''),
                        'section': doc.get('metadata', {}).get('section_number', ''),
                        'content_type': doc.get('metadata', {}).get('content_type', ''),
                        'relevance_score': doc.get('relevance', 0)
                    }
                    for doc in retrieved_docs[:3]  # Include top 3 sources
                ]
            }
            
            logger.info(f"Processed query successfully. Confidence: {confidence:.2f}")
            return final_response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'answer': "I encountered an error while processing your legal query. Please try again later or consult with a legal professional.",
                'confidence': 0.0,
                'success': False,
                'error': str(e),
                'retrieved_docs': 0,
                'query_type': 'error',
                'sections_cited': []
            }
    
    def get_system_status(self) -> Dict[str, any]:
        """
        Get comprehensive system status for the RAG pipeline.
        
        Returns:
            System status information
        """
        try:
            # Check vector store health
            vector_store_health = self.vector_store.health_check()
            
            # Check OpenAI API
            try:
                test_response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                openai_status = "healthy"
            except Exception as e:
                openai_status = f"error: {str(e)}"
            
            # Get vector store stats
            collection_stats = self.vector_store.get_collection_stats()
            
            return {
                'overall_status': 'healthy' if vector_store_health.get('status') == 'healthy' and openai_status == 'healthy' else 'unhealthy',
                'vector_store': vector_store_health,
                'openai_api': openai_status,
                'collection_stats': collection_stats,
                'config': Config.get_summary(),
                'ready_for_queries': vector_store_health.get('document_count', 0) > 0 and openai_status == 'healthy'
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'ready_for_queries': False
            }
    
    def get_example_queries(self) -> List[Dict[str, str]]:
        """
        Get example queries for different types of legal questions.
        
        Returns:
            List of example queries with categories
        """
        return [
            {
                'category': 'Definitions',
                'query': 'What is the definition of theft under BNS?',
                'description': 'Get clear definitions of legal terms and concepts'
            },
            {
                'category': 'Penalties',
                'query': 'What is the punishment for assault under BNS?',
                'description': 'Learn about specific penalties and punishments'
            },
            {
                'category': 'Procedures',
                'query': 'What is the procedure for filing a complaint?',
                'description': 'Understand legal processes and procedures'
            },
            {
                'category': 'Offences',
                'query': 'What constitutes a criminal breach of trust?',
                'description': 'Learn about different types of criminal offences'
            },
            {
                'category': 'Rights',
                'query': 'What are the rights of an accused person?',
                'description': 'Understand legal rights and protections'
            },
            {
                'category': 'Sections',
                'query': 'Explain Section 103 of BNS',
                'description': 'Get detailed explanations of specific BNS sections'
            }
        ]