#!/bin/bash

# Set PYTHONPATH to include our source directory
export PYTHONPATH=/Users/marekminarovic/AI-agent-Ntier/src:$PYTHONPATH

# Install required dependencies
pip install -r requirements.txt

# Run the verification test
echo "Running analyzer sync verification test..."
python test_analyzer_sync.py
