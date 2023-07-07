from openai import ChatCompletion, Completion
from vertexai.preview.language_models import ChatModel, TextGenerationModel

from jsonllm.utils import no_tokens, OpenAIErrors
from jsonllm.constants import MAX_TOKENS, DEFAULT_MODEL_KWARGS


class _Completion:
    class ClientError(Exception): pass
    class ServerError(Exception): pass

    @staticmethod
    def _openai(prompt: str, *, model='gpt-3.5-turbo', **model_kwargs):
        try:
            model_kwargs = model_kwargs or DEFAULT_MODEL_KWARGS[model]
            if MAX_TOKENS[model] - no_tokens(prompt) < 0:
                raise Exception(
                    f"Failed to complete prompt, not enough tokens left "
                    f"try reducing prompt length.")
            if 'gpt-3.5-turbo' in model:
                completion = ChatCompletion.create(model=model, messages=[{'role':'user','content':prompt}], **model_kwargs)
                raw_response = completion.choices[0].message.content
            elif any([m in model for m in ['ada', 'babbage', 'curie', 'davinci']]):
                completion = Completion.create(model=model ,prompt=prompt, **model_kwargs)
                raw_response = completion.choices[0].text
            return raw_response
        except OpenAIErrors as e:
            raise _Completion.ServerError(f"Failed to complete prompt: {e}")
        except Exception as e:
            raise _Completion.ClientError(f"Failed to complete prompt: {e}")
    
    @staticmethod
    def _google(prompt: str, *, model='chat-bison@001', **model_kwargs):
        '''Usable models (tested) are: chat-bison@001 & †ext-bison@001'''
        try:
            if 'chat' in model:
                return ChatModel.from_pretrained(model).start_chat(examples=[]).send_message(prompt, **model_kwargs).text
            elif 'text' in model:
                return TextGenerationModel.from_pretrained(model).predict(prompt, **model_kwargs).text
        # except GoogleErrors as e: TODO: what error Google is responsible for?
        except Exception as e:
            raise _Completion.ClientError(f"Failed to complete prompt: {e}")

    @staticmethod
    def complete_prompt(prompt: str, llm: str, model: str, **model_kwargs):
        if llm == 'openai': return _Completion._openai(prompt, model, **model_kwargs)
        elif llm == 'google': return _Completion._google(prompt, model=model, **model_kwargs)
        else: raise NotImplementedError(f"Completion model {llm} not implemented")