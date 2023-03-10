from typing import Tuple, List
from enum import Enum
from dataclasses import dataclass

KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']


class TokenType(Enum):
    """Token Type

    Type of the token in the C-Minus Language
    """
    NUM, ID, KEYWORD, SYMBOL, COMMENT, WHITESPACE = range(6)


"""Token

Token is a type alias for tuple(int, str) which will be used as tokens in the
compiler. `str` part will change in the future but for now scanner will pass
type of the token, which is an integer, and the lexim of the token.
"""
Token = Tuple[TokenType, str]
