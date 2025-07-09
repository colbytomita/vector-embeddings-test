#!/usr/bin/env python3
"""Debug script to test chat bot response to taxonomy question."""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from main import DocumentManager, ChatBot

def debug_taxonomy_question():
    """Debug the taxonomy question response."""
    print("🔍 Debugging Chat Bot Response")
    print("=" * 40)
    
    # Initialize document manager
    doc_manager = DocumentManager()
    chat_bot = ChatBot(doc_manager)
    
    # Test question
    question = "List all genera and subgenera mentioned under the tribe Unionini."
    
    print(f"Question: {question}")
    print("\nSearching for relevant documents...")
    
    # Test search directly
    relevant_docs = doc_manager.search_by_query(question, threshold=0.3)
    print(f"Found {len(relevant_docs)} relevant documents")
    
    for i, doc in enumerate(relevant_docs, 1):
        print(f"\nDocument {i}: {doc['filename']}")
        print(f"Similarity: {doc['similarity']:.2%}")
        print(f"Content preview: {doc['content'][:1000]}...")
        print(f"Content length: {len(doc['content'])} characters")
        print("-" * 50)
    
    print("\n" + "="*50)
    print("CHAT BOT RESPONSE:")
    print("="*50)
    
    # Get chat bot response
    response = chat_bot.chat(question)
    print(response)

if __name__ == "__main__":
    debug_taxonomy_question() 