from util.cminus import GRAMMAR
from scanner import Scanner


class Parser:
    """Parser of CMinus

    This parser is using Transition Diagram Model.
    """

    def __init__(self, scanner: Scanner) -> None:
        """
        TODO: add logger to the parser
        """
        self.scanner = scanner

    def match(self, terminal):
        """Accepts a terminal

        Accepts a terminal, add it to the parse tree and get the next token as
        the lookahead.
        """
        pass

    def transit(self, diagram='Program'):
        """Executes the transition of `diagram`

        This function tries to match current lookahead token with current
        diagram."""
        pass

    def parse(self):
        """Generates Parse Tree and Syntax Errors"""
        self.lookahead = self.scanner.get_next_token()
        self.transit()
