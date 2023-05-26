from collections import deque
from util.symbol import SymbolTable
from util.types_ import Lookahead


class CodeGenerator:
    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.pb = [None] * 100
        self.i = 0
        self.ss = deque()
        self.top = -1
        self.data_p = 100
        self.temp_p = 500

    def pop(self, n):
        """Pops n items from semantic stack"""
        for _ in range(n):
            self.ss.pop()

    def push(self, x):
        """Pushes x into the stack"""
        self.ss.append(x)

    def code_gen(self, action, lookahead):
        getattr(self, "action_" + action[1:])(lookahead)

    def get_data(self, size=1):
        """returns address of data allocated in data block"""
        addr = self.data_p
        self.data_p += size * 4
        return addr

    def get_temp(self):
        self.temp_p += 4
        return self.temp_p - 4

    def action_ptype(self, lookahead: Lookahead):
        """Pushes type in lookahead. This is separated from #pname because it
        might be useful in the future and semantic analyzer (not sure)."""
        self.push(lookahead.lexeme)

    def action_pname(self, lookahead: Lookahead):
        """Pushes id name. This is separated from #ptype because it might be 
        useful in the future and semantic analyzer (not sure)."""
        self.push(lookahead.lexeme)

    def action_pid(self, lookahead: Lookahead):
        """Pushed address of current ID from symbol table"""
        addr = self.symbol_table.get_symbol_addr(lookahead.lexeme)
        self.push(addr)

    def action_pnum(self, lookahead: Lookahead):
        """Pushes number in lookahead."""
        self.push(int(lookahead.lexeme))

    def action_var(self, lookahead: Lookahead):
        """Registers variable

        And pops required data from semantic stack:
            - type
            - name
        """
        self.symbol_table.install_var(self.ss[self.top],
                                      self.ss[self.top-1],
                                      self.get_data())
        self.pop(2)

    def action_arr(self, lookahead: Lookahead):
        """Registers array variable

        And pops required data from semantic stack:
            - type
            - name
            - num (size of array)
        """
        size = self.ss[self.top]
        self.symbol_table.install_arr(self.ss[self.top-1],
                                      self.ss[self.top-2],
                                      self.get_data(size),
                                      size)
        self.pop(3)
