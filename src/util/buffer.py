class Buffer:
    """Abstract Buffer class

    This buffer class will handle reading files and buffering the input.

    Buffer can be responsible for line number as adding it to DFAs can cause
    DOOSHVARI in comment and whitespace.
    """

    def __call__(self, *args, **kwds) -> str:
        """returns char at the current forward position

        this function will allow buffer to be a callable and when it is called
        it should return the character at the current position or \x05 if we
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

    def close(self):
        """Closes the buffer and removes allocated data"""
        self.f.close()

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


class AllBuffer(Buffer):
    """Dummy Buffer

    This Buffer class opens the file and read the whole file. It keep pointers
    with their real index in the original file and no literal buffering is done.
    This class should be implemented so we ensure the main part of the scanner
    works. An appropriate buffer will be implemented later.

    TODO: this implementation is not tested and can be buggy AF.
    """

    def __call__(self, *args, **kwds) -> str:
        if self.forward == len(self.file):
            return '\x05'
        else:
            return self.file[self.forward]

    def __init__(self, file="input.txt", fake=None) -> None:
        if not fake:
            super().__init__(file)
            self.file = self.f.read()
        else:
            self.file = fake
        self.beginning = 0
        self.forward = 0
        self.lineno = 1

    def close(self):
        super().close()
        del self.file

    def step(self) -> None:
        self.forward = min(len(self.file), self.forward + 1)
        if self.__call__() == '\n':
            self.lineno += 1

    def extract(self) -> str:
        retval = self.file[self.beginning:self.forward+1]
        self.step
        self.beginning = self.forward
        return retval

    def extract_retreat(self) -> str:
        retval = self.file[self.beginning:self.forward]
        self.beginning = self.forward
        return retval

    def get_lineno(self) -> int:
        return self.lineno
