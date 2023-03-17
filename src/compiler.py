import os

from util.types_ import TokenType
from scanner import Scanner


if __name__ == "__main__":
    INPUT_FILENAME = os.path.join(os.path.dirname(__file__), 'input.txt')
    scanner = Scanner(file=INPUT_FILENAME)
    tt = TokenType.WHITESPACE
    while tt != TokenType.DOLOR:
        tt, lexim = scanner.get_next_token()
