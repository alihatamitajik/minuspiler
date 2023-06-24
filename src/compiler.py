#  Ali Hatami (98101385) - Fatemeh Alimoradi (9909358)

import os

from scanner import Scanner
from cparser import Parser

if __name__ == "__main__":
    INPUT_FILENAME = os.path.join(os.path.dirname(__file__), 'input.txt')
    scanner = Scanner(file=INPUT_FILENAME)
    parser = Parser(scanner)
    parser.parse()
