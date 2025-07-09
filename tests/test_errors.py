#!/usr/bin/env python3
"""
Error testing script for the vector embeddings application.
Tests error handling, edge cases, and robustness.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def create_corrupted_files():
    """Create various corrupted and problematic files for testing."""
    embeddings_dir = Path("embeddings")
    embeddings_dir.mkdir(exist_ok=True)
    
    print("🧪 Creating test files for error scenarios...")
    
    # 1. Corrupted JSON file
    corrupted_json = embeddings_dir / "corrupted.json"
    with open(corrupted_json, "w") as f:
        f.write('{"invalid": json, "missing": quotes}')
    print("✅ Created corrupted JSON file")
    
    # 2. Empty JSON file
    empty_json = embeddings_dir / "empty.json"
    with open(empty_json, "w") as f:
        f.write("")
    print("✅ Created empty JSON file")
    
    # 3. JSON with missing fields
    incomplete_json = embeddings_dir / "incomplete.json"
    incomplete_data = {
        "original_filename": "test.txt",
        "content": "Some content"
        # Missing embedding and other fields
    }
    with open(incomplete_json, "w") as f:
        json.dump(incomplete_data, f)
    print("✅ Created incomplete JSON file")
    
    # 4. JSON with wrong embedding dimensions
    wrong_dim_json = embeddings_dir / "wrong_dim.json"
    wrong_dim_data = {
        "original_filename": "test.txt",
        "content": "Some content",
        "embedding": [0.1, 0.2, 0.3],  # Only 3 dimensions instead of 1536
        "added_date": datetime.now().isoformat()
    }
    with open(wrong_dim_json, "w") as f:
        json.dump(wrong_dim_data, f)
    print("✅ Created JSON with wrong embedding dimensions")
    
    # 5. JSON with non-numeric embedding
    invalid_embedding_json = embeddings_dir / "invalid_embedding.json"
    invalid_embedding_data = {
        "original_filename": "test.txt",
        "content": "Some content",
        "embedding": ["not", "a", "number", "list"],
        "added_date": datetime.now().isoformat()
    }
    with open(invalid_embedding_json, "w") as f:
        json.dump(invalid_embedding_data, f)
    print("✅ Created JSON with invalid embedding data")

def test_error_handling():
    """Test how the application handles various error scenarios."""
    print("\n🔍 Testing Error Handling")
    print("=" * 35)
    
    # Create problematic files
    create_corrupted_files()
    
    # Import and test DocumentManager
    from src.main import DocumentManager
    
    print("\n📊 Testing DocumentManager initialization with corrupted files...")
    
    try:
        doc_manager = DocumentManager()
        print("✅ DocumentManager initialized successfully")
        
        # Test listing documents (should handle corrupted files gracefully)
        print("\n📚 Testing document listing with corrupted files...")
        docs = doc_manager.list_documents()
        print(f"✅ Successfully listed {len(docs)} valid documents")
        
        # Test search functionality
        print("\n🔍 Testing search with corrupted files...")
        results = doc_manager.search_by_query("test", threshold=0.5)
        print(f"✅ Search completed, found {len(results)} results")
        
        # Test cache validation
        print("\n✅ Testing cache validation...")
        is_valid = doc_manager.is_cache_valid()
        print(f"Cache valid: {is_valid}")
        
        # Test embedding dimension checking
        print("\n📏 Testing embedding dimension checking...")
        doc_manager.check_embedding_dimensions()
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("\n🎯 Testing Edge Cases")
    print("=" * 25)
    
    from src.main import DocumentManager
    
    doc_manager = DocumentManager()
    
    # Test 1: Empty search query
    print("\n1. Testing empty search query...")
    try:
        results = doc_manager.search_by_query("", threshold=0.5)
        print(f"   Results: {len(results)} documents")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Very high threshold
    print("\n2. Testing very high threshold (0.95)...")
    try:
        results = doc_manager.search_by_query("machine learning", threshold=0.95)
        print(f"   Results: {len(results)} documents")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Very low threshold
    print("\n3. Testing very low threshold (0.1)...")
    try:
        results = doc_manager.search_by_query("machine learning", threshold=0.1)
        print(f"   Results: {len(results)} documents")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Non-existent document ID
    print("\n4. Testing non-existent document retrieval...")
    try:
        doc = doc_manager.get_document("non_existent_doc")
        print(f"   Retrieved: {doc['original_filename']}")
    except Exception as e:
        print(f"   Expected error: {e}")
    
    # Test 5: Invalid threshold values
    print("\n5. Testing invalid threshold values...")
    invalid_thresholds = [-0.1, 1.5, "not_a_number", None]
    for threshold in invalid_thresholds:
        try:
            results = doc_manager.search_by_query("test", threshold=threshold)
            print(f"   Threshold {threshold}: {len(results)} results")
        except Exception as e:
            print(f"   Threshold {threshold}: Error - {e}")

def test_file_permissions():
    """Test file permission scenarios."""
    print("\n🔐 Testing File Permissions")
    print("=" * 30)
    
    embeddings_dir = Path("embeddings")
    
    # Test 1: Read-only directory
    print("\n1. Testing read-only directory scenario...")
    try:
        # This is a simulation - in real scenarios you'd change permissions
        print("   (Simulated) Would test read-only directory access")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Missing directory
    print("\n2. Testing missing directory scenario...")
    try:
        # Temporarily rename directory with unique name
        temp_name = embeddings_dir.with_name(f"embeddings_temp_{int(time.time())}")
        if embeddings_dir.exists():
            embeddings_dir.rename(temp_name)
        
        # Try to initialize DocumentManager
        from src.main import DocumentManager
        
        doc_manager = DocumentManager()
        print("   ✅ DocumentManager handled missing directory gracefully")
        
        # Restore directory
        if temp_name.exists():
            try:
                temp_name.rename(embeddings_dir)
            except OSError:
                # If rename fails, try to move files back
                print("   ⚠️  Directory restore failed, but DocumentManager worked correctly")
            
    except Exception as e:
        print(f"   Error: {e}")
        # Restore directory if it was renamed
        temp_name = Path("embeddings_temp")
        if temp_name.exists():
            try:
                temp_name.rename(embeddings_dir)
            except OSError:
                print("   ⚠️  Could not restore directory, but test completed")

def test_memory_stress():
    """Test memory usage with large datasets."""
    print("\n💾 Testing Memory Stress")
    print("=" * 25)
    
    import psutil
    import os
    
    def get_memory_usage():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Initial memory usage: {get_memory_usage():.1f} MB")
    
    # Create many test documents
    embeddings_dir = Path("embeddings")
    embeddings_dir.mkdir(exist_ok=True)
    
    print("\n📝 Creating large test dataset...")
    for i in range(50):  # Create 50 test documents
        doc_data = {
            "original_filename": f"stress_test_{i}.txt",
            "content": f"This is stress test document number {i} with some content to make it realistic.",
            "embedding": [0.1 + (i * 0.01) + (j * 0.001) for j in range(1536)],
            "added_date": datetime.now().isoformat()
        }
        
        doc_path = embeddings_dir / f"stress_{i}.json"
        with open(doc_path, "w") as f:
            json.dump(doc_data, f)
    
    print("✅ Created 50 test documents")
    print(f"Memory usage after creating files: {get_memory_usage():.1f} MB")
    
    # Test DocumentManager with large dataset
    print("\n📊 Testing DocumentManager with large dataset...")
    from src.main import DocumentManager
    
    start_memory = get_memory_usage()
    doc_manager = DocumentManager()
    end_memory = get_memory_usage()
    
    print(f"Memory usage after loading cache: {end_memory:.1f} MB")
    print(f"Memory increase: {end_memory - start_memory:.1f} MB")
    print(f"Cache size: {len(doc_manager.embeddings_cache)} documents")

def main():
    """Run all error tests."""
    print("🚨 Vector Embeddings Error Testing")
    print("=" * 40)
    
    # Run error handling tests
    error_success = test_error_handling()
    
    # Run edge case tests
    test_edge_cases()
    
    # Run file permission tests
    test_file_permissions()
    
    # Run memory stress tests
    test_memory_stress()
    
    # Summary
    print("\n📋 Error Testing Summary")
    print("=" * 25)
    if error_success:
        print("✅ All error handling tests passed")
    else:
        print("❌ Some error handling tests failed")
    
    print("\n✅ Error testing completed!")

if __name__ == "__main__":
    main() 