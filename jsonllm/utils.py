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
    prompt_tokens = len(prompt.split(' '))
    return prompt_tokens


def no_tokens(prompt: str, model: str='gpt-3.5-turbo') -> int:
    '''despite the model being gpt-3.5-turbo it is safe to assume the result
    fo other LLMs, SOTA embeddings are pretty similar.'''
    try:
        encoding = tiktoken.get_encoding(model)
    except:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except:
            return no_tokens_approx(prompt)
    prompt_tokens = len(encoding.encode(prompt))
    return prompt_tokens


def _replace_and_load(raw_response: str, 
                      replacements: Dict[str, str]=DEFAULT_REPLACE) -> dict:        
        response = raw_response
        for k,v in replacements.items():
            response = response.replace(k, v)
        response = json.loads(response)
        return response


def _to_dict_replacement(raw_response: str):
    for i, replacement in enumerate(REPLACEMENTS):
        try:
            return _replace_and_load(raw_response, replacements=replacement) 
        except JSONDecodeError as e:
            if i == len(REPLACEMENTS) - 1: raise e


def _to_dict_regex(raw_response: str):
    for i, pattern in REGEX_PATTERNS:
        try:
            matches = re.findall(pattern, raw_response)
            n_matches = len(matches) 
            if n_matches == 0:
                raise JSONDecodeError('No matches found', raw_response, 0)
            if n_matches > 1:
                warnings.warn(f'Found {n_matches} matches found')
            return json.loads(matches[0])
        except JSONDecodeError as e:
            if i == len(REGEX_PATTERNS)-1: raise e
    