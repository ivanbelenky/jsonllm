import json
from time import sleep
from dateutil.parser import parse
from json.decoder import JSONDecodeError
from typing import Union, Dict

from jsonllm.schema import Schema, validate_schema
from jsonllm.completions import Completion
from jsonllm.utils import _to_dict_replacement, _to_dict_regex


class ParsedResponse:
    def __init__(self, raw_response: str, schema: Schema):
        self.raw_response = raw_response
        self.schema = schema
        self.response_dict = self.to_dict(raw_response)
        self.validate_missing_cast()

    def to_dict(self, raw_response=None) -> dict:
        '''Convert the raw response to a dictionary'''
        raw_response = raw_response or self.raw_response
        try:
            response = _to_dict_replacement(raw_response)
            return self.rename_keys(response)
        except JSONDecodeError as e:
            pass
        try:
            response = _to_dict_regex(raw_response)
            return self.rename_keys(response)
        except JSONDecodeError as e:
            raise e
        
    def validate_missing_cast(self, response: dict) -> dict:
        raise NotImplementedError

    def to_dataclass(self, dataclass: type) -> object:
        '''Convert the raw response to a dataclass'''
        return dataclass(**self.response_dict)

    @staticmethod
    def _rename_keys(schema, response: dict) -> dict:
        for k,v in response.items():
            name = schema[k].get('name')
            if name is not None and isinstance(name, str):
                response[name] = v
                response.pop(k)
        return response
    

def loads(text: str,
          *,
          schema: Union[Schema, dict],
          llm: str='openai',
          model: str='gpt-3.5-turbo',
          retries: int=0,
          temperature: float=0.) -> ParsedResponse:
    '''Load a schema from a completion prompt'''
    validate_schema(schema)
    raw_response = Completion.complete_prompt(text, llm, model, temperature)
    return ParsedResponse(raw_response, schema)
