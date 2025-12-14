import os
from langchain_openai import ChatOpenAI
from openai import OpenAI

def get_azure_chat_openai_model():
    """Get OpenAI chat model (renamed for compatibility, but uses standard OpenAI)"""
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise ValueError("API key not found. Please set the AZURE_OPENAI_API_KEY environment variable.")

    return ChatOpenAI(
        api_key=api_key,
        model=model_name,
        temperature=0.0
    )

def get_azure_embedding_openai_model():
    """Get OpenAI embedding model (renamed for compatibility, but uses standard OpenAI)"""
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    embedding_model_name = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    if not api_key:
        raise ValueError("API key not found. Please set the AZURE_OPENAI_API_KEY environment variable.")

    return OpenAI(api_key=api_key), embedding_model_name

def generate_embeddings(text, model=None):
    embedding_model, embedding_model_name = model or get_azure_embedding_openai_model()
    response = embedding_model.embeddings.create(input=[text], model=embedding_model_name)
    return response.data[0].embedding