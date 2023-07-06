## `jsonllm` (WIP)

```python
import jsonllm
jsonllm.config('openai', 'sk-#################')

person = {
    'first_name': {
        'types': str,
        'needed': True,
        'instructions': 'Find the first name, if not found input John'        
    },
    'last_name': {
        'types': str,
        'needed': True,
        'instructions': 'Find the last name, if not found input Doe'
    },
    'date_of_birth': {
        'output_name': 'dob',
        'types': str,
        'instructions': 'Find the date of birth and cast it to isoformat'
    }
}

message = 'My name is John Connor, I think I was born 0 of Unix time.'
response = jsonllm.loads(message, person, completion='openai')
print(response)

{
    'first_name': 'John',
    'last_name': 'Connor',
    'dob': '1970-01-01'
}

```
