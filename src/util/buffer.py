class Buffer:
    """Abstract Buffer class

    This buffer class will handle reading files and buffering the input.

    Buffer can be responsible for line number as adding it to DFAs can cause
    DOOSHVARI in comment and whitespace.
    """

    def __call__(self, *args, **kwds) -> str:
        """returns char at the current forward position

        this function will allow buffer to be a callable and when it is called
        it should return the character at the current position or None if we
        reach EOF.
        """
        raise NotImplementedError()

    def __init__(self, file="input.txt") -> None:
        """initializes the abstract buffer

        Initialization consist of opening the specified file. If the read method
        (i.e. 'r') should be overwritten, then child class must provide None as
        file and open the file itself.

        Args:
            file (str, required): Name of the file to be buffered. Defaults to 
            "input.txt".
        """
        if file:
            self.f = open(file)

    def step(self) -> None:
        """step will move the `forward` pointer one step ahead

        In case of EOF it will not move the forward pointer.
        """
        raise NotImplementedError()

    def extract(self) -> str:
        """extract the token

        calling this function will cause the buffer to return the string from
        [beginning, forward] and set both pointers to the next character.

        This function can be used for getting lexim of accepted tokens or in
        case of panic, it could be used to discard the input.

        This function should maintain lineno.
        """
        raise NotImplementedError()

    def extract_retreat(self) -> str:
        """extract and take one step back

        calling this function will cause the buffer to return the string from
        [beginning, forward) and set both pointers to the current character.

        This option can be used in the dfa states that uses `other` option.

        This function should maintain lineno.
        """
        raise NotImplementedError()

    def get_lineno(self) -> int:
        """returns line number of the `beginning` pointer that is in it.

        This function can be used by the scanner before calling match to keep
        the line number of the tokens.

        Returns:
            int: lineno of `beginning` pointer.
        """
        raise NotImplementedError()
