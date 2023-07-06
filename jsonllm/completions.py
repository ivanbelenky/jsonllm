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
            project_id = None # TODO: config['project_id']
            location = None # TODO: "us-central1"
            parameters = {
                    "temperature": temperature,
                    "max_output_tokens": 1024,
                    "top_p": 0.8,
                    "top_k": 40,
                }

            vertexai.init(project=project_id, location=location)
            if 'chat' in model:
                chat_model = ChatModel.from_pretrained(model)
                raw_response = chat_model.start_chat(examples=[]).send_message(prompt, **parameters).text
            elif 'text' in model:
                text_model = TextGenerationModel.from_pretrained(model)
                raw_response = text_model.predict(prompt, **parameters).text

            return raw_response
        except Exception as e:
            raise Completion.ClientError(f"Failed to complete prompt: {e}")

    @staticmethod
    def complete_prompt(prompt: str,
                        llm: str,
                        model: str,
                        **model_kwargs,
                        ):
        '''
        '''
        if llm == 'openai':
            return Completion.openai(prompt, model, **model_kwargs)
        elif llm == 'google':
            return Completion.google_completion(prompt, model=model, **model_kwargs)
        else:
            raise NotImplementedError(f"Completion model {llm} not implemented")