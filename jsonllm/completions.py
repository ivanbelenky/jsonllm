import os
from typing import Dict, Union

import dotenv
from openai import ChatCompletion, Completion
from vertexai.preview.language_models import ChatModel, TextGenerationModel # type: ignore
from anthropic import Anthropic
 
from .utils import no_tokens, OpenAIErrors, AnthropicErrors
from .constants import MAX_TOKENS, DEFAULT_MODEL_KWARGS, OPENAI_MODELS, GOOGLE_MODELS, ANTHROPIC_MODELS, DEFAULT_SYSTEM_PROMPT

try:
    dotenv.load_dotenv()
    anthropic_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
except Exception as e:
    client = None


class _Completion:
    class ClientError(Exception): pass
    class ServerError(Exception): pass

    @staticmethod
    def _anthropic(prompt: str, model: str, **model_kwargs: Dict[str, Union[str, float, int]]) -> str:
        try:
            model_kwargs = model_kwargs or DEFAULT_MODEL_KWARGS[model]
            message = anthropic_client.messages.create(
                model=model or "claude-3-opus-20240229", **model_kwargs,
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            )
            return message.content[0].text
        except AnthropicErrors as e:
            raise _Completion.ServerError(f"Failed to complete prompt: {e}")
        except Exception as e:
            raise _Completion.ClientError(f"Failed to complete prompt: {e}")

    @staticmethod
    def _openai(prompt: str, model: str, system_prompt: str=None, **model_kwargs: Dict[str, Union[str, float, int]]) -> str:
        try:
            model_kwargs = model_kwargs or DEFAULT_MODEL_KWARGS[model]
            if MAX_TOKENS[model] - no_tokens(prompt) < 0:
                raise Exception("Failed to complete prompt, not enough tokens left. Try reducing prompt length.")
            if 'gpt-3.5-turbo' in model:
                system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
                return ChatCompletion.create(
                    model=model, **model_kwargs, 
                    messages=[{'role':'system', 'content': system_prompt}, {'role':'user', 'content':prompt}], 
                ).choices[0].message.content # type: ignore
            elif any([m in model for m in ['ada', 'babbage', 'curie', 'davinci']]):
                return Completion.create(model=model, prompt=prompt, **model_kwargs).choices[0].text # type: ignore
        except OpenAIErrors as e:
            raise _Completion.ServerError(f"Failed to complete prompt: {e}")
        except Exception as e:
            raise _Completion.ClientError(f"Failed to complete prompt: {e}")
        raise ValueError(f"Model {model} not implemented")

    @staticmethod
    def _google(prompt: str, model: str, **model_kwargs: Dict[str, Union[str, float, int]]) -> str:
        '''Usable models (tested) are: chat-bison@001 & †ext-bison@001'''
        try:
            if 'chat' in model:
                return ChatModel.from_pretrained(model).start_chat(examples=[]).send_message(prompt, **model_kwargs).text # type: ignore
            elif 'text' in model:
                return TextGenerationModel.from_pretrained(model).predict(prompt, **model_kwargs).text # type: ignore
        # except GoogleErrors as e: TODO: what error Google is responsible for?
        except Exception as e:
            raise _Completion.ClientError(f"Failed to complete prompt: {e}")
        raise ValueError(f"Model {model} not implemented")

    @staticmethod
    def complete_prompt(prompt: str, model: str, **model_kwargs: Dict[str, Union[str, float, int]]) -> str:
        if model in OPENAI_MODELS: return _Completion._openai(prompt, model=model, **model_kwargs)
        elif model in GOOGLE_MODELS: return _Completion._google(prompt, model=model, **model_kwargs)
        elif model in ANTHROPIC_MODELS: return _Completion._anthropic(prompt, model=model, **model_kwargs)
        else: raise NotImplementedError(f"Completion model {model} not implemented")
