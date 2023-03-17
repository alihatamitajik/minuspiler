import os

from util.types_ import TokenType
from scanner import Scanner
from util.logger import Logger

if __name__ == "__main__":
    INPUT_FILENAME = os.path.join(os.path.dirname(__file__), 'input.txt')
    scanner = Scanner(file=INPUT_FILENAME)
    scanner.iterate_ignore()
    scanner.finish()
