## `jsonllm`

```python
from dateutil.parser import parse
from dataclasses import dataclass

import jsonllm
from jsonllm import ToParse, parse_field

jsonllm.config('openai', 'sk-123')
#jsonllm.config('google', 'project_id', 'us-central1')
               
@dataclass
class Address:
    street: ToParse=parse_field(types=str, needed=True,
                                instructions='Find the street, if not found input 123 Main St')
    city: ToParse=parse_field(types=str, needed=True,
                              instructions='Find the city, if not found input New York')

@dataclass
class Person:
    first_name: ToParse=parse_field(name='first_name', types=str, needed=True,
                                    instructions='Find the first name, if not found input John')
    last_name: ToParse=parse_field(name='last_name', types=str, needed=True,
                                   instructions='Find the last name, if not found input Doe')
    address: ToParse=parse_field(output_name='address', types=Address, needed=True)
    age: ToParse=parse_field(output_name='age', types=(int, float), valid=lambda x: x > 0, default=0)
    date_of_birth: ToParse=parse_field(output_name='dob', types=str, caster=lambda dob: parse(dob).date(),
                                        instructions='Find the date of birth and cast it to isoformat')
    

message = 'My name is John Connor, I think I was born 0 of Unix time.'
response = jsonllm.loads(message, schema=Person, completion='openai')
print(response)
```
