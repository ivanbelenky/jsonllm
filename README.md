## `jsonllm`
-----------

![image](https://github.com/ivanbelenky/jsonllm/assets/49297252/d0526122-0199-4434-ad3c-19d11a3a9fd4)

## Installation
---------------
### From source

```bash
git clone https://github.com/ivanbelenky/jsonllm.git
cd jsonllm
python3 -m pip install -e .
```

## Documentation
----------------

### Schema type

```python
class SchemaKey(TypedDict):
    name: Optional[str]
    type: Optional[type]
    default: JSONCompatible
    required: Optional[bool]
    instructions: Optional[str]
    valid: Optional[Caster] 
    caster: Optional[Validator]

class Schema(TypedDict):
    __key__: Union[SchemaKey, 'Schema'] # nested schemas
```


### Example

```python
import jsonllm
import openai

# vertexai.init(project_id='jsonllm-rocks?', location='us-central1') | 
openai.api_key = 'sk-...'

person = {
    'first_name': {
        'type': str,
        'required': True,
        'instructions': 'Find the first name, if not found input John'        
    },
    'last_name': {
        'type': str,
        'required': True,
        'instructions': 'Find the last name, if not found input Doe'
    },
    'date_of_birth': {
        'name': 'dob',
        'type': str,
        'instructions': 'Find the date of birth and cast it to isoformat'
    }
}

message = 'My name is John Connor, I think I was born 0 of Unix time.'
response = jsonllm.loads(message, person, model='gpt-3.5-turbo')
print(response.response)

{
    'first_name': 'John',
    'last_name': 'Connor',
    'dob': '1970-01-01'
}

```
