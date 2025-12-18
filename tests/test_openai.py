import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('AZURE_OPENAI_API_KEY')
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
model = os.getenv('AZURE_OPENAI_MODEL')

print(f'API Key: {api_key[:20]}...' if api_key else 'API Key: NOT SET')
print(f'Endpoint: {endpoint}')
print(f'Model: {model}')

try:
    client = OpenAI(api_key=api_key, base_url=endpoint)
    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': 'Say hello in one word'}],
        max_tokens=10
    )
    print(f'\nTest successful! Response: {response.choices[0].message.content}')
except Exception as e:
    print(f'\nError: {e}')
