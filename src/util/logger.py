from typing import Tuple

from typing import Dict

from src.util.types_ import TokenType, ErrorType


class Logger:
    Token = Tuple[TokenType, str]

    # self.tokens = {1: [(TokenType.KEYWORD, "void"), (TokenType.ID, "main"), (TokenType.SYMBOL, "("),
    #               (TokenType.KEYWORD, "void"), (TokenType.SYMBOL, ")"), (TokenType.SYMBOL, "{")],
    #           2: [(TokenType.KEYWORD, "int"), (TokenType.ID, "a"), (TokenType.SYMBOL, "="), (TokenType.NUM, "0"),
    #               (TokenType.SYMBOL, ";")]}
    #
    # self.errors = {7: ("3d", "Invalid number"),
    #           9: ("cd!", "Invalid input"),
    #           11: ("*/", "Unmatched comment"),
    #           14: ("@", "Invalid input"),
    #           16: ("/* comm...", "Unclosed comment")}
    #
    # self.symbol_table = {"break": [], "else": [], "if": []}
    def __init__(self):
        self.tokens = {}
        self.errors = {}

    def create_tokens_string(self, tokens: dict):
        tokens_string = ""
        for key in tokens.keys():
            line = ""
            for tup in tokens[key]:
                if str(tup[0]).split(".")[1] == "DOLOR":
                    continue
                line += "(" + str(tup[0]).split(".")[1] + ", " + tup[1] + ") "
            line += "\n"
            if line != "\n":
                tokens_string += str(key) + ".\t" + line
        return tokens_string

    def create_symbol_table_string(self, symbol_table: dict):
        symbol_table_string = ""
        symbols = list(symbol_table.keys())
        for i in range(len(symbols)):
            symbol_table_string += str(i + 1) + ".\t" + symbols[i] + "\n"
        return symbol_table_string

    def create_errors_string(self, errors):
        errors_string = ""
        for key in errors.keys():
            line = str(key) + ".\t"
            tt = errors[key][1]
            error_type = ""

            if str(tt).split(".")[1] == "INVALID_INPUT":
                error_type = "Invalid input"
            elif str(tt).split(".")[1] == "INVALID_NUMBER":
                error_type = "Invalid number"
            elif str(tt).split(".")[1] == "UNCLOSED_COMMENT":
                error_type = "Unclosed comment"
            elif str(tt).split(".")[1] == "UNMATCHED_COMMENT":
                error_type = "Unmatched comment"

            line += "(" + errors[key][0] + ", " + error_type + ") "

            line += "\n"
            errors_string += line
        if errors_string == "":
            return "There is no lexical error."
        return errors_string

    def save_as_text(self, string: str, file_name=None, file=None):
        if file_name != None:
            f = open(file_name, "w")
            f.write(string)
            f.close()
        else:
            file.write(string)
            file.close()

    def create_log(self, symbol_table, file_tokens=None, file_errors=None, file_symbols=None):
        if file_symbols == None:
            self.save_as_text(self.create_errors_string(self.errors), file_name="lexical_errors.txt")
            self.save_as_text(self.create_tokens_string(self.tokens), file_name="tokens.txt")
            self.save_as_text(self.create_symbol_table_string(symbol_table), file_name="symbol_table.txt")
        else:
            self.save_as_text(self.create_errors_string(self.errors), file=file_errors)
            self.save_as_text(self.create_tokens_string(self.tokens), file=file_tokens)
            self.save_as_text(self.create_symbol_table_string(symbol_table), file=file_symbols)

    def add_error(self, cur_line_no, lexim, tt):
        if len(lexim) > 6:
            self.errors[cur_line_no] = (lexim[:7] + "...", tt)
        else:
            self.errors[cur_line_no] = (lexim, tt)

    def add_token(self, cur_line_no, lexim, tt):
        if cur_line_no in self.tokens.keys():
            self.tokens[cur_line_no].append((tt, lexim))
        else:
            self.tokens[cur_line_no] = [(tt, lexim)]
