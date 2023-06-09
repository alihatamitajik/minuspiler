from dataclasses import dataclass
from enum import Enum


@dataclass
class Symbol:
    lexeme: str
    address: str
    s_type: str
    size: int = 0
    args: list = None


class SymbolTable:
    def __init__(self) -> None:
        self.scope = {
            "symbol": {'output': Symbol('output', 'output', 'void', 0, ['int'])},
            "up": None}

    def check(self, id):
        if id in self.scope["symbol"]:
            return KeyError(f"ID({id}) already declared in this scope")

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
        self.get_symbol_addr(id).args.append(arg)
        # print(id, ":", self.get_symbol_addr(id).args)


    def get_symbol_addr(self, id):
        scope = self.scope
        while scope:
            if id in scope["symbol"]:
                return scope["symbol"][id]
            scope = scope["up"]
        return KeyError(f"\'{id}\' is not defined.")

    def get_symbol_by_addr(self, addr):
        scope = self.scope
        while scope:
            for symbol in scope["symbol"].values():
                if symbol.address == addr:
                    return symbol
            scope = scope["up"]
        return KeyError(f"Address ({addr}) not registered")

    def up_scope(self):
        self.scope = {"symbol": {}, "up": self.scope}

    def down_scope(self):
        self.scope = self.scope["up"]
