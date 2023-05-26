from util.dfa import *
from util.types_ import classproperty
from util.types_ import *
import json


class AsteriskTail(DfaTail):
    def match(self, buffer) -> Tuple[TokenType, bool]:
        buffer.step()
        c = buffer()
        if c == "/":
            raise ValueError(ErrorType.UNMATCHED_COMMENT)
        elif c not in SIGMA:
            raise ValueError(ErrorType.INVALID_INPUT)
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
        buffer.step()
        c = buffer()
        if c != "*":
            raise ValueError(ErrorType.BAD_SLASH)
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


# Following JSON is generated by firstFollow js module given in the
# assignment's document
GRAMMAR = json.loads(
    """
    {"Program":{
        "first":[null,"int","void"],
        "follow":["DOLOR"],
        "rules":[
            {"rule":["Declaration-list"],"prediction":["int","void","DOLOR"]}]},
    "Declaration-list":{
        "first":[null,"int","void"],
        "follow":["DOLOR","{","break",";","if","repeat","return","ID","(","NUM","}"],
        "rules":[
            {"rule":["Declaration","Declaration-list"],"prediction":["int","void"]},
            {"rule":[null],"prediction":["DOLOR","{","break",";","if","repeat","return","ID","(","NUM","}"]}]},
    "Declaration":{
        "first":["int","void"],
        "follow":["int","void","DOLOR","{","break",";","if","repeat","return","ID","(","NUM","}"],
        "rules":[
            {"rule":["Declaration-initial","Declaration-prime"],"prediction":["int","void"]}]},
    "Declaration-initial":{
        "first":["int","void"],
        "follow":["(",";","[",",",")"],
        "rules":[
            {"rule":["#ptype", "Type-specifier", "#pname", "ID"],"prediction":["int","void"]}]},
    "Declaration-prime":{
        "first":["(",";","["],
        "follow":["int","void","DOLOR","{","break",";","if","repeat","return","ID","(","NUM","}"],
        "rules":[
            {"rule":["Fun-declaration-prime"],"prediction":["("]},
            {"rule":["Var-declaration-prime"],"prediction":[";","["]}]},
    "Var-declaration-prime":{
        "first":[";","["],
        "follow":["int","void","DOLOR","{","break",";","if","repeat","return","ID","(","NUM","}"],
        "rules":[
            {"rule":[";", "#var"],"prediction":[";"]},
            {"rule":["[", "#pnum", "NUM","]",";", "#arr"],"prediction":["["]}]},
    "Fun-declaration-prime":{
        "first":["("],
        "follow":["int","void","DOLOR","{","break",";","if","repeat","return","ID","(","NUM","}"],
        "rules":[
            {"rule":["(","Params",")","Compound-stmt"],"prediction":["("]}]},
    "Type-specifier":{
        "first":["int","void"],
        "follow":["ID"],
        "rules":[
            {"rule":["int"],"prediction":["int"]},
            {"rule":["void"],"prediction":["void"]}]},
    "Params":{
        "first":["int","void"],
        "follow":[")"],
        "rules":[
            {"rule":["int","ID","Param-prime","Param-list"],"prediction":["int"]},
            {"rule":["void"],"prediction":["void"]}]},
    "Param-list":{
        "first":[",",null],
        "follow":[")"],
        "rules":[
            {"rule":[",","Param","Param-list"],"prediction":[","]},
            {"rule":[null],"prediction":[")"]}]},
    "Param":{
        "first":["int","void"],
        "follow":[",",")"],
        "rules":[
            {"rule":["Declaration-initial","Param-prime"],"prediction":["int","void"]}]},
    "Param-prime":{
        "first":["[",null],
        "follow":[",",")"],
        "rules":[
            {"rule":["[","]"],"prediction":["["]},
            {"rule":[null],"prediction":[",",")"]}]},
    "Compound-stmt":{
        "first":["{"],
        "follow":["int","void","DOLOR","{","break",";","if","repeat","return","ID","(","NUM","}","else","until"],
        "rules":[
            {"rule":["#scope_up" ,"{","Declaration-list","Statement-list", "#scope_down", "}"],"prediction":["{"]}]},
    "Statement-list":{
        "first":[null,"{","break",";","if","repeat","return","ID","(","NUM"],
        "follow":["}"],
        "rules":[
            {"rule":["Statement","Statement-list"],"prediction":["{","break",";","if","repeat","return","ID","(","NUM"]},
            {"rule":[null],"prediction":["}"]}]},
    "Statement":{
        "first":["{","break",";","if","repeat","return","ID","(","NUM"],
        "follow":["{","break",";","if","repeat","return","ID","(","NUM","}","else","until"],
        "rules":[
            {"rule":["Expression-stmt"],"prediction":["break",";","ID","(","NUM"]},
            {"rule":["Compound-stmt"],"prediction":["{"]},
            {"rule":["Selection-stmt"],"prediction":["if"]},
            {"rule":["Iteration-stmt"],"prediction":["repeat"]},
            {"rule":["Return-stmt"],"prediction":["return"]}]},
    "Expression-stmt":{
        "first":["break",";","ID","(","NUM"],
        "follow":["{","break",";","if","repeat","return","ID","(","NUM","}","else","until"],
        "rules":[
            {"rule":["Expression", "#pexpr",";"],"prediction":["ID","(","NUM"]},
            {"rule":["break",";"],"prediction":["break"]},
            {"rule":[";"],"prediction":[";"]}]},
    "Selection-stmt":{
        "first":["if"],
        "follow":["{","break",";","if","repeat","return","ID","(","NUM","}","else","until"],
        "rules":[
            {"rule":["if","(","Expression",")","Statement","else","Statement"],"prediction":["if"]}]},
    "Iteration-stmt":{
        "first":["repeat"],
        "follow":["{","break",";","if","repeat","return","ID","(","NUM","}","else","until"],
        "rules":[
            {"rule":["repeat","Statement","until","(","Expression",")"],"prediction":["repeat"]}]},
    "Return-stmt":{
        "first":["return"],
        "follow":["{","break",";","if","repeat","return","ID","(","NUM","}","else","until"],
        "rules":[
            {"rule":["return","Return-stmt-prime"],"prediction":["return"]}]},
    "Return-stmt-prime":{
        "first":[";","ID","(","NUM"],
        "follow":["{","break",";","if","repeat","return","ID","(","NUM","}","else","until"],
        "rules":[
            {"rule":[";"],"prediction":[";"]},
            {"rule":["Expression",";"],"prediction":["ID","(","NUM"]}]},
    "Expression":{
        "first":["ID","(","NUM"],
        "follow":[";",")","]",","],
        "rules":[
            {"rule":["Simple-expression-zegond"],"prediction":["(","NUM"]},
            {"rule":["#pid", "ID","B"],"prediction":["ID"]}]},
    "B":{
        "first":["=","[","(","*","+","-","<","==",null],
        "follow":[";",")","]",","],
        "rules":[
            {"rule":["=","Expression", "#assign"],"prediction":["="]},
            {"rule":["[","Expression","]","H"],"prediction":["["]},
            {"rule":["Simple-expression-prime"],"prediction":["(","*","+","-","<","==",";",")","]",","]}]},
    "H":{
        "first":["=","*",null,"+","-","<","=="],
        "follow":[";",")","]",","],
        "rules":[
            {"rule":["=","Expression"],"prediction":["="]},
            {"rule":["G","D","C"],"prediction":["*","+","-","<","==",";",")","]",","]}]},
    "Simple-expression-zegond":{
        "first":["(","NUM"],
        "follow":[";",")","]",","],
        "rules":[
            {"rule":["Additive-expression-zegond","C"],"prediction":["(","NUM"]}]},
    "Simple-expression-prime":{
        "first":["(","*","+","-","<","==",null],
        "follow":[";",")","]",","],
        "rules":[
            {"rule":["Additive-expression-prime","C"],"prediction":["(","*","+","-","<","==",";",")","]",","]}]},
    "C":{
        "first":[null,"<","=="],
        "follow":[";",")","]",","],
        "rules":[
            {"rule":["#pop", "Relop","Additive-expression", "#calc"],"prediction":["<","=="]},
            {"rule":[null],"prediction":[";",")","]",","]}]},
    "Relop":{
        "first":["<","=="],
        "follow":["(","ID","NUM"],
        "rules":[
            {"rule":["<"],"prediction":["<"]},
            {"rule":["=="],"prediction":["=="]}]},
    "Additive-expression":{
        "first":["(","ID","NUM"],
        "follow":[";",")","]",","],
        "rules":[
            {"rule":["Term","D"],"prediction":["(","ID","NUM"]}]},
    "Additive-expression-prime":{
        "first":["(","*","+","-",null],
        "follow":["<","==",";",")","]",","],
        "rules":[
            {"rule":["Term-prime","D"],"prediction":["(","*","+","-","<","==",";",")","]",","]}]},
    "Additive-expression-zegond":{
        "first":["(","NUM"],
        "follow":["<","==",";",")","]",","],
        "rules":[
            {"rule":["Term-zegond","D"],"prediction":["(","NUM"]}]},
    "D":{
        "first":[null,"+","-"],
        "follow":["<","==",";",")","]",","],
        "rules":[
            {"rule":["#pop", "Addop","Term","#calc","D"],"prediction":["+","-"]},
            {"rule":[null],"prediction":["<","==",";",")","]",","]}]},
    "Addop":{
        "first":["+","-"],
        "follow":["(","ID","NUM"],
        "rules":[
            {"rule":["+"],"prediction":["+"]},
            {"rule":["-"],"prediction":["-"]}]},
    "Term":{
        "first":["(","ID","NUM"],
        "follow":["+","-",";",")","<","==","]",","],
        "rules":[
            {"rule":["Factor","G"],"prediction":["(","ID","NUM"]}]},
    "Term-prime":{
        "first":["(","*",null],
        "follow":["+","-","<","==",";",")","]",","],
        "rules":[
            {"rule":["Factor-prime","G"],"prediction":["(","*","+","-","<","==",";",")","]",","]}]},
    "Term-zegond":{
        "first":["(","NUM"],
        "follow":["+","-","<","==",";",")","]",","],
        "rules":[
            {"rule":["Factor-zegond","G"],"prediction":["(","NUM"]}]},
    "G":{
        "first":["*",null],
        "follow":["+","-","<","==",";",")","]",","],
        "rules":[
            {"rule":["#pop", "*","Factor", "#calc", "G"],"prediction":["*"]},
            {"rule":[null],"prediction":["+","-","<","==",";",")","]",","]}]},
    "Factor":{
        "first":["(","ID","NUM"],
        "follow":["*","+","-",";",")","<","==","]",","],
        "rules":[
            {"rule":["(","Expression",")"],"prediction":["("]},
            {"rule":["#pid", "ID","Var-call-prime"],"prediction":["ID"]},
            {"rule":["#pnum", "NUM"],"prediction":["NUM"]}]},
    "Var-call-prime":{
        "first":["(","[",null],
        "follow":["*","+","-",";",")","<","==","]",","],
        "rules":[
            {"rule":["(","Args",")"],"prediction":["("]},
            {"rule":["Var-prime"],"prediction":["[","*","+","-",";",")","<","==","]",","]}]},
    "Var-prime":{
        "first":["[",null],
        "follow":["*","+","-",";",")","<","==","]",","],
        "rules":[
            {"rule":["[","Expression","]"],"prediction":["["]},
            {"rule":[null],"prediction":["*","+","-",";",")","<","==","]",","]}]},
    "Factor-prime":{
        "first":["(",null],
        "follow":["*","+","-","<","==",";",")","]",","],
        "rules":[
            {"rule":["(","Args",")"],"prediction":["("]},
            {"rule":[null],"prediction":["*","+","-","<","==",";",")","]",","]}]},
    "Factor-zegond":{
        "first":["(","NUM"],
        "follow":["*","+","-","<","==",";",")","]",","],
        "rules":[
            {"rule":["(","Expression",")"],"prediction":["("]},
            {"rule":["#pnum", "NUM"],"prediction":["NUM"]}]},
    "Args":{
        "first":[null,"ID","(","NUM"],
        "follow":[")"],
        "rules":[
            {"rule":["Arg-list"],"prediction":["ID","(","NUM"]},
            {"rule":[null],"prediction":[")"]}]},
    "Arg-list":{
        "first":["ID","(","NUM"],
        "follow":[")"],
        "rules":[
            {"rule":["Expression","Arg-list-prime"],"prediction":["ID","(","NUM"]}]},
    "Arg-list-prime":{
        "first":[",",null],
        "follow":[")"],
        "rules":[
            {"rule":[",","Expression","Arg-list-prime"],"prediction":[","]},
            {"rule":[null],"prediction":[")"]}]}}
    """
)
