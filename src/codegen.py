from collections import deque
from util.types_ import SymbolTable


class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table = symbol_table
        self.pb = [None] * 100
        self.i = 0
        self.ss = deque()
        self.top = -1

    def _pop(self, n):
        """Pops n items from semantic stack"""
        for _ in range(n):
            self.ss.pop()

    def _push(self, x):
        """Pushes x into the stack"""
        self.ss.append(x)
