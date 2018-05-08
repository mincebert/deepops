#!/usr/bin/env python3

# test_deepops.pytest_deepops.py - unittests for deepops

import unittest
import deepops


class TestDeepOps(unittest.TestCase):
    """Tests for `deepops.py`."""

    def setUp(self):
        # something complex to merge into
        self.x = {"a": "x",
                  "b": 2,
                  "c": ["x"],
                  "d": {"m": "x",
                        "n": 3,
                        "p": [1, 2],
                        "q": {"t": [1]}},
                  "e": {7, 8}}

        # something to complex to merge into above
        self.y = {"a": "y",
                  "b": 6,
                  "c": ["y", "x"],
                  "d": {"m": "y",
                        "o": 4,
                        "p": [2, 3],
                        "q": {"t": [2]}},
                  "e": {8, 9}}

        # something complex to remove
        self.z = {"a": {},
                  "b": {},
                  "c": {"x": {}},
                  "t": {"n": {}}}

    def test_deepops_merge(self):
        x_merge_y = {"a": "y",
                     "b": 6,
                     "c": ["x", "y"],
                     "d": {"m": "y",
                           "n": 3,
                           "p": [1, 2, 3],
                           "q": {"t": [1, 2]},
                           "o": 4},
                     "e": {8, 9, 7}}
        
        deepops.deepmerge(self.x, self.y, list_as_set=True)
        self.assertEqual(x_merge_y, self.x)

    def test_deepops_remove(self):
        x_remove_z = {"c": [],
                      "d": {"m": "x",
                            "n": 3,
                            "p": [1, 2],
                            "q": {"t": [1]}},
                      "e": {8, 7}}

        deepops.deepremoveitems(self.x, self.z)
        self.assertEqual(x_remove_z, self.x)
