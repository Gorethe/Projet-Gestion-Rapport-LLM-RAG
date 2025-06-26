from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings


def get_embedding_function():  
    return OllamaEmbeddings(  
        model="nomic-embed-text",  
        base_url="http://localhost:11434"  # URL d'Ollama  
    )  



# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_ollama import OllamaEmbeddings

# def get_embedding_function(): 

#     embeddings = OllamaEmbeddings(model="nomic-embed-text", temperature=0) 
#     return embeddings
