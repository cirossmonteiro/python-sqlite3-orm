import random
import unittest

import utils

class TestUtils(unittest.TestCase):
    def test_compute_transpositions(self):
        start, end = random.sample(range(10), 10), random.sample(range(10), 10)
        random.shuffle(end)
        transpositions = utils.compute_transpositions(start, end)
        self.assertEqual(utils.apply_transpositions(start, transpositions), end)


if __name__ == '__main__':
    unittest.main()