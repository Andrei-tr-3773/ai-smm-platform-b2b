from langchain_openai import ChatOpenAI
from deepeval.models.base_model import DeepEvalBaseLLM

class DeepEvalOpenAI(DeepEvalBaseLLM):
    """DeepEval wrapper for OpenAI model"""
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        return chat_model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        return res.content

    def get_model_name(self):
        return "OpenAI Model"