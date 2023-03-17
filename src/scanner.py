from util.buffer import AllBuffer
from util.cminus import CMinus
from util.types_ import TokenType, ErrorType, KEYWORDS, SymbolTable
from typing import Tuple


class Scanner:
    """Scanner (Lexer)

    This module will use Buffer and Dfa of the language to get tokens.
    """

    def __init__(self, log=False, buffer=None, file=None) -> None:
        self.dfa = CMinus.get_language()
        if buffer:
            self.buf = buffer
        elif file:
            self.buf = AllBuffer(file=file)
        else:
            self.buf = AllBuffer()
        self.log = log
        self.symbol_table = SymbolTable()

    def get_token(self) -> Tuple[TokenType, str]:
        """returns next token

        This function will try to get the next token type with usage of the Dfa
        and its lexim. If a lexical error happened, error type and problematic
        lexim will be returned.
        """
        try:
            tok, ret = self.dfa.match(self.buf)
            lexim = self.buf.extract_retreat() if ret else self.buf.extract()
            if tok == TokenType.ID:
                if lexim in KEYWORDS:
                    tok = TokenType.KEYWORD
                else:
                    self.symbol_table.install(lexim)
            return tok, lexim
        except ValueError as e:
            return self.panic(e)

    def get_next_token(self):
        """Get Next Token

        This function will call get_token function until it receives a valuable
        token (COMMENT and WHITESPACE tokens will be ignored). 

        NOTE: Logging is done inside this function.
        """
        while True:
            cur_line_no = self.buf.lineno
            tt, lexim = self.get_token()
            if tt in ErrorType:
                # TODO: logging
                pass
            elif tt in TokenType:
                if tt in [TokenType.COMMENT, TokenType.WHITESPACE]:
                    continue
                else:
                    # TODO: logging
                    return tt, lexim
            else:
                raise TypeError(f'Invalid Type [{tt}]')

    def panic(self, e: ValueError):
        """Panic Mode

        This function will handle discarding of the input buffer.
        """
        err_lexim = self.buf.extract()
        return e.args[0], err_lexim
