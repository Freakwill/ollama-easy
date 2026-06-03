#!/usr/bin/env python3

import ollama
from ollama import Client

from . import ChatMixin

from .secret import api_key

default_description = 'You are a very intelligent agent'

cloude_models = ['deepseek-v3.1:671b-cloud', 'gpt-oss:120b', 'gpt-oss:20b', 'ministral-3:8b-cloud', 'glm-5:cloud',
'kimi-k2.5:cloud', 'qwen3-coder-next:cloud', 'rnj-1:8b-cloud', 'minimax-m2.1:cloud']


class ModelNotFoundError(Exception):
    """
    Do not find the model locally
    """
    
    def __init__(self, model):
        self.model = model
        super().__init__(f"Model `{self.model}` is not found in locally!")


class OllamaChat(ChatMixin, Client):
    """see https://github.com/ollama/ollama-python
    
    Attributes:
        chat_params (dict): parameters in chat method
        description (str): description of the assistant, system prompt
        model (str): the name of the model
        name (str): the name of the assistant

    Usage:
        .attr value: set the attribute `attr` to be the value
        :arg value: set the argument `arg` in chat method (i.e. `chat_params`) to be the value
        !cmd *args: run command `cmd(obj, *args)`
    """

    default_model = 'gpt-oss:20b'
    default_description = """
    As a very intelligent agent, answer questions concisely and directly, without focusing too much on the "general-specific-general" structure — just give the answer directly.
    When writing code, usually just provide the code (comments in the code are fine).**
    """
    def __init__(self, description=None, history=[], name='Assistant', model='gpt-oss:120b', api_key=api_key, *args, **kwargs):
        if api_key:
            super().__init__(host='https://ollama.com',
                headers={'Authorization': 'Bearer ' + api_key}, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
            if any(self.model==m.model for m in ollama.list().models):
                raise ModelNotFoundError(self.model)
        self._history = history
        self.description = description or self.__class__.default_description
        self.name = name
        self.model = model
        self.chat_params = {}

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, m):
        for m_ in cloude_models:
            if m_.startswith(m):
                self._model = m
        else:
            if ':' not in m:
                m += ':latest'
            self._model = m

    def _reply(self, messages, max_retries=10):
        """Wrapper of `chat.completions.create` method of LLM
        The reply method of the AI chat assistant
        as a mapping message --> response

        Args:
            message: the prompt object inputed by the user
            max_retries (int, optional): the number of times to get response
        """

        try:
            response = self.chat(
                model=self.model,
                messages = messages,
                **self.chat_params)
            return response.message.content
        except Exception as e:
            print(f"💻System: An error occurred after {max_retries} attempts: {e}")

    def __enter__(self, *args, **kwargs):
        import sh
        sh.brew.services.start.ollama()
        return self

    def __exit__(self, *args, **kwargs):
        import sh
        sh.brew.services.stop.ollama()


class LocalOllamaChat(OllamaChat):
    """Run ollama locally
    """

    default_model = 'gemma3'
    
    def __init__(self, model='gemma3', *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)
    
    def init(self, *args, **kwargs):        
        if any(self.model==m.model for m in ollama.list().models):
            raise ModelNotFoundError(self.model)
        super().init(*args, **kwargs)

