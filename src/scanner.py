from util.types_ import TokenType
from util.buffer import AllBuffer


class Dfa:
    """Dfa class

    This class will accepts token types of the language. If none is detected,
    an error will be raised. Also if a type is matched partially but not
    completely, it will raise an error as soon as the first bad input.

    C-Minus token has no ambiguity and can be detected/discarded in one pass and
    no recursion is needed in the scanner. DFA object can be interpreted as
    state 0 in the DFA found in the WA1. This class is constructed with <entry,
    tail> pairs. DFA checks current input in the Buffer with entry points and
    step the buffer and call `match` on the tail. If no match is found it will
    raise an error. NOTE that dfa object does not extract from the buffer.

    SEE DfaTail class.
    """

    def __init__(self, tails) -> None:
        """initializes a DFA

        Args:
            tails (List[Tuple[str, DfaTail]]): list of tails. DFA object will
            match the entry points in the order of the list specified to it.
        """
        self.tails = tails

    def __call__(self, *args, **kwds) -> TokenType:
        """dfa(buffer) is equivalent of dfa.match(buffer)"""
        self.match(args[0])

    def match(self, buffer) -> TokenType:
        """accepts input

        This function will check the first input in the buffer and test it with
        entrypoint DFA initialized with. If no entrypoint is ok, it will raise
        an error.

        Args:
            buffer (Buffer): buffer to be accepted

        Raises:
            ValueError: If it cannot accept the input it would raise a value
            error. The error message will be important as it will be used in
            panic mode.

        Returns:
            TokenType: type of the token found
        """
        c = buffer()
        for entry, tail in self.tails:
            if c in entry:
                buffer.step()
                tail.match(buffer)
        raise ValueError('Invalid Input')