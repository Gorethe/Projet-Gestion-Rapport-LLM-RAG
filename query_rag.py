import argparse
import psycopg2
from get_embeddings import get_embedding_function
from reset import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
import requests
import json

# Template de prompt simplifié
PROMPT_TEMPLATE = """Contexte: {context}

Question: {question}

Réponse:"""

def connect_to_db():
    """Connexion rapide à PostgreSQL"""
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASS
    )

def query_postgres_fast(query_text, k=5):
    """Recherche rapide avec moins de résultats"""
    embedding_function = get_embedding_function()
    query_embedding = embedding_function.embed_query(query_text)
    
    with connect_to_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT content, metadata->'content' as content_meta, 
                       embedding <-> %s::vector AS distance
                FROM tb_vecteurs
                ORDER BY distance ASC
                LIMIT %s;
            """, (query_embedding, k))
            return cursor.fetchall()

def call_ollama_direct(prompt, model="tinyllama:1.1b", max_tokens=100):
    """Appel direct à l'API Ollama - version optimisée"""
    # 1. Vérifier si Ollama est disponible
    try:
        health_check = requests.get('http://localhost:11434/api/tags', timeout=5)
        if health_check.status_code != 200:
            return " Ollama n'est pas accessible. Lancez 'ollama serve' d'abord."
    except requests.RequestException:
        return " Ollama n'est pas lancé. Exécutez 'ollama serve' dans un autre terminal."
    
    # 2. Prompt plus court pour réponse plus rapide
    short_prompt = f"Question: {prompt.split('Question: ')[-1]}\nRéponse courte:"
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': short_prompt,
                'stream': False,
                'options': {
                    'num_predict': max_tokens,  # Response plus courte
                    'temperature': 0.3,  # Moins créatif = plus rapide
                    'top_p': 0.8,
                    'num_ctx': 1024,  # Context plus petit
                    'repeat_penalty': 1.1
                }
            },
            timeout=60  # Timeout plus long
        )
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            return f" Erreur API Ollama: {response.status_code}"
    except requests.Timeout:
        return " Timeout - Ollama prend trop de temps. Essayez un modèle plus petit."
    except requests.RequestException as e:
        return f" Erreur Ollama: {e}"

def query_rag_light(query_text: str, max_results=3):
    """Version allégée de la requête RAG"""
    print(f" Recherche: {query_text}")
    
    # Récupération rapide des résultats
    results = query_postgres_fast(query_text, k=max_results)
    
    if not results:
        return "Aucun résultat trouvé dans la base de données."
    
    # Afficher d'abord les résultats de recherche
    print(f" {len(results)} documents trouvés:")
    for i, (content, _, distance) in enumerate(results[:max_results]):
        preview = content[:100] + "..." if len(content) > 100 else content
        print(f"  {i+1}. (score: {distance:.3f}) {preview}")
    
    # Contexte plus court - seulement les 2 meilleurs résultats
    context_parts = []
    for i, (content, _, distance) in enumerate(results[:2]):  # Seulement 2 résultats
        short_content = content[:150] + "..." if len(content) > 150 else content
        context_parts.append(short_content)
    
    context_text = "\n---\n".join(context_parts)
    
    # Prompt encore plus court
    prompt = f"Contexte:\n{context_text}\n\nQuestion: {query_text}\nRéponse:"
    
    print("\n Génération de la réponse...")
    
    # Appel rapide au LLM
    response_text = call_ollama_direct(prompt, max_tokens=80)  # Réponse très courte
    
    # Affichage
    print(f"\n Réponse:\n{response_text}")
    
    return response_text

def main():
    parser = argparse.ArgumentParser(description="RAG Query - Version Légère")
    parser.add_argument("query_text", type=str, help="Votre question")
    parser.add_argument("--results", type=int, default=3, help="Nombre de résultats (défaut: 3)")
    
    args = parser.parse_args()
    
    try:
        query_rag_light(args.query_text, max_results=args.results)
    except KeyboardInterrupt:
        print("\n Annulé par l'utilisateur")
    except Exception as e:
        print(f" Erreur: {e}")

if __name__ == "__main__":
    main()