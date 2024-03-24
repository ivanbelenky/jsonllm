import json
from copy import deepcopy
from json.decoder import JSONDecodeError
from typing import Union, TypedDict, Optional, List, Dict, Any, cast

from jsonllm.utils import _to_dict_replacement, _to_dict_regex
from jsonllm.constants import (
    PROMPT_TO_PARSE_SCHEMA,
    SCHEMA_PLACEHOLDER,
    TEXT_PLACEHOLDER,
    JSONCompatible,
)

class Validator: pass
class Caster: pass

class SchemaKey(TypedDict):
    name: Optional[str]
    type: Optional[type]
    default: JSONCompatible
    required: Optional[bool]
    instructions: Optional[str]
    valid: Optional[Caster] 
    caster: Optional[Validator]

class Schema(TypedDict):
    __key__: Union[SchemaKey, 'Schema']

SchemaError = TypeError(f"Schema must be a dictionary following {Schema}")

def is_valid_schema_key(key: Union[SchemaKey, Schema]) -> bool:
    '''Being a valid key is either holding the SchemaKey type or a Schema'''
    if len(key) == 0: return False
    if all(isinstance(v, dict) for v in key.values()) and len(key) > 1:
        return all(is_valid_schema_key(cast(Schema, v)) for v in key.values())
    if any(isinstance(v, dict) for v in key.values()): return False
    if any(k not in SchemaKey.__annotations__ for k in key.keys()): return False
    for k, a in SchemaKey.__annotations__.items():
        if any(isinstance(t, (Validator, Caster)) for t in a.__args__): continue
        if all(not isinstance(key.get(k), t) for t in a.__args__): return False
    return True

def is_valid_schema(schema: Schema) -> bool:
    for sk, sv in schema.items():
        if not isinstance(sk, str): return False
        if isinstance(sv, dict):
            if not is_valid_schema_key(cast(Schema, sv)): return False
    return True

def validate_schema(schema: Schema) -> None:
    if not isinstance(schema, dict) or not is_valid_schema(schema): raise SchemaError

def _shorten_schema(schema: Schema) -> Schema:
    shortened_schema = cast(Schema, {})
    for k, v in schema.items():
        if not all(isinstance(v, dict) for v in schema.values()): raise SchemaError
        if all(isinstance(vv, dict) for vv in cast(Schema,v).values()): shortened_schema[k] = _shorten_schema(cast(Schema, v)) # type: ignore
        else:
            if not cast(SchemaKey, v).get('instructions') is None and cast(SchemaKey, v).get('type') is None: shortened_schema[k] = {} # type: ignore
            elif not cast(SchemaKey, v).get('instructions', False): shortened_schema[k] = {'type': cast(SchemaKey, v).get('type').__name__} # type: ignore
            else: shortened_schema[k] = {'type': cast(SchemaKey, v).get('type').__name__, 'instructions': cast(SchemaKey, v).get('instructions')} # type: ignore
    return shortened_schema

def to_prompt(schema: Schema, text: str) -> str:
    if not isinstance(schema, dict) or not is_valid_schema(schema): raise SchemaError
    shortened_schema = _shorten_schema(schema)
    dumped_schema = json.dumps(shortened_schema, indent=4)
    return PROMPT_TO_PARSE_SCHEMA.replace(SCHEMA_PLACEHOLDER, dumped_schema).replace(TEXT_PLACEHOLDER, text)
           

class ParsedResponse:
    def __init__(self, raw_response: str, schema: Schema, name: Optional[str]=None):
        self.raw_response = raw_response
        self.schema = schema
        self.raw_response_dict = self.to_dict(raw_response)
        self.missing: List[str]; self.invalid: List[str]; self.exceptions: Dict[str, str]; 
        self.missing, self.invalid, self.exceptions = [], [], {}
        self.validated_casted_response = self.validate_missing_cast(self.raw_response_dict, self.schema, name or 'root', self.missing, self.invalid, self.exceptions)
        self.renamed_response = self._rename_keys(self.schema, self.validated_casted_response)

    @property
    def response(self) -> dict: return self.renamed_response

    def to_dict(self, raw_response: Optional[str]=None) -> dict:
        raw_response = raw_response or self.raw_response
        try: return _to_dict_replacement(raw_response)
        except JSONDecodeError: pass
        try:  return _to_dict_regex(raw_response)
        except JSONDecodeError: pass
        raise JSONDecodeError('No JSON parseable matches found for response: ', raw_response, 0)
        
    def validate_missing_cast(self, response: dict, schema: Schema, schema_name: str, missing: List[str], invalid: List[str], exceptions: Dict[str, str]) -> Dict[Any, Any]:
        validated_casted_response, schema = deepcopy(response), deepcopy(schema)
        for k, v in self.schema.items():
            if all(isinstance(vv, dict) for vv in v.values()): validated_casted_response[k] = self.validate_missing_cast(response[k], schema[k], f'{schema_name}.{k}', missing, invalid); continue # type: ignore
            if k not in response and self.schema[k].get('required', False): missing.append(f'{schema_name}.{k}'); continue # type: ignore
            if k not in response and self.schema[k].get('default', False): missing.append(f'{schema_name}.{k}'); continue # type: ignore
            if k not in response: validated_casted_response[k] = self.schema[k]['default'] # type: ignore
            if self.schema[k].get('caster', self.schema[k]['type']): # type: ignore
                try: validated_casted_response[k] = self.schema[k]['cast'](response[k]) # type: ignore
                except Exception as e: exceptions[f'{schema_name}.{k}'] = f'Failed to cast {response[k]}: {e}' # type: ignore
            if self.schema[k].get('valid', False): # type: ignore
                try: self.schema[k]['validate'](response[k]) # type: ignore
                except: invalid.append(f'{schema_name}.{k}')
        return validated_casted_response

    def _rename_keys(self, schema: Schema, response: Dict[str, Any]) -> Dict[str, Any]:
        renamed_response = deepcopy(response)
        for k, v in schema.items():
            if k not in response: continue
            if all(isinstance(vv, dict) for vv in cast(Schema,v).values()):
                renamed_response[k] = self._rename_keys(cast(Schema,v), response[k])
            if 'name' in cast(SchemaKey, v): renamed_response[cast(str, cast(SchemaKey,v)['name'])] = renamed_response.pop(k)
        return renamed_response
