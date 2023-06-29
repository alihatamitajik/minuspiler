from collections import deque
from util import *
TOP = -1


class CodeGenerator:
    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.pb = [None] * 100
        self.i = 0
        self.ss = deque()
        self.arg_count = deque()
        self.break_stack = deque()
        self.semantic_errors = []
        self.CF = 200
        self.SP = 204
        self.temp = 208
        # save 5 temp for each address in instructions (so next address is 224)
        # This value is used in symbol table init

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
        self.temp = 208  # reset conversion temp
        getattr(self, "action_" + action[1:])(lookahead)

    def get_conversion_temp(self):
        addr = self.temp
        self.temp += 4
        return addr

    def get_data(self, size=1):
        """returns address of data allocated in data block"""
        raise NotImplementedError("Should be handled inside symbol table")

    def get_temp(self):
        raise NotImplementedError("Should be connected to symbol table")

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
        symbol = self.symbol_table.get_by_id(lookahead.lexeme)
        self.push(symbol)

    def action_pnum(self, lookahead: Lookahead):
        """Pushes number in lookahead."""
        self.push(SemanticSymbol(None, SymbolType.INT,
                  int(lookahead.lexeme), is_constant=True))

    def action_var(self, _):
        """Registers variable

        And pops required data from semantic stack:
            - type
            - name
        """
        symbol_type = SymbolType[self.ss[TOP-1].upper()]
        self.symbol_table.install_variable(self.ss[TOP], symbol_type)
        self.pop(2)

    def action_func(self, _):
        """Adds function to the symbol table

        This also saves a space to offset the TOP after function ends

        NOTE: In time of calling a function, when we jumped into the callee
        (i.e. the codes are written in this section as first instruction of the
        function) The Runtime Stack looks like this:

        +---------------------------+ <- CF
        |       Caller Frame        |
        |                           |
        |                           |
        +---------------------------+ <- SP
        |       Return Value        |
        |       Return Address      |
        +---------------------------+

        And it's the task of callee to save TOP/TOP_SP and allocate space for
        its variables inside the stack.
        """
        symbol_type = SymbolType[self.ss[TOP-1].upper()]
        self.symbol_table.install_func(self.ss[TOP], symbol_type, self.i)
        self.pop(2)
        ct = self.get_conversion_temp()
        self.pb[self.i] = ADD("#8", f"{self.SP}", f"{ct}")
        self.pb[self.i + 1] = ASSIGN(f"{self.SP}", f"@{ct}")
        self.pb[self.i + 2] = ADD("#4", f"{ct}", f"{ct}")
        self.pb[self.i + 3] = ASSIGN(f"{self.CF}", f"@{ct}")
        self.pb[self.i + 4] = ASSIGN(f"{self.SP}", f"{self.CF}")
        self.push(self.i + 5)  # Save an space for Adding current AR to SP
        self.i += 6

    def action_func_end(self, _):
        """Tells symbol table that current function is done"""
        self.symbol_table.end_func()
        # TODO: We should fill the start of function with size of the AR for SP
        # TODO: Also Callee Code for returning
        # This Code Includes:
        #   1. POP AR
        #   2. Restore CF and SP
        #   3. Jump to Return Address

    def action_arr(self, _):
        """Registers array variable

        And pops required data from semantic stack:
            - type
            - name
            - num (size of array)
        """
        size = self.ss[TOP].value
        symbol_type = SymbolType["ARRAY_" + self.ss[TOP - 2].upper()]
        self.symbol_table.install_array(self.ss[TOP-1], symbol_type, size)
        self.pop(3)

    def action_par_ptr(self, _):
        """Adds pointer parameter to the function"""
        symbol_type = SymbolType["POINTER_" + self.ss[TOP - 1].upper()]
        self.symbol_table.add_arg_to_func(self.ss[TOP], symbol_type)
        self.pop(2)

    def action_par_var(self, _):
        """Adds variable parameter to the function"""
        symbol_type = SymbolType[self.ss[TOP - 1].upper()]
        self.symbol_table.add_arg_to_func(self.ss[TOP], symbol_type)
        self.pop(2)

    def action_scope_up(self, _):
        """Add one scope to the symbol table"""
        self.symbol_table.scope_up()

    def action_scope_down(self, _):
        """Remove top level scope from stack (its ids can't be used later)"""
        self.symbol_table.scope_down()

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
        # TODO: Whole Function needs fundamental changes
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

    def action_save(self, _):
        """Saves a space in PB and pushes i into SS"""
        self.push(self.i)
        self.i += 1

    def action_jpf_save(self, _):
        """JPF and Save

        Saves an space in the PB and fill previous saved space with JPF:

        STACK:

        *
        *
        * saved space
        * expr result
        """
        self.pb[self.ss[TOP]] = JPF(self.ss[TOP-1], str(self.i + 1))
        self.pop(2)
        self.action_save(_)

    def action_jp(self, _):
        """JP in saved space to current line

        STACK:

        *
        *
        * saved space
        """
        self.pb[self.ss[TOP]] = JP(str(self.i))
        self.pop(1)

    def action_label(self, _):
        """label current line"""
        self.push(self.i)

    def action_jpf(self, _):
        """JPf to label with expr in SS

        STACK:

        *
        *
        * expr result
        * saved space
        """
        self.pb[self.i] = JPF(self.ss[TOP], str(
            self.ss[TOP-1]))  # DONNO HOW TO
        # HANDLE CALCULATE THIS SS[TOP]
        # IDEA : EVEN ASSIGN CONSTANTS TO A TEMP SO ALL OF EXPRESSION REFERENCES
        # ARE TO A TEMP VARIABLE THAT SHOULD BE CALCULATED WITH A DEFINITE
        # NUMBER OF CALCULATIONS
        self.i += 1
        self.pop(2)

    def action_pbp(self, _):
        """Push breakpoint

        pushes a temp variable that should be in break_stack so break use it
        as a jump point."""
        t = self.get_temp()  # TODO: global temp should be used (not recursive and is a simple address)
        self.break_stack.append(t)

    def action_until(self, _):
        """fill the saved space with address of break point and pop breakpoint
        from stack."""
        self.pb[self.ss[TOP]] = ASSIGN(
            f"#{self.i}", str(self.break_stack.pop()))
        self.pop(1)

    def action_break(self, _):
        """break expression action"""
        self.pb[self.i] = JP(f"@{self.break_stack[TOP]}")
        self.i += 1
