import json
from time import sleep
from dateutil.parser import parse

from jsonllm.schema import Schema, ParsedResponse, validate_schema
from jsonllm.completions import Completion
    

def loads(text: str,
          schema: Schema,
          *,
          llm: str='openai',
          model: str='gpt-3.5-turbo',
          retries: int=0,
          temperature: float=0.) -> ParsedResponse:
    '''Load a schema from a completion prompt'''
    validate_schema(schema)
    raw_response = Completion.complete_prompt(text, llm, model, temperature)
    return ParsedResponse(raw_response, schema)
