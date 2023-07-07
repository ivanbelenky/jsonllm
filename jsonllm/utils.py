import re
import json
import warnings
from typing import Dict
from json import JSONDecodeError

import tiktoken
from openai.error import (
    RateLimitError, 
    APIConnectionError, 
    APIError, 
    ServiceUnavailableError, 
    Timeout
)

from jsonllm.constants import DEFAULT_REPLACE, REPLACEMENTS, REGEX_PATTERNS


OpenAIErrors = (RateLimitError, APIConnectionError, APIError, ServiceUnavailableError, Timeout)


def no_tokens_approx(prompt: str) -> int:
    prompt_tokens = max(len(prompt)//4,4)
    return prompt_tokens


def no_tokens(prompt: str, model: str='gpt-3.5-turbo') -> int:
    '''despite the model being gpt-3.5-turbo it is safe to assume the result
    for other embeddings are pretty similar.'''
    try:
        encoding = tiktoken.get_encoding(model)
    except:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except:
            return no_tokens_approx(prompt)
    return len(encoding.encode(prompt))
    

def _replace_and_load(raw_response: str, 
                      replacements: Dict[str, str]=DEFAULT_REPLACE) -> dict:        
        response = raw_response
        for k,v in replacements.items():
            response = response.replace(k, v)
        return json.loads(response)
        

def _to_dict_replacement(raw_response: str):
    for replacement in REPLACEMENTS:
        try:
            return _replace_and_load(raw_response, replacements=replacement) 
        except JSONDecodeError as e:
            pass
    raise JSONDecodeError('No matches found', raw_response, 0)


def _to_dict_regex(raw_response: str):
    for pattern in REGEX_PATTERNS:
        try:
            matches = re.findall(pattern, raw_response)
            n_matches = len(matches) 
            if n_matches == 0:
                raise JSONDecodeError('No matches found', raw_response, 0)
            if n_matches > 1:
                warnings.warn(f'Found {n_matches} matches found')
            return json.loads(matches[0])
        except JSONDecodeError as e:
            pass
    raise JSONDecodeError('No matches found', raw_response, 0)