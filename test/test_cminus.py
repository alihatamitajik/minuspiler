import unittest

from util.buffer import AllBuffer
from util.cminus import CMinus
from util.types_ import TokenType


class CMinusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dfa = CMinus.get_language()

    def test_correct_whitespace(self):
        buf = AllBuffer(fake=" ")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.WHITESPACE)
        self.assertFalse(r)
        # buffer should return the whitespace because it should not proceed if
        # it was not retreat so in extract method proceeding is happening.
        self.assertEqual(buf(), ' ')

    def test_correct_num(self):
        buf = AllBuffer(fake="12345 ")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.NUM)
        self.assertTrue(r)
        self.assertEqual(buf(), ' ')

    def test_corrupted_num(self):
        buf = AllBuffer(fake="1234x5")
        self.assertRaises(ValueError, self.dfa, buf)
        self.assertEqual(buf.forward, 4)

    def test_id_key(self):
        buf = AllBuffer(fake="mean = 1;")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.ID)
        self.assertTrue(r)
        self.assertEqual(buf.forward, 4)

    def test_id_key_char_ending(self):
        buf = AllBuffer(fake="mean2/ 1;")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.ID)
        self.assertTrue(r)
        self.assertEqual(buf.forward, 5)

    def test_id_key_eof(self):
        buf = AllBuffer(fake="mean")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.ID)
        self.assertTrue(r)
        self.assertEqual(buf(), '\x05')

    def test_id_key_corrupt(self):
        buf = AllBuffer(fake="mean% = 1;")
        self.assertRaises(ValueError, self.dfa, buf)
        self.assertEqual(buf.forward, 4)

    def test_symbol_normal(self):
        buf = AllBuffer(fake=";,(")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.SYMBOL)
        self.assertFalse(r)
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.SYMBOL)
        self.assertFalse(r)
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.SYMBOL)
        self.assertFalse(r)

    def test_symbol_asterisk(self):
        buf = AllBuffer(fake="*a")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.SYMBOL)
        self.assertTrue(r)

    def test_symbol_asterisk_eof(self):
        buf = AllBuffer(fake="*")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.SYMBOL)
        self.assertTrue(r)

    def test_unmatched_comment(self):
        buf = AllBuffer(fake="*/")
        self.assertRaises(ValueError, self.dfa, buf)
        self.assertEqual(buf.forward, 1)

    def test_symbol_assign(self):
        buf = AllBuffer(fake="=2")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.SYMBOL)
        self.assertTrue(r)

    def test_symbol_equals(self):
        buf = AllBuffer(fake="==3")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.SYMBOL)
        self.assertFalse(r)
        self.assertEqual(buf.forward, 1)

    def test_comment(self):
        buf = AllBuffer(fake="/*** com*men/t *** **/")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.COMMENT)
        self.assertFalse(r)

    def test_empty_comment(self):
        buf = AllBuffer(fake="/**/")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.COMMENT)
        self.assertFalse(r)

    def test_multiline_comment(self):
        buf = AllBuffer(fake="/*** com*m\nen/t *\n** *\n*/")
        t, r = self.dfa(buf)
        self.assertEqual(t, TokenType.COMMENT)
        self.assertFalse(r)

    def test_unclosed_comment(self):
        buf = AllBuffer(fake="/*** com*m\nen/t *\n** *\n*")
        self.assertRaises(ValueError, self.dfa, buf)
        self.assertEqual(buf(), '\x05')
