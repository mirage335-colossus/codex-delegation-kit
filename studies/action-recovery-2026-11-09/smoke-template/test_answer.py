import unittest

import answer


class AnswerTest(unittest.TestCase):
    def test_answer_is_42(self):
        self.assertEqual(answer.answer(), 42)


if __name__ == "__main__":
    unittest.main()
