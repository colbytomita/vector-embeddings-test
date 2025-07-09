# Vector Embeddings Application Tests

This folder contains the testing suite for the vector embeddings application.

## 📁 Test Files

- **`test_caching.py`** - Tests the hybrid caching functionality
- **`test_performance.py`** - Performance benchmarks and scalability tests
- **`test_errors.py`** - Error handling and edge case tests
- **`run_tests.py`** - Main test runner that executes all tests
- **`testing_plan.md`** - Comprehensive testing strategy and scenarios

## 🚀 How to Run Tests

### From Project Root:

```bash
# Run all tests
python run_tests.py

# Run individual tests
python tests/test_caching.py
python tests/test_performance.py
python tests/test_errors.py
```

### From Tests Folder:

```bash
cd tests
python run_tests.py
```

## 🧪 Test Categories

### 1. **Caching Tests** (`test_caching.py`)

- Cache building and loading
- Cache validation
- Cache invalidation
- Memory usage monitoring

### 2. **Performance Tests** (`test_performance.py`)

- Search speed benchmarks
- Cache vs file-based performance comparison
- Scalability testing with different document counts
- Memory usage analysis

### 3. **Error Handling Tests** (`test_errors.py`)

- Corrupted file handling
- Edge cases and boundary conditions
- File permission scenarios
- Memory stress testing

## 📊 Expected Results

### Performance Benchmarks:

- **Document addition:** < 30 seconds
- **Search with cache:** < 1 second
- **Cache building:** < 10 seconds for 100 documents
- **Memory usage:** < 100MB for 1000 documents

### Quality Checks:

- **All tests pass** without errors
- **Realistic similarity scores** (not 99%+)
- **Proper error handling** for edge cases
- **Cache functionality** working correctly

## 🔧 Dependencies

Make sure you have all required packages installed:

```bash
pip install -r requirements.txt
```

Required packages for testing:

- `psutil` - For memory monitoring
- `numpy` - For numerical operations
- All other packages from main requirements.txt

## 📝 Manual Testing

After running automated tests, perform these manual tests:

1. **Add real documents** to test realistic similarity scores
2. **Test different file types** (PDF, images, text)
3. **Verify cache management** works correctly
4. **Check embedding dimensions** are consistent
5. **Test chat bot** with real questions

## 🐛 Troubleshooting

### Common Issues:

1. **Import errors** - Make sure you're running from the project root
2. **Memory errors** - Close other applications to free up memory
3. **Performance issues** - Check if cache is working properly
4. **Similarity scores too high** - Use real documents instead of test data

### Debug Mode:

To run tests with more verbose output, modify the test files to include debug prints.

## 📈 Performance Monitoring

The tests include performance monitoring for:

- **Search response times**
- **Memory usage**
- **Cache hit rates**
- **Scalability metrics**

Use these metrics to ensure your application performs well as you add more documents.
