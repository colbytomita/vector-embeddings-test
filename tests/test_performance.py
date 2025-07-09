#!/usr/bin/env python3
"""
Performance testing script for the vector embeddings application.
Tests cache performance, search speed, and memory usage.
"""

import time
import json
import psutil
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def measure_memory_usage():
    """Measure current memory usage."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def create_test_documents(num_docs=10):
    """Create test documents with realistic content."""
    embeddings_dir = Path("embeddings")
    embeddings_dir.mkdir(exist_ok=True)
    
    # Realistic document contents
    documents = [
        {
            "title": "Machine Learning Basics",
            "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It involves algorithms that can identify patterns in data and make predictions or decisions based on that data."
        },
        {
            "title": "Neural Networks Introduction",
            "content": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes called neurons that process information and can learn to recognize patterns, classify data, and make predictions."
        },
        {
            "title": "Python Programming Guide",
            "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in data science, web development, automation, and artificial intelligence applications."
        },
        {
            "title": "Data Science Fundamentals",
            "content": "Data science combines statistics, computer science, and domain expertise to extract insights from data. It involves data collection, cleaning, analysis, visualization, and machine learning techniques."
        },
        {
            "title": "Web Development Basics",
            "content": "Web development involves creating websites and web applications. It includes frontend development (HTML, CSS, JavaScript) and backend development (server-side programming, databases)."
        },
        {
            "title": "Database Management Systems",
            "content": "Database management systems are software systems designed to store, retrieve, and manage data efficiently. They provide data integrity, security, and concurrent access capabilities."
        },
        {
            "title": "Cloud Computing Overview",
            "content": "Cloud computing provides on-demand access to computing resources over the internet. It includes services like infrastructure as a service (IaaS), platform as a service (PaaS), and software as a service (SaaS)."
        },
        {
            "title": "Cybersecurity Principles",
            "content": "Cybersecurity involves protecting computer systems, networks, and data from digital attacks. It includes practices like encryption, authentication, access control, and security monitoring."
        },
        {
            "title": "Software Engineering Practices",
            "content": "Software engineering applies engineering principles to software development. It includes requirements analysis, design, implementation, testing, deployment, and maintenance phases."
        },
        {
            "title": "Artificial Intelligence Applications",
            "content": "Artificial intelligence encompasses technologies that enable machines to perform tasks that typically require human intelligence. Applications include natural language processing, computer vision, robotics, and expert systems."
        }
    ]
    
    # Create embeddings (mock 1536-dimensional vectors)
    for i, doc in enumerate(documents[:num_docs]):
        # Create unique embedding for each document
        embedding = [0.1 + (i * 0.1) + (j * 0.001) for j in range(1536)]
        
        doc_data = {
            "original_filename": f"{doc['title'].lower().replace(' ', '_')}.txt",
            "original_path": f"knowledge_base/{doc['title'].lower().replace(' ', '_')}.txt",
            "file_type": ".txt",
            "content": doc['content'],
            "embedding": embedding,
            "added_date": datetime.now().isoformat()
        }
        
        doc_id = f"test_doc_{i+1}"
        embedding_path = embeddings_dir / f"{doc_id}.json"
        with open(embedding_path, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=2)
    
    print(f"✅ Created {num_docs} test documents")

def test_cache_performance():
    """Test cache performance vs file-based search."""
    print("\n🧪 Performance Testing")
    print("=" * 40)
    
    # Import the DocumentManager
    from src.main import DocumentManager
    
    # Initialize document manager
    print("📊 Initializing DocumentManager...")
    start_time = time.time()
    doc_manager = DocumentManager()
    init_time = time.time() - start_time
    print(f"✅ Initialization time: {init_time:.2f} seconds")
    
    # Test search performance
    test_queries = [
        "machine learning",
        "neural networks", 
        "python programming",
        "data science",
        "web development"
    ]
    
    print(f"\n🔍 Testing search performance with {len(test_queries)} queries...")
    
    total_search_time = 0
    for i, query in enumerate(test_queries, 1):
        print(f"  Query {i}: '{query}'")
        
        start_time = time.time()
        results = doc_manager.search_by_query(query, threshold=0.5)
        search_time = time.time() - start_time
        total_search_time += search_time
        
        print(f"    Results: {len(results)} documents")
        print(f"    Time: {search_time:.3f} seconds")
        
        if results:
            top_result = results[0]
            print(f"    Top match: {top_result['filename']} ({top_result['similarity']:.1%})")
    
    avg_search_time = total_search_time / len(test_queries)
    print(f"\n📈 Average search time: {avg_search_time:.3f} seconds")
    
    # Memory usage
    memory_usage = measure_memory_usage()
    print(f"💾 Memory usage: {memory_usage:.1f} MB")
    
    return {
        "init_time": init_time,
        "avg_search_time": avg_search_time,
        "memory_usage": memory_usage,
        "cache_size": len(doc_manager.embeddings_cache)
    }

def test_cache_vs_file_search():
    """Compare cache performance vs file-based search."""
    print("\n⚡ Cache vs File Search Comparison")
    print("=" * 45)
    
    from src.main import DocumentManager
    
    # Test with cache
    print("🔍 Testing with cache...")
    doc_manager = DocumentManager()
    
    start_time = time.time()
    results_cached = doc_manager.search_by_query("machine learning", threshold=0.5)
    cache_time = time.time() - start_time
    
    # Test without cache (simulate by clearing cache)
    print("📁 Testing without cache (simulated)...")
    original_cache = doc_manager.embeddings_cache.copy()
    doc_manager.embeddings_cache = {}
    
    start_time = time.time()
    # This would normally read from files, but we'll simulate it
    results_uncached = doc_manager.search_by_query("machine learning", threshold=0.5)
    uncached_time = time.time() - start_time
    
    # Restore cache
    doc_manager.embeddings_cache = original_cache
    
    print(f"\n📊 Performance Comparison:")
    print(f"  With cache: {cache_time:.3f} seconds")
    print(f"  Without cache: {uncached_time:.3f} seconds")
    
    if uncached_time > 0:
        speedup = uncached_time / cache_time
        print(f"  Speedup: {speedup:.1f}x faster with cache")
    
    return {
        "cache_time": cache_time,
        "uncached_time": uncached_time
    }

def test_scalability(num_docs_list=[5, 10, 20, 50]):
    """Test performance with different numbers of documents."""
    print("\n📈 Scalability Testing")
    print("=" * 30)
    
    results = {}
    
    for num_docs in num_docs_list:
        print(f"\n📊 Testing with {num_docs} documents...")
        
        # Create test documents
        create_test_documents(num_docs)
        
        # Test performance
        from src.main import DocumentManager
        
        start_time = time.time()
        doc_manager = DocumentManager()
        init_time = time.time() - start_time
        
        start_time = time.time()
        results_search = doc_manager.search_by_query("machine learning", threshold=0.5)
        search_time = time.time() - start_time
        
        memory_usage = measure_memory_usage()
        
        results[num_docs] = {
            "init_time": init_time,
            "search_time": search_time,
            "memory_usage": memory_usage,
            "results_count": len(results_search)
        }
        
        print(f"  Init time: {init_time:.3f}s")
        print(f"  Search time: {search_time:.3f}s")
        print(f"  Memory: {memory_usage:.1f}MB")
        print(f"  Results: {len(results_search)}")
    
    return results

def main():
    """Run all performance tests."""
    print("🚀 Vector Embeddings Performance Testing")
    print("=" * 50)
    
    # Create test documents
    print("📝 Creating test documents...")
    create_test_documents(10)
    
    # Run performance tests
    perf_results = test_cache_performance()
    
    # Run cache comparison
    cache_results = test_cache_vs_file_search()
    
    # Run scalability tests
    scalability_results = test_scalability([5, 10, 20])
    
    # Summary
    print("\n📋 Performance Summary")
    print("=" * 25)
    print(f"Cache size: {perf_results['cache_size']} documents")
    print(f"Average search time: {perf_results['avg_search_time']:.3f}s")
    print(f"Memory usage: {perf_results['memory_usage']:.1f}MB")
    
    if 'speedup' in cache_results:
        print(f"Cache speedup: {cache_results['speedup']:.1f}x")
    
    print("\n✅ Performance testing completed!")

if __name__ == "__main__":
    main() 