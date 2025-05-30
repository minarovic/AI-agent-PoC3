#!/bin/bash
echo "Deploying to LangGraph Platform..."
echo "1. Checking langgraph.json..."
cat langgraph.json
echo "2. Checking required files..."
ls -la src/memory_agent/*.py
echo "3. Ready for deployment!"
echo "Next: Use LangGraph CLI or web interface to deploy"
