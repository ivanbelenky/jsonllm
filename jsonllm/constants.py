from typing import Dict, List, Union, Any

JSONCompatible = Union[str, int, float, bool, None, dict, list]
JSONtypes = (str, int, float, bool, None, dict, list)

REPLACEMENTS: List[Dict[str, str]] = [
    {},
    {
    '\'': '"',
    ' ': '',
    '\n': ''
}]

OPENAI_MODELS = ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4o-mini']
GOOGLE_MODELS = ['chat-bison@001', 'text-bison@001']
ANTHROPIC_MODELS = ['claude-3-opus-20240229']

REGEX_PATTERNS = [r'{[^{}]*}', r'\[[^\[\]]*\]']

MAX_TOKENS = {
    'chat-bison@001': float('inf'), 
    'gpt-3.5-turbo': 4096,
    'gpt-4': 4096,
}

DEFAULT_TEMPERATURE = 0.
DEFAULT_SYSTEM_PROMPT = 'You are an expert dedicated to transform natural langauge text to JSON given a format schema'
DEFAULT_BISON_KWARGS = {'temperature': DEFAULT_TEMPERATURE, 'max_output_tokens': 1024, 'top_p': 0.8, 'top_k': 40}
DEFAULT_CLAUDE_KWARGS = {'temperature': DEFAULT_TEMPERATURE, 'max_tokens': 4096, 'system': DEFAULT_SYSTEM_PROMPT}

DEFAULT_MODEL_KWARGS: Dict[str, Dict[str, Any]] = {
    'chat-bison@001': DEFAULT_BISON_KWARGS,
    'text-bison@001': DEFAULT_BISON_KWARGS,
    'gpt-3.5-turbo': {'temperature': DEFAULT_TEMPERATURE, 'response_format': { "type": "json_object" }},
    'gpt-4': {'temperature': DEFAULT_TEMPERATURE},
    'gpt-4o': {'temperature': DEFAULT_TEMPERATURE, 'response_format': { "type": "json_object" }},
    'gpt-4o-mini': {'temperature': DEFAULT_TEMPERATURE, 'response_format': { "type": "json_object" }},
    'claude-3-opus-20240229': DEFAULT_CLAUDE_KWARGS,
    'claude-3-haiku-20240307': DEFAULT_CLAUDE_KWARGS,
    'claude-3-sonnet-20240229': DEFAULT_CLAUDE_KWARGS,
}

EXAMPLES_PROMPTS = [
    'Examples: <examples>',
]

SCHEMA_PLACEHOLDER = '<schema>'
TEXT_PLACEHOLDER = '<text>'
PROMPT_TO_PARSE_SCHEMA = f"""
As a genius expert, your task is to understand the content of the following text 

\"\"\"
{TEXT_PLACEHOLDER}
\"\"\"

Create a JSON object with the following schema. If keys are not found input null.
Follow the extra instructions to find the key values in the text. Refrain from outputting
anything but the keys

{SCHEMA_PLACEHOLDER}
"""
