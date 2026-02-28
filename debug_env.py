import sys
import os
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"Sys Path: {sys.path}")
try:
    import flask
    print(f"flask version: {flask.__version__}")
    print(f"flask file: {flask.__file__}")
except ImportError as e:
    print(f"flask import failed: {e}")

try:
    import deep_translator
    print(f"deep_translator version: {deep_translator.__version__}")
    print(f"deep_translator file: {deep_translator.__file__}")
except ImportError as e:
    print(f"deep_translator import failed: {e}")
