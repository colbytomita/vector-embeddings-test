#!/usr/bin/env python3
"""
Simple test runner script for the vector embeddings application.
This script runs the tests from the tests folder.
"""

import sys
from pathlib import Path

# Add the tests directory to the Python path
tests_dir = Path(__file__).parent / "tests"
sys.path.insert(0, str(tests_dir))

if __name__ == "__main__":
    from tests.run_tests import main
    main() 