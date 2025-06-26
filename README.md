# Projet-Gestion-Rapport-LLM-RAG

This project implements a RAG (Retrieval-Augmented Generation) pipeline using Ollama 
for embeddings and language models, with PostgreSQL as the vector database.

#Features
PDF document loading and processing

Document chunking

Embedding generation with Ollama

Storage in PostgreSQL

RAG query with vector search and answer generation

#Prerequisites
Python 3.x

PostgreSQL with pgvector extension

Ollama installed and running (ollama serve)

Ollama model nomic-embed-text for embeddings

Ollama model tinyllama:1.1b (or other) for generation

#Installation
Clone the repository:

#Install dependencies:

pip install -r requirements.txt

#File Structure
file_mover.py: Handles processed file management

get_embeddings.py: Ollama embeddings configuration

processus.py: Document processing pipeline

query.py: RAG query interface

reset.py: Database reset utility

#Usage
1. Document Processing
Place your PDF files in the data/ directory then run:
python processus.py
To reset the database before processing: python processus.py --reset
2. Querying the System
To ask a question to the RAG system:

python query.py "Your question here")

3. Reset
To completely clear the database:

python reset.py
Configuration
Main parameters are configured in reset.py:

PostgreSQL connection settings

Default embedding model (nomic-embed-text)

In query.py, you can modify:

Generation model (tinyllama:1.1b by default)


Directories
data/: Contains PDFs to process

processed_data/: Stores PDFs after processing

Notes
Ensure Ollama is running (ollama serve)

For better performance, use a GPU for embeddings and generation

The system is optimized for fast responses with some quality trade-offs


