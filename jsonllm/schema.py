import warnings
import dataclasses
from dataclasses import dataclass, field, fields, Field
from typing import Tuple, Callable, Union, Any, Dict, List, NewType, TypeVar


JSONCompatible = Union[str, int, float, bool, None, dict, list]
JSONtypes = (str, int, float, bool, None, dict, list)


class Schema(type): pass
class Dataclass(type): pass
class UnparseableField(type): pass


class SchemaError(Exception):
    def __init__(self):
        super().__init__("No field was of type Field")


@dataclass
class ToParse:
    name: str = None
    types: Union[type, Tuple[type, ...]] = JSONtypes
    caster: Callable[[Any], Any] = None
    valid: Callable[[Any], bool] = None
    needed: bool = False
    instructions: str = None
    default: Any = None


def parse_field(name=None,    
                types=None,
                caster=None,
                valid=None,
                needed=False,
                instructions='',
                default=None) -> ToParse:
    '''Create a field that can be used to parse a json response.'''
    types = types if isinstance(types, tuple) else (types,)
    return field(default=ToParse(name=name, types=types, caster=caster, 
                                      valid=valid, needed=needed, instructions=instructions, 
                                      default=default))


def _strip_unparseable_fields_from_schema(schema_dict) -> None:
    '''Remove all keys that have NotParseableField as their value'''
    for field_name, field_info in schema_dict.items():
        if isinstance(field_info, UnparseableField):
            del schema_dict[field_name]
        elif isinstance(field_info, dict):
            _strip_unparseable_fields_from_schema(field_info)


def _dataclass_to_schema_dict(_dataclass: Dataclass) -> Dict[str, Any]:
    '''From dataclass to dictionary schema containing only the ToParseableFields'''
    schema = {}
    for _field in fields(_dataclass):
        tp_field = _field.default
        if not isinstance(tp_field, ToParse):
            schema[_field.name] = UnparseableField
        elif isinstance(tp_field, ToParse):
            if any([dataclasses.is_dataclass(tp) for tp in tp_field.types]):
                schema[_field.name] = _dataclass_to_schema_dict(tp_field.types[0])
            else:
                schema[_field.name] = {
                    'types': tp_field.types,
                    'needed': tp_field.needed,
                    'instructions': tp_field.instructions,
                    'default': tp_field.default,
                    'name': tp_field.name if tp_field.name else tp_field.name,
                }
    return schema


def _validate_schema_dict(schema_dict: Dict[str, Any], invalid_fields: List[str], field_name: str):
    for child_field_name, child_field_info in schema_dict.items():
        if isinstance(child_field_info, UnparseableField):
            invalid_fields.append(f'{field_name}.{child_field_name}')
        elif isinstance(child_field_info, dict):
            _validate_schema_dict(child_field_info, invalid_fields, f'{field_name}.{child_field_name}')


def validate_schema(schema: Union[Dataclass, Dict[str, Union[Any, Field]]]):
    invalid_fields = []
    if dataclasses.is_dataclass(schema):
        schema_dict = _dataclass_to_schema_dict(schema)
    
    for field_name, field_info in schema_dict.items():
        if isinstance(field_info, UnparseableField):
            invalid_fields.append(field_name)
        elif isinstance(field_info, dict):
            _validate_schema_dict(field_info, invalid_fields, field_name)

    invalid_fields_n = len(invalid_fields)
    if invalid_fields_n > 0:
        warnings.warn(f"Invalid fields: {invalid_fields}")
    _strip_unparseable_fields_from_schema(schema_dict)
    if not schema_dict:
        raise SchemaError()
