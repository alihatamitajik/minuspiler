from typing import Tuple
from types_ import TokenType

Token = Tuple[TokenType, str]

tokens = {1: [(TokenType.KEYWORD, "void"), (TokenType.ID, "main"), (TokenType.SYMBOL, "("),
              (TokenType.KEYWORD, "void"), (TokenType.SYMBOL, ")"), (TokenType.SYMBOL, "{")],
          2: [(TokenType.KEYWORD, "int"), (TokenType.ID, "a"), (TokenType.SYMBOL, "="), (TokenType.NUM, "0"),
              (TokenType.SYMBOL, ";")]}

errors = {7: ("3d", "Invalid number"),
         9: ("cd!", "Invalid input"),
         11: ("*/", "Unmatched comment"),
         14: ("@", "Invalid input"),
         16: ("/* comm...", "Unclosed comment")}

symbol_table = {"break": [], "else":[], "if":[]}

def create_tokens_string(tokens: dict):
    tokens_string = ""
    for key in tokens.keys():
        line = str(key) + ".\t"
        for tup in tokens[key]:
            line += "(" + str(tup[0]).split(".")[1] + ", " + tup[1] + ") "
        line += "\n"
        tokens_string += line
    return tokens_string


def create_symbol_table_string(symbol_table: dict):
    symbol_table_string = ""
    symbols = list(symbol_table.keys())
    for i in range(len(symbols)):
        symbol_table_string += str(i+1) + ".\t" + symbols[i] + "\n"
    return symbol_table_string

def create_errors_string(errors: {str, str}):
    errors_string = ""
    for key in errors.keys():
        line = str(key) + ".\t"
        line += "(" + errors[key][0] + ", " + errors[key][1] + ") "
        line += "\n"
        errors_string += line
    return errors_string


def save_as_text(string: str, file_name: str):
    f = open(file_name + ".txt", "w")
    f.write(string)
    f.close()


save_as_text(create_errors_string(errors), "lexical_errors")
save_as_text(create_tokens_string(tokens), "tokens")
save_as_text(create_symbol_table_string(symbol_table), "symbol_table")
