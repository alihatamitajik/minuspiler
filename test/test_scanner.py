import unittest

from util.buffer import AllBuffer
from scanner import Scanner
from util.types_ import TokenType, ErrorType


class GetTokenTest(unittest.TestCase):
    def test_simple_tokens(self):
        buf = AllBuffer(fake="int a=22;")
        scanner = Scanner(buffer=buf)
        expected = [
            (TokenType.KEYWORD, "int"), (TokenType.WHITESPACE, " "),
            (TokenType.ID, "a"), (TokenType.SYMBOL, "="), (TokenType.NUM, "22"),
            (TokenType.SYMBOL, ";"), (TokenType.DOLOR, "")]
        for expected_type, expected_lexim in expected:
            tt, lexim = scanner.get_token()
            self.assertEqual(expected_type, tt)
            self.assertEqual(expected_lexim, lexim)

    def test_panic(self):
        buf = AllBuffer(fake="\t\tcd!e=7;\n\t}")
        scanner = Scanner(buffer=buf)
        expected = [
            (TokenType.WHITESPACE, '\t'), (TokenType.WHITESPACE, '\t'),
            (ErrorType.INVALID_INPUT, 'cd!'), (TokenType.ID, "e"),
            (TokenType.SYMBOL, '='), (TokenType.NUM, '7'),
            (TokenType.SYMBOL, ';'), (TokenType.WHITESPACE, '\n'),
            (TokenType.WHITESPACE, '\t'), (TokenType.SYMBOL, '}'),
            (TokenType.DOLOR, '')]
        for expected_type, expected_lexim in expected:
            tt, lexim = scanner.get_token()
            self.assertEqual(expected_type, tt)
            self.assertEqual(expected_lexim, lexim)
