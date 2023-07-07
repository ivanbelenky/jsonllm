REPLACEMENTS = [
    {},
    {
    '\'': '"',
    ' ': '',
    '\n': ''
}]

OPENAI_MODELS = ['ada', 'babbage', 'curie', 'davinci', 'gpt-3.5-turbo']
GOOGLE_MODELS = ['chat-bison@001', 'text-bison@001']

DEFAULT_REPLACE = REPLACEMENTS[1]

REGEX_PATTERNS = [r'{[^{}]*}', r'\[[^\[\]]*\]']

MAX_TOKENS = {
    'chat-bison@001': float('inf'), 
    'ada': 2048,
    'babbage': 2048,
    'curie': 2048,
    'davinci': 2048,
    'gpt-3.5-turbo': 4096,
}

DEFAULT_TEMPERATURE = 0.
DEFAULT_MODEL_KWARGS = {
    'chat-bison@001': {'temperature': DEFAULT_TEMPERATURE, 'max_output_tokens': 1024, 'top_p': 0.8, 'top_k': 40},
    'text-bison@001': {'temperature': DEFAULT_TEMPERATURE, 'max_output_tokens': 1024, 'top_p': 0.8, 'top_k': 40},
    'ada': {'temperature': DEFAULT_TEMPERATURE},
    'babbage': {'temperature': DEFAULT_TEMPERATURE},
    'curie': {'temperature': DEFAULT_TEMPERATURE},
    'davinci': {'temperature': DEFAULT_TEMPERATURE},
    'gpt-3.5-turbo': {'temperature': DEFAULT_TEMPERATURE},    
}

EXAMPLES_PROMPTS = [
    'Examples: <examples>',
]

SCHEMA_PLACEHOLDER = '<schema>'
TEXT_PLACEHOLDER = '<text>'
PROMPT_TO_PARSE_SCHEMA = """
Given the following text:

\"\"\"
<text>
\"\"\"

Create a JSON object with the following keys. If keys are not found input null.
Follow the instructions to find the key values in the text.

<schema>
"""