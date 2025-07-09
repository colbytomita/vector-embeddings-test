#!/usr/bin/env python3
"""Debug script specifically for taxonomy document content."""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

from main import DocumentManager, ChatBot

def debug_taxonomy_content():
    """Debug the taxonomy document content specifically."""
    print("🔍 Debugging Taxonomy Document Content")
    print("=" * 50)
    
    # Initialize document manager
    doc_manager = DocumentManager()
    
    # Get the taxonomy document specifically
    taxonomy_doc = doc_manager.get_document("document1_taxonomy")
    
    if taxonomy_doc:
        print("📄 Taxonomy Document Found:")
        print(f"Filename: {taxonomy_doc.get('original_filename', 'Unknown')}")
        print(f"Content length: {len(taxonomy_doc.get('content', ''))} characters")
        print("\n" + "="*50)
        print("FULL CONTENT:")
        print("="*50)
        print(taxonomy_doc.get('content', ''))
        print("="*50)
        
        # Test search for Unionini
        print("\n🔍 Testing search for 'Unionini':")
        results = doc_manager.search_by_query("Unionini", threshold=0.3)
        print(f"Found {len(results)} results")
        
        if results:
            top_result = results[0]
            print(f"\nTop result: {top_result['filename']}")
            print(f"Similarity: {top_result['similarity']:.2%}")
            print(f"Content preview: {top_result['content'][:1000]}...")
        
        # Test chat bot response
        print("\n" + "="*50)
        print("CHAT BOT TEST:")
        print("="*50)
        
        chat_bot = ChatBot(doc_manager)
        question = "List all genera and subgenera mentioned under the tribe Unionini."
        response = chat_bot.chat(question)
        print(response)
        
    else:
        print("❌ Taxonomy document not found!")

if __name__ == "__main__":
    debug_taxonomy_content() 