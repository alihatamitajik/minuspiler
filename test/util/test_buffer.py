import unittest
import os

from util.buffer import AllBuffer

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'input.txt')


class AllBufferTest(unittest.TestCase):
    def setUp(self) -> None:
        self.buf = AllBuffer(TESTDATA_FILENAME)

    def tearDown(self) -> None:
        self.buf.close()

    def test_init(self):
        self.assertEqual(self.buf.forward, 0)
        self.assertEqual(self.buf.beginning, 0)
        self.assertTrue(self.buf.file.startswith("void main (void) {"))

    def test_call(self):
        self.assertEqual(self.buf(), "v")

    def test_step(self):
        self.buf.step()
        self.buf.step()
        self.assertEqual(self.buf(), "i")

    def test_extract(self):
        for _ in range(3):
            self.buf.step()
        self.assertEqual(self.buf.extract(), "void")
        self.assertEqual(self.buf.forward, 4)
        self.assertEqual(self.buf.beginning, 4)
        self.assertEqual(self.buf(), " ")

    def test_extract_retreat(self):
        pass

    def test_none_when_end(self):
        pass

    def test_line_no(self):
        pass
