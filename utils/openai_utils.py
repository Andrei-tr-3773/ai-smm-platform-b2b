import os
from langchain_openai import ChatOpenAI
from openai import OpenAI

def get_openai_model():
    """Get OpenAI chat model"""
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

    return ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0.0
    )

def get_openai_embedding_model():
    """Get OpenAI embedding model"""
    api_key = os.getenv("OPENAI_API_KEY")
    embedding_model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    if not api_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

    return OpenAI(api_key=api_key), embedding_model_name

def get_openai_client():
    """Get OpenAI client for direct API calls"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

    return OpenAI(api_key=api_key)

def generate_embeddings(text, model=None):
    """Generate embeddings using OpenAI"""
    embedding_model, embedding_model_name = model or get_openai_embedding_model()
    response = embedding_model.embeddings.create(input=[text], model=embedding_model_name)
    return response.data[0].embedding