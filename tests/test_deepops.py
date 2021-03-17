#!/usr/bin/env python3


# test_deepops.py - unittests for deepops


import unittest

from deepops import (
    deepmerge, deepremoveitems, deepdiff, deepsetdefault, deepget)

from copy import deepcopy


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
                                "p": 7,
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


    # deepmerge() tests

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

        deepmerge(self.x, self.y, list_as_set=True)
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

        deepmerge(self.x, self.y, replace=False, list_as_set=True)
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

        deepmerge(self.x, self.y, list_as_set=False)
        self.assertEqual(x_merge_y, self.x)

    def test_deepops_merge_illegal_original(self):
        self.assertRaises(
            TypeError, deepmerge, self.illegal_x, self.y, list_as_set=True)

    def test_deepops_merge_illegal_from(self):
        self.assertRaises(
            TypeError, deepmerge, self.x, self.illegal_y, list_as_set=True)

    def test_deepops_merge_illegal_compound_from_simple(self):
        self.assertRaises(TypeError, deepmerge, self.x, {"d": {"p": 1}})

    def test_deepops_merge_compound_from_simple_filtered(self):
        x_merge_const_filtered = {
            "a": "x",
            "b": 2,
            "c": ["x", "y"],
            "d": {"m": "x",
                "n": 3,
                "p": [1, 2],
                "q": {"t": [1]}},
            "e": {7, 8}}

        deepmerge(self.x, {"c":["y"], "d": {"p": 1}},
                  filter_func=lambda p, a, b: not p.startswith(["d", "p"]))
        self.assertEqual(x_merge_const_filtered, self.x)

    def test_deepops_merge_illegal_simple_from_compound(self):
        self.assertRaises(TypeError, deepmerge, {"a": [1]}, self.x)


    # deepremoveitems() tests

    def test_deepops_remove(self):
        x_remove_z = {"c": [],
                      "d": {"m": "x",
                            "n": 3,
                            "p": [1, 2],
                            "q": {"t": [1]}},
                      "e": {8, 7}}

        deepremoveitems(self.x, self.z)
        self.assertEqual(x_remove_z, self.x)

    def test_deepops_remove_list(self):
        x_remove_z = ["c", "d"]
        deepremoveitems(self.x_list, self.z_list)
        self.assertEqual(x_remove_z, self.x_list)

    def test_deepops_remove_illegal(self):
        self.assertRaises(TypeError, deepremoveitems, "a", self.z)

    def test_deepops_remove_illegal_from(self):
        self.assertRaises(TypeError, deepremoveitems, self.x, "a")

    def test_deepops_remove_illegal_from_list(self):
        self.assertRaises(ValueError, deepremoveitems, self.x_list, self.z)

    def test_deepops_remove_empty_dict_from_list(self):
        x_remove_z = ["a", "b", "c", "d"]
        deepremoveitems(self.x_list, {})
        self.assertEqual(x_remove_z, self.x_list)

    def test_deepops_remove_illegal_type_simple(self):
        self.assertRaises(TypeError, deepremoveitems, self.x, {"a": 5})

    def test_deepops_remove_illegal_compound_from_simple(self):
        self.assertRaises(TypeError, deepremoveitems, self.x, {"a": [1]})

    def test_deepops_remove_compound_from_simple_filtered(self):
        x_remove_const = {
            "b": 2,
            "c": ["x"],
            "d": {"m": "x",
                "n": 3,
                "p": [1, 2],
                "q": {"t": [1]}},
            "e": {7, 8}
        }

        deepremoveitems(
            self.x, {"a": {}, "d": {"n": [1]}},
            filter_func=lambda p, a, b: not p.startswith(["d", "n"]))
        self.assertEqual(x_remove_const, self.x)

    def test_deepops_remove_illegal_simple_from_compound(self):
        self.assertRaises(TypeError, deepremoveitems, {"a": [1]}, self.x)

    def test_deepops_remove_dict_from_list(self):
        x_remove_z = ["c", "d"]
        deepremoveitems(self.x_list, self.z_dict_from_list)
        self.assertEqual(x_remove_z, self.x_list)

    def test_deepops_remove_list_from_dict(self):
        x_remove_z = {"c": ["x"],
                      "d": {"m": "x",
                            "n": 3,
                            "p": [1, 2],
                            "q": {"t": [1]}},
                      "e": {7, 8}}
        deepremoveitems(self.x, self.z_list)
        self.assertEqual(x_remove_z, self.x)


    # deepdiff() tests

    def test_deepops_diff_complex(self):
        x_diff_y_remove = {"c": ['x'],
                           "d": {"n": None,
                                 "p": [1, 2],
                                 "q": {"t": [1]}},
                           "e": {7}}

        x_diff_y_update = {"a": "y",
                           "b": 6,
                           "c": ["y", "x"],
                           "d": {"m": "y",
                                 "o": 4,
                                 "p": [2, 3],
                                 "q": {"t": [2]}},
                           "e": {9}}

        diff_remove, diff_update = deepdiff(self.x, self.y)
        self.assertEqual(x_diff_y_remove, diff_remove)
        self.assertEqual(x_diff_y_update, diff_update)

    def test_deepops_diff_remove_update(self):
        diff_remove, diff_update = deepdiff(self.x, self.y)
        deepremoveitems(self.x, deepcopy(diff_remove))
        deepmerge(self.x, deepcopy(diff_update))
        self.assertEqual(self.x, self.y)

    def test_deepops_diff_illegal_type(self):
        self.assertRaises(TypeError, deepdiff, self.x, {"a": 1})

    def test_deepops_diff_illegal_simple_to_compound(self):
        self.assertRaises(TypeError, deepdiff, self.x, {"b": [1]})

    def test_deepops_diff_illegal_compound_to_simple(self):
        self.assertRaises(TypeError, deepdiff, {"b": [1]}, self.x)

    def test_deepops_diff_compound_to_simple_filtered(self):
        x_different = {
                    "a": "y",
                    "b": 2,
                    "c": ["x"],
                    "d": {"m": "x",
                          "n": [3],
                          "p": [2, 3],
                          "q": {"t": [1]}},
                    "e": {8, 9}}

        x_diff_const_remove = {"d": {"p": [1, 2]}, "e": {7}}
        x_diff_const_update = {"a": "y", "d": {"p": [2, 3]}, "e": {9}}

        diff_remove, diff_update = deepdiff(
            self.x, x_different,
            filter_func=lambda p, a, b: not p.startswith(["d", "n"]))

        self.assertEqual(x_diff_const_remove, diff_remove)
        self.assertEqual(x_diff_const_update, diff_update)

    def test_deepops_diff_illegal_list_to_set(self):
        self.assertRaises(TypeError, deepdiff, self.x, {"c": {1}})


    # deepsetdefault() tests

    def test_deepsetdefault_empty(self):
        x = {}

        x_default = { 1: { 2: {} } }
        y_default = {}

        y = deepsetdefault(x, 1, 2)

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)

    def test_deepsetdefault_distinct(self):
        x = { 1: { 2: {} } }

        x_default = { 1: { 2: {} }, 3: { 4: {} } }
        y_default = {}

        y = deepsetdefault(x, 3, 4)

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)

    def test_deepsetdefault_existing(self):
        x = { 1: { 2: { 3: {} } } }

        x_default = { 1: { 2: { 3: {} } } }
        y_default = { 2: { 3: {} } }

        y = deepsetdefault(x, 1)

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)

    def test_deepsetdefault_last(self):
        x = { 1: { 2: {} } }

        x_default = { 1: { 2: { 3: [] } } }
        y_default = []

        y = deepsetdefault(x, 1, 2, 3, last=[])

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)


    # deepget() tests

    def test_deepget_simple(self):
        x = { 1: { 2: { 3: {} } } }

        x_get = x[1][2]

        y = deepget(x, 1, 2)

        self.assertEqual(y, x_get)

    def test_deepget_none(self):
        x = { 1: { 2: { 3: {} } } }

        y = deepget(x, 1, 3)

        self.assertEquals(y, None)

    def test_deepget_default(self):
        x = { 1: { 2: { 3: {} } } }

        y = deepget(x, 1, 3, default=4)

        self.assertEquals(y, 4)


if __name__ == '__main__':
    unittest.main()
