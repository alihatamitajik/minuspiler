from dataclasses import dataclass
from enum import Enum


@dataclass
class Symbol:
    lexeme: str
    address: int
    s_type: str
    size: int = 0
    args: list = None


class SymbolTable:
    def __init__(self) -> None:
        self.scope = {"symbol": {}, "up": None}

    def check(self, id):
        if id in self.scope["symbol"]:
            raise KeyError(f"ID({id}) already declared in this scope")

    def install_var(self, id, type, address):
        self.check(id)
        self.scope["symbol"][id] = Symbol(id, address, type)

    def install_arr(self, id, type, address, size):
        self.check(id)
        self.scope["symbol"][id] = Symbol(id, address, type, size)

    def install_func(self, id, type, address):
        self.check(id)
        self.scope["symbol"][id] = Symbol(id, address, type, 0, [])

    def add_arg_func(self, id, arg):
        self.scope["symbol"][id].args.append(arg)

    def get_symbol_addr(self, id):
        scope = self.scope
        while scope:
            if id in scope["symbol"]:
                return scope["symbol"][id].address
            scope = scope["up"]
        return KeyError(f"ID({id}) not declared")

    def up_scope(self):
        self.scope = {"symbol": {}, "up": self.scope}

    def down_scope(self):
        self.scope = self.scope["up"]
