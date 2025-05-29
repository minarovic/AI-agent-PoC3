#!/bin/bash
# Simple script to run LangGraph Platform locally for development

# Export environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Warning: .env file not found. Make sure to set environment variables manually."
fi

# Run LangGraph development server
echo "Starting LangGraph development server..."
langgraph dev

# Instructions for accessing the UI
echo -e "\nLangGraph development server is running."
echo "Access the API at: http://127.0.0.1:2024"
echo "Access LangGraph Studio UI at: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
