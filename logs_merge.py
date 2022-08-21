#!/usr/bin/env python3

import unittest
import re
from datetime import datetime


def merge(*iterables, key=lambda x: x):
    iterators = []
    for iterator in iterables:
        iterators.extend(iterator)
    result = sorted(iterators, key=key)
    return iter(result)


def log_key(s):
    lines = re.findall(r'\[(.+?) \+0600\]', s)
    if len(lines) == 0:
        raise ValueError(f'"{s[:5]}..." Key not contained')
    result = datetime.strptime(lines[0], '%d/%b/%Y:%H:%M:%S')
    return result


class TestTest(unittest.TestCase):
    def test_null_iter(self):
        a = []
        b = []
        result = list(merge(a, b))
        self.assertEqual([], result)

    def test_simple_one(self):
        a = [2]
        b = [1]
        result = list(merge(a, b))
        self.assertEqual([1, 2], result)

    def test_simple_two(self):
        a = [8]
        b = [8]
        result = list(merge(a, b))
        self.assertEqual([8, 8], result)

    def test_little_hard(self):
        a = [1, 3, 4, 6, 7, 9]
        b = [2, 3, 5, 6, 9, 10]
        result = list(merge(a, b))
        self.assertEqual([1, 2, 3, 3, 4, 5, 6, 6, 7, 9, 9, 10], result)

    def test_log_key(self):
        result = log_key("194.226.228.1 - - [11/Sep/2001:08:46:01 +0600]")
        expected_result = datetime.strptime("11/Sep/2001:08:46:01",
                                            '%d/%b/%Y:%H:%M:%S')
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
