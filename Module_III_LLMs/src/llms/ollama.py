from collections.abc import Generator
from contextlib import contextmanager

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from config import OLLAMA_BASE_URL

@contextmanager
def initialize(name: str, **kwargs) -> Generator[ChatOllama]:
    """Initialize ollama model

    Args:
        name (str): Name of ollama model utilized
        kwargs: Parameters that are passed to OllamLLM constructor. Check documentation for more details: https://reference.langchain.com/python/langchain-ollama/chat_models/ChatOllama.

    Returns:
        OllamaLLM: OllamaLLM model instance
    """
    kwargs["keep_alive"] = -1
    ollama = ChatOllama(
        model=name,
        base_url=OLLAMA_BASE_URL,
        **kwargs
    )
    
    try:
        try:
            ollama.invoke([])
        except Exception:
            pass
        yield ollama
    finally:
        kwargs["keep_alive"] = 0
        ollama = ChatOllama(
            model=name,
            base_url=OLLAMA_BASE_URL,
            **kwargs
        )
    

def execute(model: ChatOllama, prompt: str, system: str = '', input: dict = {}) -> AIMessage:
    """Excute prompt on model 

    Args:
        model (ChatOllama): ChatOllama model where the prompt will be executed 
        prompt (str): Prompt that will be executed on the model
        system (str, optional): System prompt used on role prompting techniques. Defaults to ''.
        input (dict, optional): Variables to replace template on prompt. Defaults to {}.

    Returns:
        AIMessage: _description_
    """
    
    messages = [
        ("user", prompt)
    ]
    
    if system != '':
        messages = [("system", system)] + messages
    
    chat_prompt = ChatPromptTemplate.from_messages(messages)

    chain = chat_prompt | model 

    return chain.invoke(input)