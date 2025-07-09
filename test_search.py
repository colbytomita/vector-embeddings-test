#!/usr/bin/env python3
"""Test script to check search functionality."""

from src.main import DocumentManager

def test_search():
    print("🔍 Testing Search Functionality")
    print("=" * 40)
    
    # Initialize DocumentManager
    dm = DocumentManager()
    print(f"✅ Loaded {len(dm.embeddings_cache)} documents from cache")
    
    # Test queries
    test_queries = [
        "agile development",
        "development methodologies", 
        "scrum methodology",
        "software development",
        "waterfall model"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 30)
        
        # Test with different thresholds
        for threshold in [0.1, 0.3, 0.5, 0.7]:
            try:
                results = dm.search_by_query(query, threshold=threshold)
                print(f"  Threshold {threshold}: {len(results)} results")
                
                if results:
                    for i, result in enumerate(results[:3], 1):
                        print(f"    {i}. {result['filename']} (similarity: {result['similarity']:.2%})")
                        print(f"       Content: {result['content'][:100]}...")
                else:
                    print(f"    No results found with threshold {threshold}")
                    
            except Exception as e:
                print(f"    ❌ Error with threshold {threshold}: {e}")
        
        print()

if __name__ == "__main__":
    test_search() 