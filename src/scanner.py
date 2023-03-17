from util.buffer import AllBuffer
from util.cminus import CMinus
from util.types_ import TokenType, ErrorType, KEYWORDS, SymbolTable
from typing import Tuple
from util.logger import Logger


class Scanner:
    """Scanner (Lexer)

    This module will use Buffer and Dfa of the language to get tokens.
    """

    def __init__(self, buffer=None, file=None) -> None:
        self.dfa = CMinus.get_language()
        if buffer:
            self.buf = buffer
        elif file:
            self.buf = AllBuffer(file=file)
        else:
            self.buf = AllBuffer()
        self.symbol_table = SymbolTable()
        self.logger = Logger()

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
                self.logger.add_error(cur_line_no, str(lexim), tt)
                pass
            elif tt in TokenType:
                if tt in [TokenType.COMMENT, TokenType.WHITESPACE]:
                    continue
                else:
                    self.logger.add_token(cur_line_no, str(lexim), tt)
                    return tt, lexim
            else:
                raise TypeError(f'Invalid Type [{tt}]')

    def panic(self, e: ValueError):
        """Panic Mode

        This function will handle discarding of the input buffer.
        """
        err_lexim = self.buf.extract()
        return e.args[0], err_lexim

    @property
    def iterator(self):
        """Generator of tokens

        Yields:
            TokenType: type of the lexim returned
            str: lexim of the token
        """
        tt = TokenType.WHITESPACE
        while tt != TokenType.DOLOR:
            tt, lexim = self.get_next_token()
            yield tt, lexim

    def iterate_ignore(self):
        """Iterates through tokens and ignore tokens

        This function will iterate through the input file and build logger
        dictionaries only.
        """
        for _, _ in self.iterator:
            pass

    def finish(self, file_tokens=None, file_errors=None, file_symbols=None):
        self.logger.create_log(self.symbol_table.table,
                               file_tokens, file_errors, file_symbols)
