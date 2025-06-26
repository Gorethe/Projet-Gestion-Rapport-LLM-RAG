from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embeddings import get_embedding_function
from file_mover import move_processed_documents
import psycopg2
from reset import clear_database
from reset import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
import os
import hashlib
import argparse
import json

DATA_PATH = "data"
PROCESSED_PATH = "processed_data"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing Database")
        clear_database()

    documents = load_documents()
    print(f"Nombre de documents chargés: {len(documents)}")

    chunks = split_documents(documents)
    print(f"Nombre de chunks générés: {len(chunks)}")

    add_to_postgresql(chunks)
    move_processed_documents(DATA_PATH, PROCESSED_PATH)

def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)

    for chunk in chunks:
        unique_id = hashlib.sha256(
            (chunk.page_content + chunk.metadata.get("source", "")).encode()
        ).hexdigest()
        chunk.metadata['id'] = unique_id
        chunk.metadata['content'] = chunk.page_content
    return chunks

def add_to_postgresql(chunks: list[Document]):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        embedding_function = get_embedding_function()
        cursor.execute("SELECT metadata->>'id' FROM tb_vecteurs")
        existing_ids = {str(row[0]) for row in cursor.fetchall()}

        for chunk in chunks:
            document_id = str(chunk.metadata.get("id"))
            if document_id in existing_ids:
                print(f"Document avec l'ID {document_id} déjà dans la base.")
                continue

            if not chunk.page_content:
                print(f"Chunk {document_id} a un contenu vide - ignoré")
                continue

            vector = embedding_function.embed_documents([chunk.page_content])[0]
            clean_metadata = json.dumps(chunk.metadata).encode('utf-8', 'ignore').decode('utf-8')
            cursor.execute(
                "INSERT INTO tb_vecteurs (content, metadata, embedding) VALUES (%s, %s, %s::vector)",
                (chunk.page_content, clean_metadata, vector)
            )
            conn.commit()
            print(f"Document ajouté avec l'ID: {document_id}")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erreur lors de l'insertion : {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()