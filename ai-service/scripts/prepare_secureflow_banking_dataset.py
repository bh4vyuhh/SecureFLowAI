#!/usr/bin/env python3
"""
SecureFlow AI - Production Banking Data Loss Prevention (DLP) Dataset Pipeline
================================================================================
Proxy runner for prepare_secureflow_banking_dataset.py located at workspace root.
"""
import os
import sys

# Ensure parent directory is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from prepare_secureflow_banking_dataset import main

if __name__ == "__main__":
    main()
