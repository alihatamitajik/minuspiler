from util.dfa import *
from util.types_ import classproperty
from util.types_ import *


class CMinus:
    """Language

    A wrapper over language methods to get DFA of the language in a cleaner way.
    """
    @staticmethod
    def get_language() -> Dfa:
        return Dfa(
            [
                (W, CMinus.whitespace_tail),
                (L, CMinus.id_keyword_tail),
                (D, CMinus.num_tail)
                (S, CMinus.symbol_tail),
                ("=", CMinus.equals_tail),
                ("*", CMinus.asterisk_tail),
                ("/", CMinus.comment_tail)
            ]
        )

    @classproperty
    def whitespace_tail() -> DfaTail:
        return AutoTail(
            [AutoTailState([], True, False)],
            TokenType.WHITESPACE
        )

    @classproperty
    def id_keyword_tail() -> DfaTail:
        """ID/Keyword Tail

        NOTE: Get_Token and Install_Id should be called in the scanner itself
        """
        return AutoTail(
            [
                AutoTailState(
                    [
                        Transition(L+D, next_state=0),
                        Transition(L+D, is_other=True, next_state=1)
                    ]
                ),
                AutoTailState([], True, True)
            ],
            TokenType.ID
        )

    @classproperty
    def num_tail() -> DfaTail:
        pass

    @classproperty
    def symbol_tail() -> DfaTail:
        pass

    @classproperty
    def equals_tail():
        pass

    @classproperty
    def asterisk_tail():
        pass

    @classproperty
    def comment_tail():
        pass
