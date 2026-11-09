import unittest
from receiver import aligned_check, load_cases, synthesize


class ReceiverTests(unittest.TestCase):
    def test_reproducible_samples(self):
        case = load_cases()[0]
        self.assertEqual(synthesize(case), synthesize(case))

    def test_aligned_discriminator_at_nominal_frequency(self):
        case = load_cases()[0]
        self.assertEqual(aligned_check(case), case['bits'])


if __name__ == '__main__':
    unittest.main()
