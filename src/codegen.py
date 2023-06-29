from collections import deque
from util import *
TOP = -1

VOID_RETURN = SemanticSymbol("VOID RETURN", SymbolType.VOID, 4)
START_STACK = 500


class CodeGenerator:
    def __init__(self) -> None:
        self.symbol_table = SymbolTable()
        self.pb = [None] * 200
        self.i = 0
        self.ss = deque()
        self.arg_count = deque()
        self.break_stack = deque()
        self.semantic_errors = []
        self.CF = 200
        self.SP = 204
        self.temp = 208
        self.current_function_return_points = []
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
        self.current_function_return_points = []
        symbol_type = SymbolType[self.ss[TOP-1].upper()]
        self.symbol_table.install_func(self.ss[TOP], symbol_type, self.i)
        self.pop(2)
        ct = self.get_conversion_temp()
        self.pb[self.i] = ADD("#8", f"{self.SP}", f"{ct}")
        self.pb[self.i + 1] = ASSIGN(f"{self.SP}", f"@{ct}")
        self.pb[self.i + 2] = ADD("#12", f"{self.SP}", f"{ct}")
        self.pb[self.i + 3] = ASSIGN(f"{self.CF}", f"@{ct}")
        self.pb[self.i + 4] = ASSIGN(f"{self.SP}", f"{self.CF}")
        self.push(self.i + 5)  # Save an space for Adding current AR to SP
        self.i += 6

    def action_func_end(self, _):
        """Tells symbol table that current function is done"""
        ar = self.symbol_table.get_current_ar()
        # Back Patch Caller start routine
        self.pb[self.ss[TOP]] = ADD(f"#{len(ar)}", f"{self.SP}", f"{self.SP}")
        # Back Patch Return Points
        for rp in self.current_function_return_points:
            self.pb[rp] = JP(f"{self.i}")
        # POP AR -> SP is RESTORED
        self.pb[self.i] = SUB(f'{self.SP}', f'#{len(ar)}', f'{self.SP}')
        # RESTORE CF
        ct = self.get_conversion_temp()
        self.pb[self.i + 1] = ADD(f"#{ar.pcf}", f"{self.SP}", f"{ct}")
        self.pb[self.i + 2] = ASSIGN(f'@{ct}', f'{self.CF}')
        # Jump to Return Address
        self.pb[self.i + 3] = ADD(f"#{ar.ra}", f"{self.SP}", f"{ct}")
        self.pb[self.i + 4] = JP(f'@{ct}')
        self.i += 5
        self.symbol_table.end_func()
        self.pop(1)

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

        # Its assumed that semantic checks has been done before this comment
        # And two operands are integers and result will be a new temp from
        # symbol table
        t = self.symbol_table.get_temp()
        res_ct, adds = self.symbol2ct(self.i, t)
        self.i += adds
        op1_ct, adds = self.symbol2ct(self.i, self.ss[TOP-2])
        self.i += adds
        op2_ct, adds = self.symbol2ct(self.i, self.ss[TOP])
        self.i += adds
        self.pb[self.i] = operation[self.ss[TOP - 1]](
            op1_ct,
            op2_ct,
            res_ct)
        self.i += 1
        self.pop(3)
        self.push(t)

    def action_pop(self, lookahead: Lookahead):
        """Push operator into SS"""
        self.push(lookahead.lexeme)

    def symbol2ct(self, i, s: SemanticSymbol):
        """Convert Semantic Symbol to lines of code starting from i

        Returns:
            str: something that can be used as operand
            int: lines of code used to generate operand
        """
        if s.is_constant:
            return f"#{s.value}", 0

        if s.is_global and s.type == SymbolType.INT:
            return f"{s.value}", 0

        if not s.is_global and s.type == SymbolType.INT:
            # we have indirect int / temp
            ct = self.get_conversion_temp()
            self.pb[i] = ADD(f"{self.CF}", f"#{s.value}", f"{ct}")
            return f"@{ct}", 1

        if s.type == SymbolType.INDEXED:
            ct = self.get_conversion_temp()
            self.pb[i] = ADD(f"{self.CF}", f"#{s.value}", f"{ct}")
            self.pb[i + 1] = ASSIGN(f"@{ct}", f"{ct}")
            return f"@{ct}", 2

        return None, 0  # Will produce error if it's used

    def action_ret_val(self, _):
        """Assigns the temp variable pushed into semantic stack to the RV field
        of AR. Return statements will be generated later"""
        ct, addition = self.symbol2ct(self.i, self.ss.pop())
        self.i += addition
        self.pb[self.i] = ASSIGN(ct, f"@{self.CF}")
        self.i += 1

    def action_return(self, _):
        """Pushes a saved return point"""
        self.current_function_return_points.append(self.i)
        self.i += 1

    def push_int_arg(self, arg, ct_rt):
        ct_arg, add = self.symbol2ct(arg, self.i)
        self.i += add
        self.pb[self.i] = ASSIGN(ct_arg, f"@{ct_rt}")
        self.i += 1

    def push_global_array_arg(self, arg, ct_rt):
        self.pb[self.i] = ASSIGN(f"#{arg.value}", f"@{ct_rt}")
        self.i += 1

    def push_local_array_arg(self, arg: SemanticSymbol, ct_rt):
        ct_address = self.get_conversion_temp()
        self.pb[self.i] = ADD(f"{self.CF}", f"#{arg.value}", f"{ct_address}")
        self.pb[self.i + 1] = ASSIGN(f"{ct_address}", ct_rt)
        self.i += 2

    def push_local_pointer_arg(self, arg, ct_rt):
        ct_address = self.get_conversion_temp()
        self.pb[self.i] = ADD(f"{self.CF}", f"#{arg.value}", f"{ct_address}")
        self.pb[self.i + 1] = ASSIGN(f"@{ct_address}", ct_rt)
        self.i += 2

    def push_pointer_arg(self, arg, ct_rt):
        if arg.type == SymbolType.ARRAY_INT and arg.is_global:
            self.push_global_array_arg(arg, ct_rt)
        elif arg.type == SymbolType.ARRAY_INT:
            self.push_local_array_arg(arg, ct_rt)
        elif arg.type == SymbolType.POINTER_INT:
            self.push_local_pointer_arg(arg, ct_rt)
        else:
            pass  # semantic error

    def push_arguments(self, arg_types):
        """This will pop args from ss and assign it to stack respectively

        NOTE: This should push to rt stack without changing sp itself.
        """
        num_args = len(arg_types)
        args = self.ss[TOP - num_args:]
        for i, arg, type in enumerate(zip(args, arg_types)):
            ct_rt = self.get_conversion_temp()
            self.pb[self.i] = ADD(f"{self.SP}", f"#{16 + i * 4}", f"{ct_rt}")
            self.i += 1
            if type == SymbolType.INT:
                self.push_int_arg(arg, ct_rt)
            elif type == SymbolType.POINTER_INT:
                self.push_pointer_arg(arg, ct_rt)
            else:
                pass  # semantic error (we cannot have any other types)
        self.pop(num_args)

    def action_call(self, _):
        """Call the function inside SS with number of its arguments

        Tasks:
            - Push Args to the rt stack
                - Ints are assigned directly
                - Pointers needs special care
            - Push Return Address (RA) to rt stack
            - Copy return value to a temp

        NOTE: Semantic checks does not apply in this section
        """
        num_arg = self.arg_count.pop()
        func = self.ss[TOP - num_arg]
        arg_types = func.args
        if func.name == 'output':
            self.generate_output()  # this also should push return value to ss
            return
        self.push_arguments(arg_types)
        ct = self.get_conversion_temp()
        # Push return address
        self.pb[self.i] = ADD(f"{self.SP}", f"#{4}", f"{ct}")
        self.pb[self.i + 1] = ASSIGN(f"{self.i + 3}", f"@{ct}")
        # Jump to function
        self.pb[self.i + 2] = JP(f"{func.value}")
        self.i += 3
        # Assign  return value
        rv = None
        if func.type == SymbolType.INT:
            rv = self.symbol_table.get_temp()
            ct_rv, add = self.symbol2ct(self.i, rv)
            self.i += add
            self.pb[self.i] = ASSIGN(f"@{self.SP}", ct_rv)
            self.i += 1
        else:
            # void return type
            rv = VOID_RETURN
        self.pop(1)  # pop func from ss
        self.push(rv)

    def code_output(self):
        ct, add = self.symbol2ct(self.i, self.ss[TOP])
        self.i += add
        self.pb[self.i] = PRINT(ct)
        self.i += 1
        self.pop(2)
        self.push(VOID_RETURN)

    def action_incarg(self, _):
        """Increment number of arguments calling"""
        self.arg_count[-1] += 1

    def action_pcount(self, _):
        """Pushes 0 as count of args

        NOTE: I think having a queue to keep number of arguments will help us
        to handle recursive and multiple function calls (i.e. f(g(), h(a))"""
        self.arg_count.append(0)

    def index_global_array(self, id: SemanticSymbol, index_ct):
        ct1 = self.get_conversion_temp()
        ct2 = self.get_conversion_temp()
        indexed = self.symbol_table.get_temp(is_indexed=True)
        self.pb[self.i] = ADD(f"{id.value}", index_ct, f"{ct1}")
        self.pb[self.i + 1] = ADD(f"{self.CF}", f"#{indexed.value}", f"{ct2}")
        self.pb[self.i + 2] = ASSIGN(f"{ct1}", f"@{ct2}")
        self.push(indexed)
        self.i += 3

    def index_local_array(self, id: SemanticSymbol, index_ct):
        ct1 = self.get_conversion_temp()
        ct2 = self.get_conversion_temp()
        indexed = self.symbol_table.get_temp(is_indexed=True)
        self.pb[self.i] = ADD(f"{self.CF}", f"#{id.value}", f"{ct1}")
        self.pb[self.i + 1] = ADD(f"@{ct1}", index_ct, f"{ct1}")
        self.pb[self.i + 2] = ADD(f"{self.CF}", f"#{indexed.value}", f"{ct2}")
        self.pb[self.i + 3] = ASSIGN(f"{ct1}", f"@{ct2}")
        self.push(indexed)
        self.i += 4

    def index_local_pointer(self, id: SemanticSymbol, index_ct):
        ct1 = self.get_conversion_temp()
        ct2 = self.get_conversion_temp()
        indexed = self.symbol_table.get_temp(is_indexed=True)
        self.pb[self.i] = ADD(f"{self.CF}", f"#{id.value}", f"{ct1}")
        self.pb[self.i + 1] = ADD(f"@{ct1}", index_ct, f"{ct1}")
        self.pb[self.i + 2] = ADD(f"{self.CF}", f"#{indexed.value}", f"{ct2}")
        self.pb[self.i + 3] = ASSIGN(f"@{ct1}", f"@{ct2}")
        self.push(indexed)
        self.i += 4

    def action_index(self, _):
        """Create an indexed temp variable and pushes it into stack"""
        index = self.ss[TOP]  # is a local variable as it's an expression
        index_ct, add = self.symbol2ct(self.i, index)
        self.i += add
        self.pb[self.i] = MUL(index_ct, "#4", index_ct)
        id = self.ss[TOP - 1]  # May be global/local array or a local pointer
        if id.type == SymbolType.ARRAY_INT and id.is_global:
            self.index_global_array(id, index_ct)
        elif id.type == SymbolType.ARRAY_INT:
            self.index_local_array(id, index_ct)
        elif id.type == SymbolType.POINTER_INT:
            self.index_local_pointer(id, index_ct)
        else:
            pass  # semantic error (we cannot index other types)
        self.pop(2)

    def action_save(self, _):
        """Saves a space in PB and pushes i into SS"""
        self.push(self.i)
        self.i += 1

    def action_jpf_save(self, _):
        """JPF and Save

        Saves an space in the PB and fill previous saved space with JPF:

        STACK:

        *
        * saved space i + 1 (actual JPF)
        * saved space i (evaluate expr temp)
        * expr result
        """
        eval_space = self.ss[TOP - 1]
        expr = self.ss[TOP-2]
        ct, add = self.symbol2ct(eval_space, expr)
        assert add == 1
        self.pb[self.ss[TOP]] = JPF(ct, str(self.i + 1))
        self.pop(3)
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
        ct, add = self.symbol2ct(self.i, self.ss[TOP])
        self.i += add
        self.pb[self.i] = JPF(ct, str(self.ss[TOP-1]))
        self.i += 1
        self.pop(2)

    def action_constant(self, lookahead):
        """Assigns num constant to a new temp"""
        num = lookahead.lexeme
        t = self.symbol_table.get_temp()
        ct, adds = self.symbol2ct(self.i, t)
        self.i += adds
        self.pb[self.i] = ASSIGN("#" + num, ct)
        self.i += 1
        self.push(t)

    def action_2temp(self, _):
        """Assigns current in the semantic stack to a new temp"""
        id = self.ss[TOP]
        self.pop()
        t = self.symbol_table.get_temp()
        ct, adds = self.symbol2ct(self.i, t)
        self.i += adds
        ct2, adds = self.symbol2ct(self.i, id)
        self.i += adds
        self.pb[self.i] = ASSIGN(ct2, ct)
        self.i += 1
        self.push(t)

    def action_pbp(self, _):
        """Push breakpoint

        pushes a temp variable that should be in break_stack so break use it
        as a jump point."""
        self.break_stack.append([])

    def action_until(self, _):
        """BackPatch all breakpoints"""
        for bp in self.break_stack.pop():
            self.pb[bp] = JP(f'{self.i}')

    def action_break(self, _):
        """break expression action"""
        self.break_stack[TOP].append(self.i)  # add label
        self.i += 1  # save space for back-patching

    def action_init(self, _):
        self.pb[0] = ASSIGN(f"#{START_STACK}", f"{self.SP}")
        self.pb[1] = ASSIGN(f"#{START_STACK}", f"{self.CF}")
        self.i = 4  # save two space for main action

    def action_main(self, _):
        # Assign return address for main
        self.pb[2] = ASSIGN(f"#{self.i}", "504")
        main = self.symbol_table.get_by_id("main")
        self.pb[3] = JP(f"#{main.value}")
