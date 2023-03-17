from util.dfa import *
from util.types_ import classproperty
from util.types_ import *


class AsteriskTail(DfaTail):
    def match(self, buffer) -> Tuple[TokenType, bool]:
        c = buffer()
        if c == "/":
            raise ValueError(ErrorType.UNMATCHED_COMMENT)
        else:
            return TokenType.SYMBOL, True


class CommentTail(DfaTail):
    def match_end(self, buffer):
        state = 0
        while True:
            c = buffer()
            if c == EOT:
                raise ValueError(ErrorType.UNCLOSED_COMMENT)
            if state == 0 and c == "*":
                state = 1
            elif state == 1:
                if c == "/":
                    return TokenType.COMMENT, False
                elif c != "*":
                    state = 0
            buffer.step()

    def match(self, buffer) -> Tuple[TokenType, bool]:
        c = buffer()
        if c != "*":
            raise ValueError(ErrorType.INVALID_INPUT)
        else:
            buffer.step()  # "/*" is matched
            return self.match_end(buffer)


class CMinus:
    """Language

    A wrapper over language methods to get DFA of the language in a cleaner way.
    """
    @staticmethod
    def get_language() -> Dfa:
        return Dfa(
            [
                (W, CMinus.whitespace_tail()),
                (L, CMinus.id_keyword_tail()),
                (D, CMinus.num_tail()),
                (S, CMinus.symbol_tail()),
                ("=", CMinus.equals_tail()),
                ("*", CMinus.asterisk_tail()),
                ("/", CMinus.comment_tail())
            ]
        )

    @staticmethod
    def whitespace_tail() -> DfaTail:
        return AutoTail(
            [AutoTailState([], True, False)],
            TokenType.WHITESPACE
        )

    @staticmethod
    def id_keyword_tail() -> DfaTail:
        """ID/Keyword Tail

        NOTE: Get_Token and Install_Id should be called in the scanner itself
        """
        other = SPEC + W + EOT
        return AutoTail(
            [
                AutoTailState(
                    [
                        Transition(L+D, next_state=0),
                        Transition(other, next_state=1)
                    ]
                ),
                AutoTailState([], True, True)
            ],
            TokenType.ID
        )

    @staticmethod
    def num_tail() -> DfaTail:
        other = SPEC + W + EOT
        return AutoTail(
            [
                AutoTailState(
                    [
                        Transition(D, next_state=0),
                        Transition(other, next_state=1)
                    ]
                ),
                AutoTailState([], True, True)
            ],
            TokenType.NUM,
            ErrorType.INVALID_NUMBER
        )

    @staticmethod
    def symbol_tail() -> DfaTail:
        return AutoTail(
            [AutoTailState([], True, False)],
            TokenType.SYMBOL
        )

    @staticmethod
    def equals_tail() -> DfaTail:
        other = L + D + W + S + "*/" + EOT
        return AutoTail(
            [
                AutoTailState([
                    Transition("=", 1),
                    Transition(other, 2)
                ]),
                AutoTailState([], True, False),
                AutoTailState([], True, True)
            ],
            TokenType.SYMBOL
        )

    @staticmethod
    def asterisk_tail() -> DfaTail:
        return AsteriskTail()

    @staticmethod
    def comment_tail() -> DfaTail:
        return CommentTail()
