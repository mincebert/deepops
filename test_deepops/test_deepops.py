# (deepops) test_deepops.test_deepops



import unittest

from deepops import (
    deepmerge, deepremoveitems, deepfilter, deepdiff, deepsetdefault, deepget)

from copy import deepcopy



class TestDeepOps(unittest.TestCase):
    """Tests for `deepops.py`."""


    def setUp(self):
        # something complex to merge into
        self.x = {
            "a": "x",
            "b": 2,
            "c": ["x"],
            "d": {
                "m": "x",
                "n": 3,
                "p": [1, 2],
                "q": {
                    "t": [1],
                },
            },
            "e": {7, 8},
        }

        # something to complex to merge into above
        self.y = {
            "a": "y",
            "b": 6,
            "c": ["y", "x"],
            "d": {
                "m": "y",
                "o": 4,
                "p": [2, 3],
                "q": {
                    "t": [2],
                },
            },
            "e": {8, 9},
        }

        # something complex to remove
        self.z = {
            "a": {},
            "b": {},
            "c": {
                "x": {},
            },
            "t": {
                "n": {},
            },
        }

        # a list to remove items from
        self.x_list = ["a", "b", "c", "d"]

        # a list to remove
        self.z_list = ["a", "b", "n"]

        # an dictionary to remove from a list
        self.z_dict_from_list = {"a": None, "b": None, "n": None}

        # something illegal to merge into
        self.illegal_x = {
            "a": "x",
            "b": ["y", "z"],
            "c": ["x"],
            "d": {
                "m": "x",
                "n": 3,
                "p": 7,
                "q": {
                    "t": [1],
                },
            },
            "e": { 7, 8 },
        }

        # something to illegal to merge into x
        self.illegal_y = {
            "a": "y",
            "b": ["y", "z"],
            "c": ["y", "x"],
            "d": {
                "m": "y",
                "o": 4,
                "p": [2, 3],
                "q": {
                    "t": [2],
                },
            },
            "e": {8, 9},
        }


    # deepmerge() tests


    def test_merge(self):
        x_merge_y = {
            "a": "y",
            "b": 6,
            "c": ["x", "y"],
            "d": {
                "m": "y",
                "n": 3,
                "p": [1, 2, 3],
                "q": {
                    "t": [1, 2]
                },
                "o": 4,
            },
            "e": {8, 9, 7},
        }

        deepmerge(self.x, self.y, list_as_set=True)
        self.assertEqual(x_merge_y, self.x)


    def test_merge_no_replace(self):
        x_merge_y = {
            "a": "x",
            "b": 2,
            "c": ["x", "y"],
            "d": {
                "m": "x",
                "n": 3,
                "p": [1, 2, 3],
                "q": {
                    "t": [1, 2],
                },
                "o": 4,
            },
            "e": {8, 9, 7},
        }

        deepmerge(self.x, self.y, replace=False, list_as_set=True)
        self.assertEqual(x_merge_y, self.x)


    def test_merge_no_set(self):
        x_merge_y = {
            "a": "y",
            "b": 6,
            "c": ["x", "y", 'x'],
            "d": {
                "m": "y",
                "n": 3,
                "p": [1, 2, 2, 3],
                "q": {
                    "t": [1, 2]
                },
                "o": 4,
            },
            "e": {8, 9, 7},
        }

        deepmerge(self.x, self.y, list_as_set=False)
        self.assertEqual(x_merge_y, self.x)


    def test_merge_illegal_original(self):
        with self.assertRaises(TypeError):
            deepmerge(self.illegal_x, self.y, list_as_set=True)


    def test_merge_illegal_from(self):
        with self.assertRaises(TypeError):
            deepmerge(self.x, self.illegal_y, list_as_set=True)


    def test_merge_illegal_compound_from_simple(self):
        with self.assertRaises(TypeError):
            deepmerge(self.x, {"d": {"p": 1}})


    def test_merge_compound_from_simple_filtered(self):
        x_merge_const_filtered = {
            "a": "x",
            "b": 2,
            "c": ["x", "y"],
            "d": {
                "m": "x",
                "n": 3,
                "p": [1, 2],
                "q": {
                    "t": [1],
                }
            },
            "e": {7, 8},
        }

        deepmerge(self.x, {"c":["y"], "d": {"p": 1}},
                  filter_func=lambda p, a, b: not p.startswith(["d", "p"]))
        self.assertEqual(x_merge_const_filtered, self.x)


    def test_merge_illegal_simple_from_compound(self):
        with self.assertRaises(TypeError):
            deepmerge({"a": [1]}, self.x)


    # deepremoveitems() tests


    def test_remove(self):
        x_remove_z = {
            "c": [],
            "d": {
                "m": "x",
                "n": 3,
                "p": [1, 2],
                "q": {
                    "t": [1],
                },
            },
            "e": {8, 7},
        }

        deepremoveitems(self.x, self.z)
        self.assertEqual(x_remove_z, self.x)


    def test_remove_list(self):
        x_remove_z = ["c", "d"]
        deepremoveitems(self.x_list, self.z_list)
        self.assertEqual(x_remove_z, self.x_list)


    def test_remove_illegal(self):
        with self.assertRaises(TypeError):
            deepremoveitems("a", self.z)


    def test_remove_illegal_from(self):
        with self.assertRaises(TypeError):
            deepremoveitems(self.x, "a")


    def test_remove_illegal_from_list(self):
        with self.assertRaises(ValueError):
            deepremoveitems(self.x_list, self.z)


    def test_remove_empty_dict_from_list(self):
        x_remove_z = ["a", "b", "c", "d"]
        deepremoveitems(self.x_list, {})
        self.assertEqual(x_remove_z, self.x_list)


    def test_remove_illegal_type_simple(self):
        with self.assertRaises(TypeError):
            deepremoveitems(self.x, {"a": 5})


    def test_remove_illegal_compound_from_simple(self):
        with self.assertRaises(TypeError):
            deepremoveitems(self.x, {"a": [1]})


    def test_remove_compound_from_simple_filtered(self):
        x_remove_const = {
            "b": 2,
            "c": ["x"],
            "d": {"m": "x",
                "n": 3,
                "p": [1, 2],
                "q": {
                    "t": [1],
                },
            },
            "e": {7, 8},
        }
        deepremoveitems(
            self.x, {"a": {}, "d": {"n": [1]}},
            filter_func=lambda p, a, b: not p.startswith(["d", "n"]))
        self.assertEqual(x_remove_const, self.x)


    def test_remove_illegal_simple_from_compound(self):
        with self.assertRaises(TypeError):
            deepremoveitems({"a": [1]}, self.x)


    def test_remove_dict_from_list(self):
        x_remove_z = ["c", "d"]
        deepremoveitems(self.x_list, self.z_dict_from_list)
        self.assertEqual(x_remove_z, self.x_list)


    def test_remove_list_from_dict(self):
        x_remove_z = {
            "c": ["x"],
            "d": {"m": "x",
                "n": 3,
                "p": [1, 2],
                "q": {
                    "t": [1],
                },
            },
            "e": {7, 8},
        }
        deepremoveitems(self.x, self.z_list)
        self.assertEqual(x_remove_z, self.x)


    # deepfilter() tests


    def test_filter_list(self):
        x_filter_z_list = {
            "a": "x",
            "b": 2
        }
        self.assertEqual(x_filter_z_list, deepfilter(self.x, self.z_list))


    def test_filter_complex(self):
        x_filter_z = {
            "a": "x",
            "b": 2,
            "c": ["x"],
        }
        self.assertEquals(x_filter_z, deepfilter(self.x, self.z))


    def test_filter_complex(self):
        x_filter = {
            "a": {},
            "d": {
                "n": {},
                "q": {
                    "s": {},
                    "t": {},
                },
            },
            "e": [8, 9],
        }

        x_filter_result = {
            "a": "x",
            "d": {
                "n": 3,
                "q": {
                    "t": [1],
                },
            },
            "e": {8},
        }

        self.assertEqual(x_filter_result, deepfilter(self.x, x_filter))


    def test_filter_illegal_dict_from_list(self):
        x_filter = {
            "d": {
                "p": {
                    1: ["list"]
                }
            }
        }

        with self.assertRaises(ValueError):
            deepfilter(self.x, x_filter)


    def test_filter_simple_from_dict(self):
        x_filter = {
            "d": {
                "q": {
                    "t": 5
                }
            }
        }

        with self.assertRaises(TypeError):
            deepfilter(self.x, x_filter)


    def test_filter_dict_from_simple(self):
        x_filter = {
            "d": {
                "m": {
                    "simple": []
                }
            }
        }

        with self.assertRaises(TypeError):
            deepfilter(self.x, x_filter)


    def test_filter_subclasses(self):
        """Tests subclasses of primary object types, to check they're
        being cloned correctly in the result.
        """

        class SubDict(dict):
            pass

        class SubList(list):
            pass

        class SubSet(list):
            pass

        sub_x = SubDict({
            "a": "x",
            "b": 2,
            "c": SubList(["x"]),
            "d": SubDict({
                "m": "x",
                "n": 3,
                "p": SubList([1, 2]),
                "q": SubDict({
                    "t": SubList([1]),
                }),
            }),
            "e": SubSet({7, 8}),
        })

        filter_x = SubDict({
            "a": None,
            "b": None,
            "c": SubList(["x"]),
            "d": SubDict({
                "m": None,
                "n": None,
                "p": None,
                "q": SubDict({
                    "t": None,
                }),
            }),
            "e": None,
        })

        filtered_x = deepfilter(sub_x, filter_x)

        self.assertIs(type(filtered_x), SubDict)
        self.assertIs(type(filtered_x["c"]), SubList)
        self.assertIs(type(filtered_x["d"]), SubDict)
        self.assertIs(type(filtered_x["d"]["q"]), SubDict)
        self.assertIs(type(filtered_x["d"]["q"]["t"]), SubList)
        self.assertIs(type(filtered_x["e"]), SubSet)


    # deepdiff() tests


    def test_diff_equal_list(self):
        list_ = [1, 2, { 11: "a", 12: "b" }]
        remove, update = deepdiff(list_, list_)
        self.assertEqual(list(), remove)
        self.assertEqual(list(), update)


    def test_diff_equal_set(self):
        set_ = { 1, 2, 3 }
        remove, update = deepdiff(set_, set_)
        self.assertEqual(set(), remove)
        self.assertEqual(set(), update)


    def test_diff_equal_dict(self):
        dict_ = { 1: "a", 2: [], 3: { 11, 12 } }
        remove, update = deepdiff(dict_, dict_)
        self.assertEqual(dict(), remove)
        self.assertEqual(dict(), update)


    def test_diff_equal_complex(self):
        remove, update = deepdiff(self.x, self.x)
        self.assertEqual(type(self.x)(), remove)
        self.assertEqual(type(self.x)(), update)


    def test_diff_complex(self):
        x_diff_y_remove = {
            "c": ['x'],
            "d": {
                "n": None,
                "p": [1, 2],
                "q": {
                    "t": [1],
                },
            },
            "e": {7},
        }

        x_diff_y_update = {
            "a": "y",
            "b": 6,
            "c": ["y", "x"],
            "d": {
                "m": "y",
                "o": 4,
                "p": [2, 3],
                "q": {
                    "t": [2],
                },
            },
            "e": {9},
        }

        diff_remove, diff_update = deepdiff(self.x, self.y)
        self.assertEqual(x_diff_y_remove, diff_remove)
        self.assertEqual(x_diff_y_update, diff_update)


    def test_diff_remove_update(self):
        diff_remove, diff_update = deepdiff(self.x, self.y)
        deepremoveitems(self.x, deepcopy(diff_remove))
        deepmerge(self.x, deepcopy(diff_update))
        self.assertEqual(self.x, self.y)


    def test_diff_illegal_type(self):
        with self.assertRaises(TypeError):
            deepdiff(self.x, {"a": 1})


    def test_diff_illegal_simple_to_compound(self):
        with self.assertRaises(TypeError):
            deepdiff(self.x, {"b": [1]})


    def test_diff_illegal_compound_to_simple(self):
        with self.assertRaises(TypeError):
            deepdiff({"b": [1]}, self.x)


    def test_diff_compound_to_simple_filtered(self):
        x_different = {
            "a": "y",
            "b": 2,
            "c": ["x"],
            "d": {
                "m": "x",
                "n": [3],
                "p": [2, 3],
                "q": {
                    "t": [1],
                },
            },
            "e": {8, 9},
        }

        x_diff_const_remove = {"d": {"p": [1, 2]}, "e": {7}}
        x_diff_const_update = {"a": "y", "d": {"p": [2, 3]}, "e": {9}}

        diff_remove, diff_update = deepdiff(
            self.x, x_different,
            filter_func=lambda p, a, b: not p.startswith(["d", "n"]))

        self.assertEqual(x_diff_const_remove, diff_remove)
        self.assertEqual(x_diff_const_update, diff_update)


    def test_diff_illegal_list_to_set(self):
        with self.assertRaises(TypeError):
            deepdiff(self.x, {"c": {1}})


    def test_diff_subclasses(self):
        """Tests subclasses of primary object types, to check they're
        being cloned correctly in the result.
        """

        class SubDict(dict):
            pass

        class SubList(list):
            pass

        class SubSet(list):
            pass

        sub_a = SubDict({
            "a": SubList(["x", "y", "z"]),
            "b": SubSet({1, 2, 3}),
            "d": SubDict({
                "m": "x",
                "n": 3,
                "p": SubList([1, 2]),
                "q": SubDict({
                    "t": SubList([1]),
                }),
            }),
        })

        sub_b = SubDict({
            "a": ["y"],
            "b": SubSet({2, 4}),
            "d": SubDict({
                "b": None,
            }),
            "e": None,
            "l": SubList(["x"]),
            "s": SubSet({1}),
            "t": SubDict({ 1: 2, 3: 4 }),
        })

        sub_remove, sub_update = deepdiff(sub_a, sub_b, list_as_set=True)

        self.assertIs(type(sub_remove), SubDict)
        self.assertIs(type(sub_update), SubDict)

        self.assertIs(type(sub_remove["b"]), SubSet)
        self.assertIs(type(sub_update["l"]), SubList)
        self.assertIs(type(sub_update["s"]), SubSet)
        self.assertIs(type(sub_update["t"]), SubDict)


    # deepsetdefault() tests


    def test_setdefault_empty(self):
        x = {}

        x_default = { 1: { 2: {} } }
        y_default = {}

        y = deepsetdefault(x, 1, 2)

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)


    def test_setdefault_distinct(self):
        x = { 1: { 2: {} } }

        x_default = { 1: { 2: {} }, 3: { 4: {} } }
        y_default = {}

        y = deepsetdefault(x, 3, 4)

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)


    def test_setdefault_existing(self):
        x = { 1: { 2: { 3: {} } } }

        x_default = { 1: { 2: { 3: {} } } }
        y_default = { 2: { 3: {} } }

        y = deepsetdefault(x, 1)

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)


    def test_setdefault_last(self):
        x = { 1: { 2: {} } }

        x_default = { 1: { 2: { 3: [] } } }
        y_default = []

        y = deepsetdefault(x, 1, 2, 3, last=[])

        self.assertEqual(x, x_default)
        self.assertEqual(y, y_default)


    def test_setdefault_subclass(self):
        class SubDict(dict):
            pass

        d = {}
        deepsetdefault(d, 1, 2, last=SubDict())
        self.assertIs(type(d[1][2]), SubDict)


    # deepget() tests


    def test_get_simple(self):
        x = { 1: { 2: { 3: {} } } }
        x_get = x[1][2]
        self.assertEqual(deepget(x, 1, 2), x_get)


    def test_get_none(self):
        x = { 1: { 2: { 3: {} } } }
        y = deepget(x, 1, 3)
        self.assertEqual(y, None)


    def test_get_default_keyerror(self):
        x = { 1: { 2: { 3: {} } } }
        self.assertEqual(deepget(x, 1, 3, default=4), 4)


    def test_get_default_typeerror(self):
        x = { 1: { 2: "string" } }
        self.assertEqual(deepget(x, 1, 2, 3, default=4), 4)


    def test_get_defaulterror_found(self):
        x = { 1: { 2: { 3: {} } } }
        x_get = { 3: {} }
        self.assertEqual(deepget(x, 1, 2, default_error=True), x_get)


    def test_get_defaulterror_keyerror(self):
        x = { 1: { 2: { 3: {} } } }
        with self.assertRaises(KeyError):
            deepget(x, 1, 3, default_error=True)


    def test_get_defaulterror_typeerror(self):
        x = { 1: { 2: "string" } }
        with self.assertRaises(TypeError):
            deepget(x, 1, 2, 3, default_error=True)


if __name__ == '__main__':
    unittest.main()
