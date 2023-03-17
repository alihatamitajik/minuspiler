from typing import Tuple

from typing import Dict

from util.types_ import TokenType, ErrorType


class Logger:
    Token = Tuple[TokenType, str]

    def __init__(self):
        """Logger Init

        Creates two dictionaries for keeping tokens and errors.

        Dictionaries Example:
        self.tokens = {1: [(TokenType.KEYWORD, "void"), (TokenType.ID, "main"), 
                           (TokenType.SYMBOL, "("), (TokenType.KEYWORD, "void"), 
                           (TokenType.SYMBOL, ")"), (TokenType.SYMBOL, "{")],
                       2: [(TokenType.KEYWORD, "int"), (TokenType.ID, "a"), 
                           (TokenType.SYMBOL, "="), (TokenType.NUM, "0"),
                           (TokenType.SYMBOL, ";")]}

        self.errors = {
                    7: ("3d", "Invalid number"),
                    9: ("cd!", "Invalid input"),
                    11: ("*/", "Unmatched comment"),
                    14: ("@", "Invalid input"),
                    16: ("/* comm...", "Unclosed comment")}

        self.symbol_table = {
            "break": [], "else": [], "if": []}
        """
        self.tokens = {}
        self.errors = {}

    def create_string(self, token_dict):
        string = ""
        for key, item in token_dict.items():
            line = ""
            for entry0, entry1 in item:
                line += f"({entry0}, {entry1}) "
            line += "\n"
            if line != "\n":
                string += str(key) + ".\t" + line
        return string

    def create_tokens_string(self):
        return self.create_string(self.tokens)

    def create_symbol_table_string(self, symbol_table: dict):
        symbol_table_string = ""
        for i, entry in enumerate(symbol_table.keys()):
            symbol_table_string += f"{i + 1}.\t{entry}\n"
        return symbol_table_string

    def create_errors_string(self):
        errors_string = self.create_string(self.errors)
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

    def create_log(self, symbol_table, file_tokens=None, file_errors=None, file_symbols=None):
        if file_symbols == None:
            self.save_as_text(self.create_errors_string(),
                              file_name="lexical_errors.txt")
            self.save_as_text(self.create_tokens_string(),
                              file_name="tokens.txt")
            self.save_as_text(self.create_symbol_table_string(
                symbol_table), file_name="symbol_table.txt")
        else:
            self.save_as_text(self.create_errors_string(),
                              file=file_errors)
            self.save_as_text(self.create_tokens_string(),
                              file=file_tokens)
            self.save_as_text(self.create_symbol_table_string(
                symbol_table), file=file_symbols)

    def add_error(self, cur_line_no, lexim, tt):
        err = (lexim[:7] + "..." if len(lexim) > 6 else lexim, tt)
        if cur_line_no in self.errors:
            self.errors[cur_line_no].append(err)
        else:
            self.errors[cur_line_no] = [err]

    def add_token(self, cur_line_no, lexim, tt):
        if tt == TokenType.DOLOR:
            return
        if cur_line_no in self.tokens:
            self.tokens[cur_line_no].append((tt, lexim))
        else:
            self.tokens[cur_line_no] = [(tt, lexim)]
