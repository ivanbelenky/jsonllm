from typing import Optional, Union, Dict

from retry import retry # type: ignore

from .schema import Schema, ParsedResponse, validate_schema, to_prompt
from .completions import _Completion


def loads(text: str,
          schema: Schema,
          *,
          model: str='gpt-3.5-turbo',
          retries: int=1,
          prompt: Optional[str]=None,
          **model_kwargs: Dict[str, Union[str, float, int]]) -> ParsedResponse:
    '''Load a schema from a completion prompt'''
    validate_schema(schema)
    complete = retry(_Completion.ServerError, tries=retries)(_Completion.complete_prompt)
    prompt = prompt if prompt is not None else to_prompt(schema, text)
    return ParsedResponse(complete(prompt, model, **model_kwargs), schema)
