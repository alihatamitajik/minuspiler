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
        self.arg_count = deque()
        self.semantic_errors = []

    def generate_output(self, file):
        if not self.semantic_errors:
            for i, inst in enumerate(self.pb):
                if not inst:
                    break
                file.write(f"{i}\t{inst}\n")
        else:
            file.write("The output code has not been generated.")

    def generate_errors(self, file):
        if not self.semantic_errors:
            file.write("The input program is semantically correct.\n")
        else:
            pass  # TODO: write semantic errors

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
        addr = self.symbol_table.get_symbol_addr(lookahead.lexeme).address
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
            self.ss[TOP-2],
            self.ss[TOP],
            str(t))
        self.i += 1
        self.pop(3)
        self.push(str(t))

    def action_pop(self, lookahead: Lookahead):
        """Push operator into SS"""
        self.push(lookahead.lexeme)

    def action_call(self, _):
        """Call the function inside SS with number of its arguments

        NOTE: As the arguments are pushed inside the SS with Expression 
        non-terminal we don't need to push them, but some action may be needed 
        for semantic analysis in Args and arg related rules."""
        num_arg = self.arg_count.pop()
        symbol = self.symbol_table.get_symbol_by_addr(self.ss[TOP - num_arg])
        if symbol.args == None:
            raise ValueError(f"ID({symbol.lexeme}) is not a function")
        if len(symbol.args) != num_arg:
            raise TypeError(
                f"Bad number of arguments ({num_arg}) for {symbol.lexeme}({', '.join(symbol.args)})")
        if symbol.lexeme == 'output':
            self.code_output()
        else:
            pass  # should be replaced with real function call in next Phase
        self.pop(num_arg + 1)  # pop arguments id of func
        # push return value (?) TODO: this is temp for return value of output
        self.push(None)

    def code_output(self):
        self.pb[self.i] = PRINT(self.ss[TOP])
        self.i += 1

    def action_incarg(self, _):
        """Increment number of arguments calling"""
        self.arg_count[-1] += 1

    def action_pcount(self, _):
        """Pushes 0 as count of args

        NOTE: I think having a queue to keep number of arguments will help us
        to handle recursive and multiple function calls (i.e. f(g(), h(a))"""
        self.arg_count.append(0)

    def action_index(self, _):
        """Index an array in a temp var

        This uses indirect addressing mode to create address of the index in
        runtime and access it."""
        t = self.get_temp()
        self.pb[self.i] = MUL(self.ss[TOP], "#4", str(t))
        self.pb[self.i + 1] = ADD(str(t), f"#{self.ss[TOP-1]}", str(t))
        self.i += 2
        self.pop(2)
        self.push(f"@{t}")
