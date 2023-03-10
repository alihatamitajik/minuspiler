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


@dataclass
class Transition:
    """Transition

    next_state: index of the next state in the list of states kept by the object
    be careful with the indexes.

    literal: if the input is in literal it is accepting

    is_other: if this option is true, then input should not be in the literal to
    be accepted.
    """
    is_other: bool = False
    next_state: int = None
    literal: str = ""


@dataclass
class AutoTailState:
    """Each state can have multiple transition and will be checked in order of
    the list. If the state is accepting dfa will return its type"""
    transitions: List[Transition] = []
    is_accepting: bool = False
    is_retreat: bool = False


class SymbolTable:
    """Symbol Table"""

    def __init__(self) -> None:
        """TODO: dumb implementation of symbol table. it could be better it
        think"""
        self.table = {}

    def dump(filename):
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
