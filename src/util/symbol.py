from dataclasses import dataclass


@dataclass
class SemanticSymbol:
    """Symbol class that is returned by get_by_id

    This class contains name, addr and weather it's a global (that should be
    used directly as its address), relative local address (that should be
    used with TOP_SP address) or a constant.

    These addresses should be indexed and used at runtime so its better to have
    a dedicated function for conversions and using them.

    Note: is_pointer flag is intended to be useful when we pass address of first
    element of an array and it might not be used (I'm not sure at this moment).
    """
    name: str
    typ: str
    value: int
    args: list
    is_function: bool
    is_global: bool
    is_constant: bool
    is_pointer: bool


class SymbolTable:
    def __init__(self) -> None:
        pass

    def install_func(self, name, return_type):
        pass

    def end_func(self):
        pass

    def add_arg_to_func(self, name):
        pass

    def install_variable(self, name, type):
        pass

    def install_array(self, name, type, size):
        pass

    def get_by_id(self, id):
        pass

    def scope_up(self, id):
        pass

    def scope_down(self, id):
        pass
