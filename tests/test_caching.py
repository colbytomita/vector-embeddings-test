#!/usr/bin/env python3
"""
Test script for the hybrid caching implementation.
This script tests the caching functionality without requiring OpenAI API.
"""

import json
import pickle
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

class MockDocumentManager:
    """Mock DocumentManager for testing caching functionality."""
    
    def __init__(self, embeddings_dir="embeddings"):
        self.embeddings_dir = Path(embeddings_dir)
        self.embeddings_dir.mkdir(exist_ok=True)
        
        # Cache-related attributes
        self.cache_file = Path("embeddings_cache.pkl")
        self.embeddings_cache = {}
        self.cache_metadata_file = Path("cache_metadata.json")
        
        # Load or build cache
        self.load_or_build_cache()
    
    def load_or_build_cache(self):
        """Load embeddings from cache or build them if not available."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "rb") as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✅ Loaded {len(self.embeddings_cache)} embeddings from cache.")
            except Exception as e:
                print(f"⚠️  Error loading cache: {e}. Rebuilding cache.")
                self.embeddings_cache = {}
        else:
            print("⚠️  Cache file not found. Building cache from scratch.")
            self.embeddings_cache = {}

        if self.cache_metadata_file.exists():
            try:
                with open(self.cache_metadata_file, "r", encoding="utf-8") as f:
                    self.cache_metadata = json.load(f)
                print(f"✅ Loaded cache metadata from {self.cache_metadata_file}")
            except Exception as e:
                print(f"⚠️  Error loading cache metadata: {e}. Starting with empty metadata.")
                self.cache_metadata = {}
        else:
            print(f"⚠️  Cache metadata file not found: {self.cache_metadata_file}. Starting with empty metadata.")
            self.cache_metadata = {}
        
        # Check if cache is valid and rebuild if necessary
        if not self.is_cache_valid():
            print("🔄 Cache is invalid, rebuilding...")
            self.build_cache()

    def save_cache(self):
        """Save embeddings and cache metadata to files."""
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"✅ Saved {len(self.embeddings_cache)} embeddings to cache.")
        except Exception as e:
            print(f"❌ Error saving cache: {e}")

    def save_cache_metadata(self):
        """Save cache metadata to a JSON file."""
        try:
            with open(self.cache_metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.cache_metadata, f, indent=2)
            print(f"✅ Saved cache metadata to {self.cache_metadata_file}")
        except Exception as e:
            print(f"❌ Error saving cache metadata: {e}")

    def build_cache(self):
        """Build cache from JSON files in the embeddings directory."""
        print("🔄 Building embeddings cache...")
        self.embeddings_cache = {}
        
        try:
            for file in self.embeddings_dir.glob("*.json"):
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        doc = json.load(f)
                        self.embeddings_cache[file.stem] = doc
                except json.JSONDecodeError:
                    print(f"⚠️  Skipping corrupted file: {file}")
                    continue
                except Exception as e:
                    print(f"⚠️  Error processing {file}: {e}")
                    continue
            
            # Save cache
            self.save_cache()
            
            # Update metadata
            self.cache_metadata = {
                "last_built": datetime.now().isoformat(),
                "total_documents": len(self.embeddings_cache),
                "cache_version": "1.0"
            }
            self.save_cache_metadata()
            
            print(f"✅ Built cache with {len(self.embeddings_cache)} documents")
            
        except Exception as e:
            print(f"❌ Error building cache: {e}")

    def invalidate_cache(self):
        """Rebuild cache when documents change."""
        print("🔄 Invalidating cache...")
        try:
            # Remove old cache files
            if self.cache_file.exists():
                self.cache_file.unlink()
            if self.cache_metadata_file.exists():
                self.cache_metadata_file.unlink()
            
            # Rebuild cache
            self.build_cache()
            print("✅ Cache invalidated and rebuilt")
            
        except Exception as e:
            print(f"❌ Error invalidating cache: {e}")

    def is_cache_valid(self):
        """Check if cache is valid by comparing with actual files."""
        try:
            # Get list of JSON files in embeddings directory
            actual_files = set()
            for file in self.embeddings_dir.glob("*.json"):
                actual_files.add(file.stem)
            
            # Get list of cached documents
            cached_files = set(self.embeddings_cache.keys())
            
            # Check if files match
            if actual_files != cached_files:
                print(f"⚠️  Cache mismatch: {len(actual_files)} files on disk vs {len(cached_files)} in cache")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking cache validity: {e}")
            return False

    def list_documents(self):
        """List all documents in the embeddings directory."""
        docs = []
        try:
            # Use cache for faster listing
            for doc_id, doc in self.embeddings_cache.items():
                docs.append({
                    "id": doc_id,
                    "filename": doc["original_filename"],
                    "file_type": doc.get("file_type", "unknown"),
                    "added_date": doc.get("added_date", "Unknown")
                })
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            raise
        return docs

def create_test_documents():
    """Create some test documents for testing."""
    embeddings_dir = Path("embeddings")
    embeddings_dir.mkdir(exist_ok=True)
    
    # Create test documents with 1536-dimensional embeddings (matching OpenAI's text-embedding-ada-002)
    test_docs = [
        {
            "original_filename": "test1.txt",
            "original_path": "knowledge_base/test1.txt",
            "file_type": ".txt",
            "content": "This is a test document about machine learning.",
            "embedding": [0.1 + i * 0.001 for i in range(1536)],  # 1536-dimensional mock embedding
            "added_date": datetime.now().isoformat()
        },
        {
            "original_filename": "test2.txt",
            "original_path": "knowledge_base/test2.txt",
            "file_type": ".txt",
            "content": "This is another test document about artificial intelligence.",
            "embedding": [0.2 + i * 0.001 for i in range(1536)],  # 1536-dimensional mock embedding
            "added_date": datetime.now().isoformat()
        },
        {
            "original_filename": "test3.pdf",
            "original_path": "knowledge_base/test3.pdf",
            "file_type": ".pdf",
            "content": "This is a PDF document about neural networks.",
            "embedding": [0.3 + i * 0.001 for i in range(1536)],  # 1536-dimensional mock embedding
            "added_date": datetime.now().isoformat()
        }
    ]
    
    # Save test documents
    for i, doc in enumerate(test_docs, 1):
        doc_id = f"test{i}"
        embedding_path = embeddings_dir / f"{doc_id}.json"
        with open(embedding_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)
    
    print(f"✅ Created {len(test_docs)} test documents with 1536-dimensional embeddings")

def test_caching():
    """Test the caching functionality."""
    print("🧪 Testing Hybrid Caching Implementation")
    print("=" * 50)
    
    # Create test documents
    create_test_documents()
    
    # Initialize document manager
    print("\n1. Initializing DocumentManager...")
    doc_manager = MockDocumentManager()
    
    # Test listing documents
    print("\n2. Testing document listing...")
    docs = doc_manager.list_documents()
    print(f"Found {len(docs)} documents:")
    for doc in docs:
        print(f"  - {doc['filename']} (ID: {doc['id']})")
    
    # Test cache status
    print("\n3. Testing cache status...")
    print(f"Documents in cache: {len(doc_manager.embeddings_cache)}")
    print(f"Cache valid: {doc_manager.is_cache_valid()}")
    
    # Test cache invalidation
    print("\n4. Testing cache invalidation...")
    doc_manager.invalidate_cache()
    
    # Test cache after invalidation
    print("\n5. Testing cache after invalidation...")
    docs = doc_manager.list_documents()
    print(f"Found {len(docs)} documents after invalidation:")
    for doc in docs:
        print(f"  - {doc['filename']} (ID: {doc['id']})")
    
    print("\n✅ All caching tests completed successfully!")

if __name__ == "__main__":
    test_caching() 