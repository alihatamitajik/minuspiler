import unittest
from pathlib import Path
from io import StringIO

from scanner import Scanner

NO_PA1_TEST_CASE = 10


class TestCases(unittest.TestCase):

    def test_pa1_test_cases(self):
        """Test all PA1 test cases

        This function will open a stringIO object and pass it to log method
        in the scanner and the output will be compared.
        """
        test_path = Path(__file__).parent.joinpath('./PA1_testcases')
        for i, test in enumerate(test_path.iterdir()):
            with self.subTest(testcase=i):
                # create scanner
                self.maxDiff = None
                scanner = Scanner(file=str(test.joinpath('input.txt')))
                scanner.iterate_ignore()
                # create outputs
                sym, tok, err = [StringIO() for i in range(3)]
                scanner.dump_log(file_tokens=tok, file_errors=err,
                                 file_symbols=sym)
                outputs = [(tok, 'tokens.txt'), (sym, 'symbol_table.txt'),
                           (err, 'lexical_errors.txt')]
                for created, output in outputs:
                    created.seek(0)
                    file = open(test.joinpath(output))
                    self.assertEqual(created.read(), file.read())
                    file.close()
                    created.close()
                scanner.buf.close()
