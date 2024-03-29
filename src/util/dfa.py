from util.types_ import *


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

    def __call__(self, *args, **kwds) -> Tuple[TokenType, bool]:
        """dfa(buffer) is equivalent of dfa.match(buffer)"""
        return self.match(args[0])

    def match(self, buffer) -> Tuple[TokenType, bool]:
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
            bool: if it should retreat or not
        """
        c = buffer()
        for entry, tail in self.tails:
            if c in entry:
                return tail.match(buffer)
        if c == '\x05':
            return TokenType.DOLOR, False
        raise ValueError(ErrorType.INVALID_INPUT)


class DfaTail:
    """Tail object

    Tail object is a DFA machine that will match the input from the second
    character (if needed) and returns token type of the input detected, or, it
    will raise an error if it cannot match the input (it is deterministically
    tell that the input cannot match any other types because input matched this
    entrypoint).

    `match` function will step the buffer until it raises an error or detects a
    type. NOTE that tails does not extract the input from buffer.
    """

    def match(self, buffer) -> Tuple[TokenType, bool]:
        """matches buffer inputs with specified dfa types.

        Args:
            buffer (Buffer): one of Buffer class implementations.

        Raises:
            NotImplementedError: This class should be implemented first and then
            be used. There will be two implementation: Automatic and Manual.
            Manual Implementation is for specific branches that cannot be
            automated easily.

            ValueError: If it cannot accept the input it would raise a value
            error. The error message will be important as it will be used in
            panic mode.

        Returns:
            TokenType: type of the token accepted
        """
        raise NotImplementedError()


class AutoTail(DfaTail):
    """Automatic Dfa Tail

    This class will accepts the inputs according to state list provided to its
    initializer and not hard coded (Manual). States passed to AutoTail as a list
    of `AutoTailState`s (see types_).
    """

    def __init__(self, states: List[AutoTailState], type: TokenType,
                 error: ErrorType = ErrorType.INVALID_INPUT) -> None:
        self.states = states
        self.type = type
        self.error = error

    def match(self, buffer) -> Tuple[TokenType, bool]:
        """Accepts the dfa

        Args:
            buffer (Buffer): input buffer

        Raises:
            ValueError: if cannot accept

        Returns:
            TokenType: token type of accepted input
            bool: if it should retreat or not
        """
        state_idx = 0
        state = self.states[state_idx]
        while not state.is_accepting:
            buffer.step()
            c = buffer()
            matched = False
            for t in state.transitions:
                if c in t.literal:
                    state_idx = t.next_state
                    matched = True
                    break
            if matched:
                state = self.states[state_idx]
            else:
                raise ValueError(self.error)

        if state.callback:
            return state.callback(), state.is_retreat
        else:
            return self.type, state.is_retreat
