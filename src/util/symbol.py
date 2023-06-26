from dataclasses import dataclass
from enum import Enum


class SymbolType(Enum):
    VOID = 0
    INT = 1
    ARRAY_VOID = 2
    ARRAY_INT = 3
    POINTER = 5


@dataclass
class SemanticSymbol:
    """Symbol class that is returned by get_by_id

    This class contains name, addr and weather it's a global (that should be
    used directly as its address), relative local address (that should be
    used with TOP_SP address) or a constant.

    These addresses should be indexed and used at runtime so its better to have
    a dedicated function for conversions and using them.
    """
    name: str
    type: SymbolType
    value: int
    args: list = None
    is_function: bool = False
    is_global: bool = False
    is_constant: bool = False


class SymbolEntry:
    def __init__(self, name, type, addr, is_global) -> None:
        self.name = name
        self.type = type
        self.addr = addr
        self.is_global = is_global

    @property
    def semantic(self):
        raise NotImplementedError("Should be implemented in the ")

    @property
    def is_func(self):
        return False

    def is_array(self):
        return False


class ActivationRecord:
    """Activation record

    Activation record class will act like a local symbol table of the function
    and handles scoping of the function. Scope variable will all be added to the
    AR at first and will be popped when the function returns (So we have same
    space for temporaries and user variables all mixed inside the AR).

    If stack grows from top to bottom:

    * Return Value (RV)     0
    * Return Address (RA)   4
    * Previous TOP (PT)     8    ] This two will be defined inside code gen and
    * Previous TOP SP (PSP) 12   ] is a reference of those
    * Arg
    * Arg[] -> address of first element should be in this cell of stack
    * ...
    * var
    * arr[0]
    * arr[1]
    * temp
    * temp
    * temp
    * var (of inner scope in the function)
    * arr[0] (of inner scope in the function)
    * temp (of inner scope in the function)
    * temp (of inner scope in the function)
    * ...
    *
    *
    *

    You should get the idea by now!    
    """

    def __init__(self) -> None:
        self.top_addr = 4 * 4

    def allocate(self, size=1):
        """Allocates space in the activation record and returns the relative
        index"""
        tmp = self.top_addr
        self.top_addr += size * 4
        return tmp

    @property
    def rv(self):
        return 0

    @property
    def ra(self):
        return 4

    @property
    def pt(self):
        return 8

    @property
    def psp(self):
        return 12

    @property
    def size(self):
        return self.top_addr


class VariableEntry(SymbolEntry):
    def __init__(self, name, type, addr, is_global=False) -> None:
        super().__init__(name, type, addr, is_global)

    def semantic(self):
        return SemanticSymbol(self.name, self.type, self.addr,
                              is_global=self.is_global)


class ArrayEntry(SymbolEntry):
    def __init__(self, name, type, addr, size, is_global=False) -> None:
        super().__init__(name, type, addr, is_global)
        self.size = size

    def is_array(self):
        return True

    def semantic(self):
        return SemanticSymbol(self.name, self.type, self.addr,
                              is_global=self.is_global)


class FunctionEntry(SymbolEntry):
    def __init__(self, name, type, addr) -> None:
        super().__init__(name, type, addr, True)
        self.ar = ActivationRecord()
        self.scopes = {"entries": {}, "last_scope": None}
        self.args = []

    def check(self, name):
        if name in self.scopes["entries"]:
            raise KeyError(f"ID({name}) is already defined in this scope")

    def add_arg(self, name, type: SymbolType):
        self.check(name)
        addr = self.ar.allocate()
        symbol = VariableEntry(name, type, addr)
        self.args.append(symbol)
        self.scopes["entries"][name] = symbol

    def add_var(self, name, type):
        self.check(name)
        addr = self.ar.allocate()
        symbol = VariableEntry(name, type, addr)
        self.scopes["entries"][name] = symbol

    def add_arr(self, name, type, size):
        self.check(name)
        addr = self.ar.allocate(size)
        symbol = ArrayEntry(name, type, addr, size)
        self.scopes["entries"][name] = symbol

    def scope_up(self):
        self.scopes = {"entries": {}, "last_scope": self.scopes}

    def scope_down(self):
        last_scope = self.scopes["last_scope"]
        if last_scope == None:
            raise RuntimeError(
                "Bad Action: Scope down without previous scope up")
        else:
            self.scopes = last_scope

    def get_by_id(self, id):
        scope = self.scopes
        while scope:
            entry = scope.get(id, None)
            if entry:
                return entry.semantic
            else:
                scope = scope["last_scope"]
        raise KeyError(f"ID({id}) not declared.")

    def get_temp(self):
        return SemanticSymbol("@!#$", SymbolType.INT, self.ar.allocate())

    def is_func(self):
        return True

    def semantic(self):
        return SemanticSymbol(self.name,
                              self.type,
                              self.addr,
                              list(self.args),
                              True)


class SymbolTable:
    """Symbol Table

    Symbol table should handle the addressing of the variables and temporaries.
    temporaries are allocated inside the AR and should be handled like normal
    integers (in terms of addressing and indexing).

    NOTE: All variables and temps should be indexed and used at each time. It's 
    not optimized and has a massive overhead on the program execution (but the
    duo is close and it works)!

    """

    def __init__(self, global_addr=152, stack_start=500) -> None:
        self.current_func = None
        self.global_last_addr = global_addr
        self.end_global = stack_start - 4
        self.table = dict()  # only global variables and functions

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

    def get_activation_record(self, id):
        pass

    def get_temp(self, id):
        pass
