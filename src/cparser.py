from util.cminus import GRAMMAR
from scanner import Scanner
from anytree import Node, RenderTree
from util.types_ import TokenType


class Rule:
    def __init__(self, rule, prediction) -> None:
        self.rule = rule
        self.prediction = prediction


class Transition:
    def __init__(self, diagram) -> None:
        self.first = diagram['first']
        self.follow = diagram['follow']
        self.rules = [Rule(rule['rule'], rule['prediction'])
                      for rule in diagram['rules']]

    def get_rule(self, terminal):
        for rule in self.rules:
            if terminal in rule.prediction:
                return rule
        return None


class Parser:
    """Parser of CMinus

    This parser is using Transition Diagram Model.
    """

    def __init__(self, scanner: Scanner) -> None:
        """
        TODO: add logger to the parser
        """
        self.scanner = scanner
        self.grammar = {key: Transition(val) for key, val in GRAMMAR.items()}
        self.unexpected_eof = False

    def step_lookahead(self):
        """Updates the lookahead

        Reads next token from the scanner and updates the lookahead token with
        the token itself and extracts the terminal string from it so it can be
        matched in with the rules in the grammar.
        """
        lookahead = self.scanner.get_next_token()
        self.lookahead = lookahead
        tt, lexim = lookahead
        if tt == TokenType.SYMBOL or tt == TokenType.KEYWORD:
            self.terminal = lexim
        else:
            self.terminal = str(tt)

    def match(self, parent_node):
        """Accepts a terminal

        Accepts a terminal, add it to the parse tree and get the next token as
        the lookahead.
        """
        tt, lexim = self.lookahead
        Node(f"({str(tt)}, {lexim})", parent_node)
        self.step_lookahead()

    def match_epsilon(self, parent_node):
        """Matches an epsilon rule

        Adds a epsilon in the tree without moving lookahead"""
        Node('epsilon', parent_node)

    def transit(self, diagram='Program', parent_node=None):
        """Executes the transition of `diagram`

        This function tries to match current lookahead token with current
        diagram."""
        node = Node(diagram, parent_node)
        trans = self.grammar[diagram]
        rule = trans.get_rule(self.terminal)
        if not rule:  # no rule can be found
            pass
        elif not rule.rule[0]:  # epsilon move
            self.match_epsilon(node)
        else:
            for i, edge in enumerate(rule.rule):
                if edge in self.grammar:  # if edge is a production rule
                    self.transit(edge, node)
                else:  # if edge is a terminal
                    if self.terminal == edge:
                        self.match(node)
                    else:  # if does not match missing something
                        pass
        return node

    def transit_program(self):
        """Program is constructed with "Program $"

        This rule is not in the set of rules but we can simulate this rule by
        adding a $ matching at the end of the transit"""
        program = self.transit()
        if not self.unexpected_eof:
            Node('$', program)
        return program

    def parse(self):
        """Generates Parse Tree and Syntax Errors"""
        self.step_lookahead()
        tree = self.transit_program()
        for pre, fill, node in RenderTree(tree):
            print("%s%s" % (pre, node.name.strip()))
        return tree
