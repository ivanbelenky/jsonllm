from retry import retry

from jsonllm.schema import Schema, ParsedResponse, validate_schema, to_prompt
from jsonllm.completions import _Completion


def loads(text: str,
          schema: Schema,
          *,
          llm: str='openai',
          model: str='gpt-3.5-turbo',
          retries: int=0,
          prompt: str=None,
          **model_kwargs) -> ParsedResponse:
    '''Load a schema from a completion prompt'''
    validate_schema(schema)
    complete = retry(_Completion.ServerError, tries=retries)(_Completion.complete_prompt)
    prompt = prompt if prompt is not None else to_prompt(schema, text)
    return ParsedResponse(complete(text, llm, model, **model_kwargs), schema)
