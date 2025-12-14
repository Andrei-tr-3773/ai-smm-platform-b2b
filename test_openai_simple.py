from utils.azure_openai_utils import get_azure_chat_openai_model
from dotenv import load_dotenv

load_dotenv()

print('Testing OpenAI client...')
try:
    model = get_azure_chat_openai_model()
    response = model.invoke('Say hello in one word')
    print(f'Success! Response: {response.content}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
