import string
from typing import Tuple, List
from enum import Enum
from dataclasses import dataclass


# Keywords
KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']
# Letters
L = string.ascii_letters
# Digits
D = string.digits
# symbols without star (*) and (=) (these will have separate tails)
S = ";:,[](){}+-<"
# Whitespaces
W = string.whitespace
# All accepted characters
SIGMA = L + D + S + W
# Extended Symbols (All special characters that can be used in code)
SPEC = ";:,[](){}+-</*="
# End of Text
EOT = "\x05"


class TokenType(Enum):
    """Token Type

    Type of the token in the C-Minus Language

    DOLOR shows end of file.
    """
    NUM, ID, KEYWORD, SYMBOL, COMMENT, WHITESPACE, DOLOR = range(7)

    def __str__(self) -> str:
        return self.name


"""Token

Token is a type alias for tuple(int, str) which will be used as tokens in the
compiler. `str` part will change in the future but for now scanner will pass
type of the token, which is an integer, and the lexim of the token.
"""
Token = Tuple[TokenType, str]


class ErrorType(Enum):
    """Types of error to be passed to the panic method"""
    INVALID_INPUT = 0,
    INVALID_NUMBER = 1,
    UNMATCHED_COMMENT = 2,
    UNCLOSED_COMMENT = 3

    def __str__(self) -> str:
        return self.name.title().replace("_", " ")


"""Err
<lexim, error type, #line>
"""
Err = Tuple[str, ErrorType, int]


@dataclass
class Transition:
    """Transition

    next_state: index of the next state in the list of states kept by the object
    be careful with the indexes.

    literal: if the input is in literal it is accepting
    """
    literal: str
    next_state: int = None
    can_none: bool = True


@dataclass
class AutoTailState:
    """Each state can have multiple transition and will be checked in order of
    the list. If the state is accepting dfa will return its type.

    Accepting states that has callback function in them, callback function
    should be returned as type instead of automatic type return"""
    transitions: List[Transition]
    is_accepting: bool = False
    is_retreat: bool = False
    callback = None


class SymbolTable:
    """Symbol Table"""

    def __init__(self) -> None:
        """TODO: dumb implementation of symbol table. it could be better it
        think"""
        self.table = {}
        for key in sorted(KEYWORDS):
            self.table[key] = None

    def dump(self):
        """dumps symbol table entries into a file

        Args:
            filename (str): name of the file that table will be dumped into.
        """
        raise NotImplementedError()

    def install(self, id_key):
        """insert id/keyword if it is not already in table

        Args:
            id_key (str): lexim of the symbol
        """
        if id_key not in self.table:
            self.table[id_key] = None


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
