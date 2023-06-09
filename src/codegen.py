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
        self.func_addr = 3000
        self.arg_count = deque()
        self.break_stack = deque()
        self.semantic_errors = []
        self.has_error = False
        self.in_repeat = False

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
            string = ""
            for error in self.semantic_errors:
                string += error + "\n"
            file.write(string)
            pass  # TODO: write semantic errors

    def pop(self, n):
        """Pops n items from semantic stack"""
        for _ in range(n):
            self.ss.pop()

    def pop_all(self):
        """Pops all items from semantic stack
        it's been used in function call in 3rd phase
        """
        self.ss.clear()

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

    def get_func_addr(self):
        self.func_addr += 4
        return self.func_addr - 4

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
        symbol = self.symbol_table.get_symbol_addr(lookahead.lexeme)
        if symbol.__class__ == KeyError:
            self.has_error = True
            error_string = str(symbol).replace("\"", "")
            self.semantic_errors.append(f"#{lookahead.lineno}: Semantic Error! {error_string}")
            self.push("500")
            return
        addr = symbol.address
        self.push(addr)

    def action_pnum(self, lookahead: Lookahead):
        """Pushes number in lookahead."""
        self.push(f"#{lookahead.lexeme}")

    def action_var(self, lookahead: Lookahead):
        """Registers variable

        And pops required data from semantic stack:
            - type
            - name
        """

        if self.ss[TOP - 1] == "void":
            self.has_error = True
            self.semantic_errors.append(
                f"#{lookahead.lineno}: Semantic Error! Illegal type of void for \'{self.ss[TOP]}\'.")

        self.symbol_table.install_var(self.ss[TOP],
                                      self.ss[TOP - 1],
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
        self.symbol_table.install_arr(self.ss[TOP - 1],
                                      self.ss[TOP - 2],
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

    def action_calc(self, lookahead: Lookahead):
        """Calculates operation inside SS on operands in SS"""
        t = self.get_temp()
        #  None -> void, >=500 -> int, <500, keyError -> not defined, # | @
        # F = a[0] + 1

        op1_symbol, op2_symbol = self.symbol_table.get_symbol_by_addr(
            self.ss[TOP - 2]), self.symbol_table.get_symbol_by_addr(self.ss[TOP])

        op1_type, op2_type = None, None

        if self.ss[TOP][0] == "#" or self.ss[TOP][0] == "@":
            op2_type = 'int'

        elif self.ss[TOP].isdecimal():
            if 3000 >= int(self.ss[TOP]) >= 500:
                op2_type = 'int'
            elif 500 > int(self.ss[TOP]) and op2_symbol.size != 0:
                op2_type = 'int[]'
            elif 500 > int(self.ss[TOP]) and op2_symbol.size == 0:
                op2_type = 'int'


        elif op2_symbol.__class__ != KeyError:
            op2_type = op2_symbol.s_type

        if self.ss[TOP - 2][0] == "#" or self.ss[TOP - 2][0] == "@":
            op1_type = 'int'
        elif self.ss[TOP - 2].isdecimal():
            if 3000 >= int(self.ss[TOP - 2]) >= 500:
                op1_type = 'int'
            elif 500 > int(self.ss[TOP - 2]) and op1_symbol.size != 0:
                op1_type = 'int[]'
            elif 500 > int(self.ss[TOP - 2]) and op1_symbol.size == 0:
                op1_type = 'int'

        elif op1_symbol.__class__ != KeyError:
            op1_type = op1_symbol.s_type

        if op1_type is None:
            self.has_error = True
            error_string = self.ss[TOP - 2].replace("\"", "")
            self.semantic_errors.append(
                f"#{lookahead.lineno}: Semantic Error! {error_string} is not defined.")

        elif op2_type is None:
            self.has_error = True
            error_string = self.ss[TOP - 2].replace("\"", "")
            self.semantic_errors.append(
                f"#{lookahead.lineno}: Semantic Error! {error_string} is not defined.")


        elif op1_type != 'int':
            self.has_error = True
            op1_type = op1_type if op1_type != 'int[]' else 'array'

            self.semantic_errors.append(
                f"#{lookahead.lineno}: Semantic Error! Type mismatch in operands, Got {op1_type} instead of int.")
        elif op2_type != 'int':
            self.has_error = True
            op2_type = op2_type if op2_type != 'int[]' else 'array'

            self.semantic_errors.append(
                f"#{lookahead.lineno}: Semantic Error! Type mismatch in operands, Got {op2_type} instead of int.")

        else:
            self.pb[self.i] = operation[self.ss[TOP - 1]](
                self.ss[TOP - 2],
                self.ss[TOP],
                str(t))
            self.i += 1
        self.pop(3)
        self.push(str(t))

    def action_pop(self, lookahead: Lookahead):
        """Push operator into SS"""
        self.push(lookahead.lexeme)

    def action_call(self, lookahead: Lookahead):
        """Call the function inside SS with number of its arguments

        NOTE: As the arguments are pushed inside the SS with Expression 
        non-terminal we don't need to push them, but some action may be needed 
        for semantic analysis in Args and arg related rules."""
        num_arg = self.arg_count.pop()

        symbol = self.symbol_table.get_symbol_by_addr(self.ss[TOP - num_arg])

        if symbol.lexeme == 'output':
            self.code_output()

        else:

            if symbol.__class__ == KeyError:
                self.has_error = True
                error_string = str(symbol).replace("\"", "")
                self.semantic_errors.append(f"#{lookahead.lineno}: Semantic Error! {error_string}")

            elif symbol.args is None or len(symbol.args) != num_arg:
                self.has_error = True

                self.semantic_errors.append(
                    f"#{lookahead.lineno}: Semantic Error! Mismatch in numbers of arguments of \'{symbol.lexeme}\'.")

            else:
                call_args = [self.ss[TOP + i] for i in range(num_arg)]
                true_args = symbol.args
                counter = 0
                for arg_type in true_args:
                    arg2 = self.symbol_table.get_symbol_by_addr(call_args[counter])

                    if call_args[counter][0] == "#" and arg_type == "int":
                        counter += 1
                        continue
                    elif call_args[counter][0] == "#" and arg_type == "int[]":
                        self.has_error = True
                        self.semantic_errors.append(
                            f"#{lookahead.lineno}: Semantic Error! Mismatch in type of argument {counter + 1} of \'{symbol.lexeme}\'. Expected 'array' but got 'int' instead.")
                        break
                    elif call_args[counter][0] == "@" and arg_type == "int[]":
                        counter += 1
                        continue
                    elif call_args[counter][0] == "@" and arg_type == "int":
                        self.has_error = True
                        self.semantic_errors.append(
                            f"#{lookahead.lineno}: Semantic Error! Mismatch in type of argument {counter + 1} of \'{symbol.lexeme}\'. Expected 'int' but got 'array' instead.")
                        break
                    elif arg2.__class__ == KeyError:
                        self.has_error = True
                        error_string = call_args[counter].replace("\"", "")
                        self.semantic_errors.append(
                            f"#{lookahead.lineno}: Semantic Error! {error_string} is not defined.")
                        break
                    elif arg_type != arg2.s_type:
                        self.has_error = True
                        arg_type = arg_type if arg_type != 'int[]' else 'array'
                        arg2_type = arg2.s_type if arg2.s_type != 'int[]' else 'array'

                        self.semantic_errors.append(
                            f"#{lookahead.lineno}: Semantic Error! Mismatch in type of argument {counter + 1} of \'{symbol.lexeme}\'. Expected {arg_type} but got {arg2_type} instead.")
                        break

        self.pop(num_arg + 1)  # pop arguments id of func
        # push return value (?) TODO: this is temp for return value of output

        if symbol.s_type == 'int':
            self.push("#500")
        elif symbol.s_type == 'int[]':
            self.push("@500")
        else:
            self.push(None)

    def code_output(self):
        self.pb[self.i] = PRINT(self.ss[TOP])
        self.i += 1

    def action_incarg(self, lookahead: Lookahead):
        """Increment number of arguments calling"""
        symbol = self.symbol_table.get_symbol_addr(lookahead.lexeme)

        if symbol.__class__ == KeyError and not lookahead.lexeme.isdecimal():
            self.has_error = True
            error_string = str(symbol).replace("\"", "")
            self.semantic_errors.append(f"#{lookahead.lineno}: Semantic Error! {error_string}")
            return
        self.arg_count[-1] += 1

    def action_pcount(self, lookahead: Lookahead):
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
        self.pb[self.i + 1] = ADD(str(t), f"#{self.ss[TOP - 1]}", str(t))
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
        self.pb[self.ss[TOP]] = JPF(self.ss[TOP - 1], str(self.i + 1))
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
        self.pb[self.i] = JPF(self.ss[TOP], str(self.ss[TOP - 1]))
        self.i += 1
        self.pop(2)

    def action_pbp(self, _):
        """Push breakpoint

        pushes a temp variable that should be in break_stack so break use it
        as a jump point."""
        t = self.get_temp()
        self.break_stack.append(t)
        self.in_repeat = True

    def action_until(self, _):
        """fill the saved space with address of break point and pop breakpoint
        from stack."""
        self.pb[self.ss[TOP]] = ASSIGN(
            f"#{self.i}", str(self.break_stack.pop()))
        self.pop(1)
        self.in_repeat = False

    def action_break(self, lookahead: Lookahead):
        """break expression action"""
        if not self.in_repeat:
            self.has_error = True
            self.semantic_errors.append(
                f"#{lookahead.lineno}: Semantic Error! No 'repeat ... until' found for 'break'.")
            return
        self.pb[self.i] = JP(f"@{self.break_stack[TOP]}")
        self.i += 1

    def action_func(self, lookahead: Lookahead):
        self.symbol_table.install_func(self.ss[TOP], self.ss[TOP - 1], str(self.get_func_addr()))
        id = self.ss[TOP]
        self.pop(2)
        self.push(id)

    def action_install_param_int(self, lookahead: Lookahead):
        self.symbol_table.install_var(self.ss[TOP], "int", str(self.get_data()))
        self.symbol_table.add_arg_func(self.ss[TOP - 2], 'int')
        self.pop(2)

    def action_install_param_arr(self, lookahead: Lookahead):
        self.symbol_table.install_arr(self.ss[TOP], "int", str(self.get_data()), "500")  # edit
        self.symbol_table.add_arg_func(self.ss[TOP - 2], "int[]")
        self.pop(2)

    def action_end_func(self, lookahead: Lookahead):
        pass

    def action_return_null(self, lookahead: Lookahead):
        pass

    def action_return_value(self, lookahead: Lookahead):
        result = self.ss[TOP]
        pass
