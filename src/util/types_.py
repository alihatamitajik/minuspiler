from typing import Tuple, List
from enum import Enum
from dataclasses import dataclass

KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']


class TokenType(Enum):
    """Token Type

    Type of the token in the C-Minus Language
    """
    NUM, ID, KEYWORD, SYMBOL, COMMENT, WHITESPACE = range(6)
