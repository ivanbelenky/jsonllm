import os

import openai
import vertexai
from vertexai.preview.language_models import ChatModel, TextGenerationModel

from jsonllm.utils import no_tokens, OpenAIErrors
from jsonllm.constants import MAX_TOKENS


class Completion:
    '''Completion strategies'''
    class ClientError(Exception):
        pass
    
    class ServerError(Exception):
        pass

    @staticmethod
    def _openai(prompt: str,
                *,
                temperature:float=0.0, 
                top_p:float=1.0,
                top_k:int=0,
                model='gpt-3.5-turbo',
                ):
        #openai.api_key = os.environ.get('OPENAI_API_KEY')
        try:
            tokens_left = MAX_TOKENS[model] - Completion.no_tokens(prompt)
            if tokens_left < 0:
                raise Exception(
                    f"Failed to complete prompt, not enough tokens left "
                    f"try reducing prompt length: {tokens_left}")

            if 'gpt-3.5-turbo' in model:
                completion = openai.ChatCompletion.create(model=model, messages=[{'role':'user','content':prompt}], temperature=temperature)
                raw_response = completion.choices[0].message.content
            elif any([m in model for m in ['ada', 'babbage', 'curie', 'davinci']]):
                completion = openai.Completion.create(model=model ,prompt=prompt, temperature=temperature)
                raw_response = completion.choices[0].text
            return raw_response
        except OpenAIErrors as e:
            raise Completion.ServerError(f"Failed to complete prompt: {e}")
        except Exception as e:
            raise Completion.ClientError(f"Failed to complete prompt: {e}")
    
    @staticmethod
    def _google(prompt: str, temperature: float = 0.0, model='chat-bison@001'):
        '''Usable models (tested) are: 
        - chat-bison@001
        - †ext-bison@001
        '''
        try:
            project_id = "trbs-dev" if os.environ.get('TRUCKBASE_SERVER') in ['DEVELOPMENT', 'LOCAL'] else "trbs-prod"
            location = "us-central1"
            parameters = {
                    "temperature": temperature,
                    "max_output_tokens": 1024,
                    "top_p": 0.8,
                    "top_k": 40,
                }

            vertexai.init(project=project_id, location=location)
            if 'chat' in model:
                chat_model = ChatModel.from_pretrained(model)
                chat = chat_model.start_chat(examples=[])
                response=chat.send_message(prompt, **parameters)
                raw_response = response.text
            elif 'text' in model:
                text_model = TextGenerationModel.from_pretrained(model)
                response = text_model.predict(prompt, **parameters)
                raw_response = response.text

            return raw_response
        except Exception as e:
            raise Completion.ClientError(f"Failed to complete prompt: {e}")

    @staticmethod
    def complete_prompt(prompt: str,
                        llm: str,
                        model: str,
                        *,
                        temperature: float = 0.0,
                        ):
        '''Completes prompt using specified strategy.

        Parameters
        ----------
        prompt : str
            prompt to complete
        llm : str, optional
            language model to use, by default 'openai', one of ['openai', 'llama', 'bard']
        max_tokens : int, optional
            max tokens to use for completion, by default MAX_TOKENS
        temperature : float, optional
            temperature defines the randomness of the predictions, the higher the more random, by default 0.0
            particular care must be taken with different models since they establish different ranges for temperature
            - openai: [0.0, 2.0]
            - llama: NotImplemented
            - bard: NotImplemented
        model : str, optional
            - openai: https://beta.openai.com/docs/api-reference/completions/create
            - llama: NotImplemented
            - bard: NotImplemented

        Returns
        -------
        raw_response: str
            raw response from completion

        Raises
        ------
        ClientError
            raised when completion fails on the client side, e.g. not enough tokens, wrong api key, etc.
        ServerError
            raised when completion fails on the side of the LLM provider
        '''
        if llm == 'openai':
            return Completion.openai(prompt, temperature=temperature, model=model)
        elif llm == 'google':
            return Completion.google_completion(prompt, temperature=temperature, model=model)
        else:
            raise NotImplementedError(f"Completion model {llm} not implemented")