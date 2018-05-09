#!/usr/bin/env python3

# test_deepops.py - unittests for deepops

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

        # a list to remove items from
        self.x_list = ["a", "b", "c", "d"]

        # a list to remove
        self.z_list = ["a", "b", "n"]

        # an dictionary to remove from a list
        self.z_dict_from_list = {"a": None, "b": None, "n": None}

        # something illegal to merge into
        self.illegal_x = {"a": "x",
                          "b": ["y", "z"],
                          "c": ["x"],
                          "d": {"m": "x",
                                "n": 3,
                                "p": [1, 2],
                                "q": {"t": [1]}},
                          "e": {7, 8}}

        # something to illegal to merge into x
        self.illegal_y = {"a": "y",
                          "b": ["y", "z"],
                          "c": ["y", "x"],
                          "d": {"m": "y",
                                "o": 4,
                                "p": [2, 3],
                                "q": {"t": [2]}},
                          "e": {8, 9}}

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

    def test_deepops_merge_no_replace(self):
        x_merge_y = {"a": "x",
                     "b": 2,
                     "c": ["x", "y"],
                     "d": {"m": "x",
                           "n": 3,
                           "p": [1, 2, 3],
                           "q": {"t": [1, 2]},
                           "o": 4},
                     "e": {8, 9, 7}}

        deepops.deepmerge(self.x, self.y, replace=False, list_as_set=True)
        self.assertEqual(x_merge_y, self.x)

    def test_deepops_merge_no_set(self):
        x_merge_y = {"a": "y",
                     "b": 6,
                     "c": ["x", "y", 'x'],
                     "d": {"m": "y",
                           "n": 3,
                           "p": [1, 2, 2, 3],
                           "q": {"t": [1, 2]},
                           "o": 4},
                     "e": {8, 9, 7}}

        deepops.deepmerge(self.x, self.y, list_as_set=False)
        self.assertEqual(x_merge_y, self.x)

    def test_deepops_illegal_merge_original(self):
        self.assertRaises(TypeError, deepops.deepmerge, self.illegal_x, self.y, list_as_set=True)

    def test_deepops_illegal_merge_from(self):
        self.assertRaises(TypeError, deepops.deepmerge, self.x, self.illegal_y, list_as_set=True)

    def test_deepops_remove(self):
        x_remove_z = {"c": [],
                      "d": {"m": "x",
                            "n": 3,
                            "p": [1, 2],
                            "q": {"t": [1]}},
                      "e": {8, 7}}

        deepops.deepremoveitems(self.x, self.z)
        self.assertEqual(x_remove_z, self.x)

    def test_deepops_remove_list(self):
        x_remove_z = ["c", "d"]
        deepops.deepremoveitems(self.x_list, self.z_list)
        self.assertEqual(x_remove_z, self.x_list)

    def test_deepops_illegal_remove(self):
        self.assertRaises(TypeError, deepops.deepremoveitems, "a", self.z)

    def test_deepops_illegal_remove_from(self):
        self.assertRaises(TypeError, deepops.deepremoveitems, self.x, "a")

    def test_deepops_illegal_remove_from_list(self):
        self.assertRaises(ValueError, deepops.deepremoveitems, self.x_list, self.z)

    def test_deepops_remove_empty_dict_from_list(self):
        x_remove_z = ["a", "b", "c", "d"]
        deepops.deepremoveitems(self.x_list, {})
        self.assertEqual(x_remove_z, self.x_list)

    def test_deepops_remove_dict_from_list(self):
        x_remove_z = ["c", "d"]
        deepops.deepremoveitems(self.x_list, self.z_dict_from_list)
        self.assertEqual(x_remove_z, self.x_list)

    def test_deepops_remove_list_from_dict(self):
        x_remove_z = {"c": ["x"],
                      "d": {"m": "x",
                            "n": 3,
                            "p": [1, 2],
                            "q": {"t": [1]}},
                      "e": {7, 8}}
        deepops.deepremoveitems(self.x, self.z_list)
        self.assertEqual(x_remove_z, self.x)
