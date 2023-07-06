REPLACEMENTS = [
    {},
    {
    '\'': '"',
    ' ': '',
    '\n': ''
}]

DEFAULT_REPLACE = REPLACEMENTS[1]

REGEX_PATTERNS = [
    r'{(?:[^{}]|(?R))*}',
    r'{[^{}]*}',
    r'\[[^\[\]]*\]',
]

MAX_TOKENS = {
    'chat-bison@001': -1, #TODO: check limits
    'ada': 2048,
    'babbage': 2048,
    'curie': 2048,
    'gpt-3.5-turbo': 4096,
}


EXAMPLES_PROMPTS = [
    'Examples: <examples>',
]

