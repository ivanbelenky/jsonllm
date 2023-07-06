from json.decoder import JSONDecodeError
from typing import (
    Union, 
    TypedDict, 
    Optional, 
)

from jsonllm.utils import _to_dict_replacement, _to_dict_regex


JSONCompatible = Union[str, int, float, bool, None, dict, list]
JSONtypes = (str, int, float, bool, None, dict, list)

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

    @staticmethod
    def _rename_keys(schema, response: dict) -> dict:
        #TODO: nested
        return {schema.get(k, {}).get('name', k): v for k,v in response.items()}
        
        

def is_valid_schema_key(key: Union[SchemaKey, Schema]) -> bool:
    '''Being a valid key is either holding the SchemaKey type or a Schema'''
    if len(key) == 0:
        return False
    if all(isinstance(v, dict) for v in key.values()):
        return all(is_valid_schema_key(v) for v in key.values())
    if any(isinstance(v, dict) for v in key.values()):
        return False
    if any(keys not in SchemaKey.__annotations__ for keys in key.keys()):
        return False

    for k, a in SchemaKey.__annotations__.items():
        if any(isinstance(t, (Validator, Caster)) for t in a.__args__):
            continue
        if all(not isinstance(key.get(k), t) for t in a.__args__): 
            return False
    return True


def is_valid_schema(schema: Schema) -> bool:
    for sk, sv in schema.items():
        if not isinstance(sk, str): 
            return False
        if isinstance(sv, dict):
            if not is_valid_schema_key(sv): 
                return False
    return True


def validate_schema(schema: Schema):
    if not isinstance(schema, dict) or is_valid_schema(schema):
        raise SchemaError
