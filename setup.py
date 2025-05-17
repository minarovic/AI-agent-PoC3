#!/usr/bin/env python
"""Setup script for AI-agent-Ntier package."""

from setuptools import setup, find_packages

setup(
    name="ai-agent-ntier",
    version="0.1.0",
    description="AI agent for LangGraph Platform",
    author="AI-agent-Ntier Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain>=0.1.0",
        "langgraph>=0.2.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.1",
        "requests>=2.31.0",
        "openai>=1.0.0",
        "unidecode>=1.3.6",
        "typing_extensions>=4.7.0"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
)
