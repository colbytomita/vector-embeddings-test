#!/usr/bin/env python3
"""Test script to check syntax of main.py."""

def test_syntax():
    """Test the syntax of main.py."""
    try:
        import src.main
        print("✅ Syntax check passed - main.py imports successfully!")
        return "Syntax check completed successfully"
    except SyntaxError as e:
        print(f"❌ Syntax error in main.py: {e}")
        raise
    except Exception as e:
        print(f"❌ Other error: {e}")
        raise

if __name__ == "__main__":
    test_syntax() 