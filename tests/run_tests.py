#!/usr/bin/env python3
"""
Test runner for the vector embeddings application.
Runs different types of tests and provides a summary.
"""

import time
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def run_test(test_name, test_function):
    """Run a test and return results."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = test_function()
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ {test_name} completed successfully")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        return {
            "name": test_name,
            "status": "PASSED",
            "duration": duration,
            "result": result
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n❌ {test_name} failed")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"💥 Error: {e}")
        
        return {
            "name": test_name,
            "status": "FAILED",
            "duration": duration,
            "error": str(e)
        }

def run_caching_test():
    """Run the caching functionality test."""
    from tests import test_caching
    test_caching.test_caching()
    return "Cache functionality working"

def run_performance_test():
    """Run the performance test."""
    from tests import test_performance
    test_performance.main()
    return "Performance benchmarks completed"

def run_error_test():
    """Run the error handling test."""
    from tests import test_errors
    test_errors.main()
    return "Error handling tests completed"

def run_manual_tests():
    """Run manual tests that require user interaction."""
    print("\n🎯 Manual Testing Checklist")
    print("=" * 35)
    
    tests = [
        "1. Add a text document and verify it appears in the list",
        "2. Add a PDF document and verify text extraction works",
        "3. Add an image file and verify OCR works (if tesseract installed)",
        "4. Search for similar documents and verify realistic similarity scores",
        "5. Test the chat bot with questions about your documents",
        "6. Use cache management to view cache status",
        "7. Test cache rebuilding functionality",
        "8. Check embedding dimensions for consistency",
        "9. Test with different similarity thresholds",
        "10. Verify error messages for invalid inputs"
    ]
    
    for test in tests:
        print(f"   {test}")
    
    print("\n📝 Instructions:")
    print("   - Run the main application: python src/main.py")
    print("   - Go through each test manually")
    print("   - Note any issues or unexpected behavior")
    print("   - Check that similarity scores are realistic (not 99%+)")
    
    return "Manual tests checklist provided"

def run_search_test():
    """Run the search functionality test."""
    from tests import test_search
    test_search.test_search()
    return "Search functionality working"

def run_syntax_test():
    """Run the syntax check test."""
    from tests import test_syntax
    test_syntax.test_syntax()
    return "Syntax check completed"

def run_quick_smoke_test():
    """Run a quick smoke test to verify basic functionality."""
    print("\n💨 Quick Smoke Test")
    print("=" * 25)
    
    try:
        # Test 1: Import DocumentManager
        from src.main import DocumentManager
        print("✅ DocumentManager imports successfully")
        
        # Test 2: Initialize DocumentManager
        doc_manager = DocumentManager()
        print("✅ DocumentManager initializes successfully")
        
        # Test 3: List documents
        docs = doc_manager.list_documents()
        print(f"✅ Document listing works: {len(docs)} documents found")
        
        # Test 4: Check cache
        cache_size = len(doc_manager.embeddings_cache)
        print(f"✅ Cache loaded: {cache_size} documents in cache")
        
        # Test 5: Basic search (if documents exist)
        if docs:
            results = doc_manager.search_by_query("test", threshold=0.5)
            print(f"✅ Search functionality works: {len(results)} results")
        else:
            print("⚠️  No documents to test search with")
        
        return "All basic functionality working"
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        raise

def main():
    """Run all tests and provide a summary."""
    print("🚀 Vector Embeddings Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run smoke test first
    test_results.append(run_test("Smoke Test", run_quick_smoke_test))
    
    # Run automated tests
    test_results.append(run_test("Caching Test", run_caching_test))
    test_results.append(run_test("Performance Test", run_performance_test))
    test_results.append(run_test("Error Handling Test", run_error_test))
    test_results.append(run_test("Search Test", run_search_test))
    test_results.append(run_test("Syntax Test", run_syntax_test))
    
    # Provide manual test checklist
    test_results.append(run_test("Manual Test Checklist", run_manual_tests))
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Test Summary")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for result in test_results:
        status_icon = "✅" if result["status"] == "PASSED" else "❌"
        print(f"{status_icon} {result['name']}: {result['status']} ({result['duration']:.2f}s)")
        
        if result["status"] == "PASSED":
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your application is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Next Steps:")
    print("   1. Run manual tests to verify user experience")
    print("   2. Add real documents to test with realistic content")
    print("   3. Test with different file types (PDF, images)")
    print("   4. Verify similarity scores are realistic (not 99%+)")
    print("   5. Test the chat bot with real questions")

if __name__ == "__main__":
    main() 