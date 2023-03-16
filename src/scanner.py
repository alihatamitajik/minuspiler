from util.buffer import AllBuffer
from util.cminus import CMinus


class Scanner:
    """Scanner (Lexer)

    This module will use Buffer and Dfa of the language to get tokens.
    """

    def __init__(self) -> None:
        self.dfa = CMinus.get_language()
        self.buf = AllBuffer()

    def get_token(self):
        """returns next token

        This function will try to get the next token type with usage of the Dfa
        and 
        """
        cur_lineno = self.buf.get_lineno()
        try:
            token_type, is_retreat = self.dfa.match(self.buf)
            # TODO: log token
            lexim = self.buf.extract()
            # TODO: return Token
        except ValueError as e:
            self.panic(e)
        except e:
            # handle general errors
            pass

    def panic(self, e: ValueError):
        """Panic Mode

        This function will handle discarding of the input buffer and logging the
        exception. TODO
        """
        pass
