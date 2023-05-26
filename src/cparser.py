from util.cminus import GRAMMAR
from scanner import Scanner
from anytree import Node, RenderTree
from util.types_ import TokenType
from codegen import CodeGenerator


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

    def __init__(self, scanner: Scanner, err=None, tree=None, output=None, semantic_err=None) -> None:
        self.scanner = scanner
        self.grammar = {key: Transition(val) for key, val in GRAMMAR.items()}
        self.unexpected_eof = False
        self.syn_err = err if err else open('syntax_errors.txt', 'w')
        self.tree = tree if tree else open('parse_tree.txt', 'w', -1, "utf-8")
        self.semantic_err = semantic_err if semantic_err else open(
            "semantic_errors.txt", "w")
        self.output = output if output else open("output.txt", "w")
        self.cg = CodeGenerator()

    def step_lookahead(self):
        """Updates the lookahead

        Reads next token from the scanner and updates the lookahead token with
        the token itself and extracts the terminal string from it so it can be
        matched in with the rules in the grammar.
        """
        lookahead = self.scanner.get_next_token()
        self.lookahead = lookahead
        tt, lexim, self.lineno = lookahead
        if tt == TokenType.SYMBOL or tt == TokenType.KEYWORD:
            self.terminal = lexim
        else:
            self.terminal = str(tt)

    def match(self, parent_node):
        """Accepts a terminal

        Accepts a terminal, add it to the parse tree and get the next token as
        the lookahead.
        """
        tt, lexim, _ = self.lookahead
        Node(f"({str(tt)}, {lexim})", parent_node)
        self.step_lookahead()

    def match_epsilon(self, parent_node):
        """Matches an epsilon rule

        Adds a epsilon in the tree without moving lookahead"""
        Node('epsilon', parent_node)

    def log_syntax_error(self, msg):
        self.syn_err.write(f"#{self.lineno} : syntax error, {msg}\n")

    def transit(self, diagram='Program', parent_node=None):
        """Executes the transition of `diagram`

        This function tries to match current lookahead token with current
        diagram."""
        trans = self.grammar[diagram]
        rule = trans.get_rule(self.terminal)
        # no rule can be found (i.e. not in first set or follow)
        while not rule:
            # PANIC!
            if self.terminal in trans.follow:
                self.log_syntax_error(f"missing " + diagram)
                return
            else:
                if self.terminal == 'DOLOR':
                    self.log_syntax_error("Unexpected EOF")
                    raise EOFError()
                else:
                    self.log_syntax_error("illegal " + self.terminal)
                    self.step_lookahead()
            rule = trans.get_rule(self.terminal)
        node = Node(diagram, parent_node)

        if None in rule.rule:  # epsilon move
            self.match_epsilon(node)
            # do actions
            for edge in rule.rule:
                if edge:
                    self.cg.code_gen(edge, self.lookahead)
        else:
            for i, edge in enumerate(rule.rule):
                if edge[0] == '#':  # if we have action
                    self.cg.code_gen(edge, self.lookahead)
                elif edge in self.grammar:  # if edge is a production rule
                    self.transit(edge, node)
                else:  # if edge is a terminal
                    if self.terminal == edge:
                        self.match(node)
                    else:  # if does not match missing something
                        self.log_syntax_error(f"missing " + edge)

    def transit_program(self):
        """Program is constructed with "Program $"

        This rule is not in the set of rules but we can simulate this rule by
        adding a $ matching at the end of the transit"""
        root = Node('root')
        # try:
        self.transit(parent_node=root)
        Node('$', root.children[0])
        # except:
        #     pass
        return root.children[0]

    def parse(self):
        """Generates Parse Tree and Syntax Errors"""
        self.step_lookahead()
        tree = self.transit_program()
        lines = [f"{pre}{node.name}" for pre, _, node in RenderTree(tree)]
        self.tree.write("\n".join(lines))
        if not self.syn_err.tell():
            self.syn_err.write('There is no syntax error.')
        self.cg.generate_output(self.output)
        self.cg.generate_errors(self.semantic_err)
        return tree
