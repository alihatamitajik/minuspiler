from collections import deque
from util.symbol import SymbolTable
from util.types_ import Lookahead
from util.instruction import ADD, MUL, SUB, EQ, LT, ASSIGN, JPF, JP, PRINT
from util.instruction import operation

TOP = -1


class CodeGenerator:
    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.pb = [None] * 100
        self.i = 0
        self.ss = deque()
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
        self.push(f"#{lookahead.lexeme}")

    def action_var(self, _):
        """Registers variable

        And pops required data from semantic stack:
            - type
            - name
        """
        self.symbol_table.install_var(self.ss[TOP],
                                      self.ss[TOP-1],
                                      str(self.get_data()))
        self.pop(2)

    def action_arr(self, _):
        """Registers array variable

        And pops required data from semantic stack:
            - type
            - name
            - num (size of array)
        """
        size = int(self.ss[TOP][1:])
        self.symbol_table.install_arr(self.ss[TOP-1],
                                      self.ss[TOP-2],
                                      str(self.get_data(size)),
                                      size)
        self.pop(3)

    def action_scope_up(self, _):
        """Add one scope to the symbol table"""
        self.symbol_table.up_scope()

    def action_scope_down(self, _):
        """Remove top level scope from stack (its ids can't be used later)"""
        self.symbol_table.down_scope()

    def action_assign(self, _):
        """Assigns top of stack to the operand below it"""
        val = self.ss[TOP]
        self.pb[self.i] = ASSIGN(val, self.ss[TOP - 1])
        self.i += 1
        self.pop(2)
        self.push(val)

    def action_pexpr(self, _):
        """Pop Expression from stack"""
        self.pop(1)

    def action_calc(self, _):
        """Calculates operation inside SS on operands in SS"""
        t = self.get_temp()
        self.pb[self.i] = operation[self.ss[TOP - 1]](
            self.ss[TOP],
            self.ss[TOP-2],
            str(t))
        self.pop(3)
        self.push(str(t))

    def action_pop(self, lookahead: Lookahead):
        """Push operator into SS"""
        self.push(lookahead.lexeme)
